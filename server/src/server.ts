import http, {IncomingMessage,ServerResponse} from 'node:http';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {SnapshotStore,StoreError,type Update} from './snapshot_store.js';
const VERSION='2.0.0', MAX_BODY=1048576, ID=/^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$/;
class HttpError extends Error { constructor(public status:number, public code:string) {super(code);} }
function validate(x:unknown):Update {
  if (!x || typeof x!=='object' || Array.isArray(x)) throw new HttpError(400,'INVALID_ARGUMENT');
  const v=x as Record<string,unknown>, keys=['update_id','run_id','mode','device_alias','title','body'];
  if (Object.keys(v).length!==keys.length || !keys.every(k=>Object.hasOwn(v,k)) || !['update_id','run_id','device_alias'].every(k=>typeof v[k]==='string' && ID.test(v[k] as string)) || !['PERIODIC','PUSH','HYBRID'].includes(v.mode as string) || typeof v.title!=='string' || !v.title.trim() || [...v.title].length>256 || typeof v.body!=='string' || [...v.body].length>4096) throw new HttpError(400,'INVALID_ARGUMENT');
  return {update_id:v.update_id as string,run_id:v.run_id as string,mode:v.mode as Update['mode'],device_alias:v.device_alias as string,title:v.title,body:v.body};
}
// JSON.parse validates syntax; this pass detects duplicate decoded object member names at any depth.
function parseUniqueJson(text:string):unknown {
  const value=JSON.parse(text); let i=0;
  const ws=()=>{while (/\s/.test(text[i] ?? '') && i<text.length) i++;};
  function str():string { const start=i++; while(i<text.length){if(text[i]==='\\'){i+=2;continue;} if(text[i++]==='"') break;} return JSON.parse(text.slice(start,i)); }
  function scan():void {
    ws(); if(text[i]==='"'){str();return;} if(text[i]==='{'){i++;const seen=new Set<string>();ws(); if(text[i]==='}'){i++;return;} while(true){ws(); const k=str();if(seen.has(k))throw Error('duplicate');seen.add(k);ws();i++;scan();ws();if(text[i++]==='}')return;}}
    if(text[i]==='['){i++;ws();if(text[i]===']'){i++;return;}while(true){scan();ws();if(text[i++]===']')return;}}
    while(i<text.length && !/[\s,}\]]/.test(text[i]))i++;
  }
  scan();return value;
}
async function body(req:IncomingMessage):Promise<unknown> {
  const chunks:Buffer[]=[]; let size=0;
  for await (const chunk of req) {const b=Buffer.from(chunk);size+=b.length;if(size<=MAX_BODY)chunks.push(b);}
  if(size>MAX_BODY)throw new HttpError(413,'PAYLOAD_TOO_LARGE');
  try { const bytes=Buffer.concat(chunks);const text=new TextDecoder('utf-8',{fatal:true}).decode(bytes);return parseUniqueJson(text); } catch {throw new HttpError(400,'INVALID_JSON');}
}
function matches(raw:string|undefined,version:number):boolean {
  if(!raw)return false; if(raw.trim()==='*')return true;
  const pattern=/^\s*(?:W\/)?"[\x21\x23-\x7e\x80-\xff]*"\s*(?:,\s*(?:W\/)?"[\x21\x23-\x7e\x80-\xff]*"\s*)*$/;
  if(!pattern.test(raw))return false;
  return [...raw.matchAll(/(?:W\/)?"([\x21\x23-\x7e\x80-\xff]*)"/g)].some(m=>m[1]===`v${version}`);
}
export function createServer(store:SnapshotStore) {
 return http.createServer(async(req:IncomingMessage,res:ServerResponse)=>{
  const headers:Record<string,string>={'X-API-Version':VERSION};
  let requestId:string|null=null;
  function json(status:number,data:unknown,extra:Record<string,string>={}) {res.writeHead(status,{...headers,'Content-Type':'application/json; charset=utf-8',...extra});res.end(JSON.stringify(data));}
  try {
    const ids=req.headersDistinct['x-correlation-request-id'];
    if(ids && (ids.length!==1 || !ID.test(ids[0])))throw new HttpError(400,'INVALID_REQUEST_ID');
    requestId=ids?.[0]??null;if(requestId)headers['X-Correlation-Request-Id']=requestId;
    const pathname=new URL(req.url??'/', 'http://localhost').pathname;
    const routes:Record<string,string>={'/health':'GET','/api/bulletin':'GET','/api/bulletin/update':'POST'};
    if(!Object.hasOwn(routes,pathname))throw new HttpError(404,'NOT_FOUND');
    if(req.method!==routes[pathname]) {headers.Allow=routes[pathname];throw new HttpError(405,'METHOD_NOT_ALLOWED');}
    if(pathname==='/health'){store.snapshot();return json(200,{api_version:VERSION,status:'ok'});}
    if(pathname==='/api/bulletin') {
      const snapshot=store.snapshot(), extra={ETag:`"v${snapshot.version}"`,'Cache-Control':'no-cache'};
      if(matches(req.headers['if-none-match'],snapshot.version)){res.writeHead(304,{...headers,...extra});return res.end();}
      return json(200,{api_version:VERSION,...snapshot},extra);
    }
    if(!/^application\/json(?:\s*;\s*charset\s*=\s*(?:utf-8|"utf-8"))?\s*$/i.test(req.headers['content-type']??'')) throw new HttpError(415,'UNSUPPORTED_MEDIA_TYPE');
    const length=req.headers['content-length'];if(length && Number(length)>MAX_BODY)throw new HttpError(413,'PAYLOAD_TOO_LARGE');
    const input=validate(await body(req));const result=store.update(input,requestId);
    return json(200,result,{ETag:`"v${result.version}"`});
  } catch(e) {
    let status=500,code='INTERNAL';
    if(e instanceof HttpError){status=e.status;code=e.code;}
    else if(e instanceof StoreError){code=e.code;status=['UPDATE_ID_CONFLICT','VERSION_EXHAUSTED','SNAPSHOT_FULL'].includes(code)?409:503;if(status===503)code='STORE_UNAVAILABLE';}
    if(!res.headersSent)json(status,{api_version:VERSION,error:{code,message:status===500?'Internal server error':status===503?'Store unavailable':'Invalid request',request_id:requestId}});else res.destroy();
  }
 });
}
if(process.argv[1] && path.resolve(process.argv[1])===fileURLToPath(import.meta.url)) {
 const base=path.resolve(process.env.STORE_DIR??'./.local/server');
 try {
  const store=new SnapshotStore(path.join(base,'state.json'),path.join(base,'events.jsonl'));
  const server=createServer(store), port=Number(process.env.PORT??3000), host=process.env.HOST??'127.0.0.1';
  server.listen(port,host,()=>console.log(`Snapshot server listening on ${host}:${port}`));
  server.on('error',()=>{console.error('SERVER_START_FAILED');store.close();process.exitCode=1;});
  for(const sig of ['SIGINT','SIGTERM'] as const)process.on(sig,()=>server.close(()=>{store.close();process.exit(0);}));
 } catch {console.error('STORE_UNAVAILABLE_OR_LOCKED');process.exitCode=1;}
}
