import fs from 'node:fs';
import path from 'node:path';
import { randomUUID } from 'node:crypto';

export type Update = { update_id: string; run_id: string; mode: 'PERIODIC'|'PUSH'|'HYBRID'; device_alias: string; title: string; body: string };
type Item = { id:string; title:string; body:string; version:number };
type Snapshot = {version:number; last_modified_utc:string; items:Item[]};
type Reply = Snapshot & {api_version:string; update_id:string; run_id:string; replayed:boolean};
type Event = Record<string, unknown>;
type State = { format:2; snapshot:Snapshot; ledger:Record<string,{request:Update; response:Reply}>; events:Event[] };
export class StoreError extends Error { constructor(public code:string) { super(code); } }

function atomicWrite(file:string, data:string) {
  const dir=path.dirname(file), tmp=path.join(dir, `.${path.basename(file)}.${process.pid}.${randomUUID()}.tmp`);
  let fd:number|undefined;
  try {
    fd=fs.openSync(tmp,'wx',0o600); fs.writeFileSync(fd,data); fs.fsyncSync(fd); fs.closeSync(fd); fd=undefined;
    fs.renameSync(tmp,file);
    if (process.platform !== 'win32') {
      const d=fs.openSync(dir,'r'); try { fs.fsyncSync(d); } finally { fs.closeSync(d); }
    }
  } finally { if(fd!==undefined) fs.closeSync(fd); try {fs.unlinkSync(tmp);} catch {} }
}
function validState(s:State):boolean {
  if (!s || s.format!==2 || !s.snapshot || !Number.isSafeInteger(s.snapshot.version) || s.snapshot.version<0 || !Array.isArray(s.snapshot.items) || !s.ledger || typeof s.ledger!=='object' || Array.isArray(s.ledger) || !Array.isArray(s.events)) return false;
  const n=s.snapshot.version, entries=Object.entries(s.ledger);
  if (n!==entries.length || n!==s.events.length || s.snapshot.items.length!==n || n>100 || typeof s.snapshot.last_modified_utc!=='string' || !/^\d{4}-\d\d-\d\dT.*Z$/.test(s.snapshot.last_modified_utc) || !Number.isFinite(Date.parse(s.snapshot.last_modified_utc))) return false;
  if (!s.snapshot.items.every((it,i)=>it && it.version===n-i && it.id===`bulletin-${it.version}` && typeof it.title==='string' && typeof it.body==='string')) return false;
  const versions=new Set<number>(), eventIds=new Set<unknown>();
  for (const [id,entry] of entries) {
    if (!entry || entry.request?.update_id!==id || entry.response?.update_id!==id || entry.response.run_id!==entry.request.run_id || entry.response.api_version!=='2.0.0' || entry.response.replayed!==false || !Number.isSafeInteger(entry.response.version) || entry.response.version<1 || entry.response.version>n || versions.has(entry.response.version)) return false;
    versions.add(entry.response.version);
  }
  return s.events.every((e,i)=>{ if (!e || e.event_type!=='server_updated' || e.data_version!==i+1 || typeof e.event_id!=='string' || eventIds.has(e.event_id) || typeof e.update_id!=='string' || !s.ledger[e.update_id] || s.ledger[e.update_id].response.version!==i+1) return false; eventIds.add(e.event_id); return true; });
}
export class SnapshotStore {
  private lockFd:number;
  private lockFile:string;
  constructor(public file:string, public eventsFile:string) {
    fs.mkdirSync(path.dirname(file),{recursive:true}); fs.mkdirSync(path.dirname(eventsFile),{recursive:true});
    this.lockFile=`${file}.lock`;
    try { this.lockFd=fs.openSync(this.lockFile,'wx',0o600); }
    catch { throw new StoreError('STORE_LOCKED'); }
    try {
      fs.writeFileSync(this.lockFd, `${process.pid}\n`); fs.fsyncSync(this.lockFd);
      if (!fs.existsSync(file)) {
        if (fs.existsSync(eventsFile) || fs.existsSync(path.join(path.dirname(file),'snapshot.json'))) throw new StoreError('STORE_UNAVAILABLE');
        const initial:State={format:2,snapshot:{version:0,last_modified_utc:new Date().toISOString(),items:[]},ledger:{},events:[]};
        atomicWrite(file,JSON.stringify(initial));
      }
      this.read(); this.exportEvents();
    } catch(e) { this.close(); throw e; }
  }
  close() { if(this.lockFd!==-1) { fs.closeSync(this.lockFd); this.lockFd=-1; try {fs.unlinkSync(this.lockFile);} catch {} } }
  private read():State { try { const s=JSON.parse(fs.readFileSync(this.file,'utf8')) as State; if (!validState(s)) throw Error(); return s; } catch { throw new StoreError('STORE_UNAVAILABLE'); } }
  snapshot():Snapshot { return this.read().snapshot; }
  exportEvents() { const s=this.read(); atomicWrite(this.eventsFile,s.events.map(e=>JSON.stringify(e)+'\n').join('')); }
  update(input:Update, requestId:string|null=null):Reply {
    const state=this.read(), existing=Object.hasOwn(state.ledger,input.update_id) ? state.ledger[input.update_id] : undefined;
    if (existing) {
      const keys: (keyof Update)[]=['update_id','run_id','mode','device_alias','title','body'];
      if (!keys.every(k=>input[k]===existing.request[k])) throw new StoreError('UPDATE_ID_CONFLICT');
      try { this.exportEvents(); } catch {};
      return {...existing.response,replayed:true};
    }
    if (state.snapshot.version>=Number.MAX_SAFE_INTEGER) throw new StoreError('VERSION_EXHAUSTED');
    if (state.snapshot.items.length>=100) throw new StoreError('SNAPSHOT_FULL');
    const version=state.snapshot.version+1, now=new Date().toISOString();
    const snapshot:Snapshot={version,last_modified_utc:now,items:[{id:`bulletin-${version}`,title:input.title,body:input.body,version},...state.snapshot.items]};
    const response:Reply={api_version:'2.0.0',update_id:input.update_id,run_id:input.run_id,replayed:false,...snapshot};
    const event:Event={schema_version:'2.0.0',event_id:randomUUID(),event_type:'server_updated',origin:'SERVER',run_id:input.run_id,mode:input.mode,source:null,device_alias:input.device_alias,timestamp_utc:now,elapsed_realtime_ms:null,boot_session_id:null,data_version:version,cached_version:null,version_hint:null,request_id:requestId,work_id:null,work_attempt:null,network_call_id:null,update_id:input.update_id,signal_ids:[],send_attempt_id:null,message_id:null,ttl_ms:null,http_status:null,provider_code:null,outcome:'updated',reason:null};
    state.snapshot=snapshot; Object.defineProperty(state.ledger,input.update_id,{value:{request:input,response},enumerable:true,writable:true,configurable:true}); state.events.push(event);
    try { atomicWrite(this.file,JSON.stringify(state)); } catch { throw new StoreError('STORE_UNAVAILABLE'); }
    try { this.exportEvents(); } catch { console.error('EVENT_EXPORT_PENDING'); }
    return response;
  }
}
