#!/usr/bin/env node
const aliases={'--update-id':'update_id','--run':'run_id','--mode':'mode','--device':'device_alias','--title':'title','--body':'body','--request-id':'request_id','--base-url':'base_url'};
const options={}; const args=process.argv.slice(2);
for(let i=0;i<args.length;i++) {
 const key=aliases[args[i]];
 if(!key || Object.hasOwn(options,key) || i+1>=args.length || args[i+1].startsWith('--')) { console.error('INVALID_ARGUMENT: kiểm tra tên tham số và giá trị.'); process.exit(2); }
 options[key]=args[++i];
}
const required=['update_id','run_id','mode','device_alias','title','body'];
if(!required.every(k=>Object.hasOwn(options,k))) {console.error('Thiếu tham số: --update-id --run --mode --device --title --body. Giữ update-id khi retry.');process.exit(2);}
const payload=Object.fromEntries(required.map(k=>[k,options[k]]));
try {
 const base=options.base_url??process.env.SERVER_URL??'http://127.0.0.1:3000';
 const url=new URL('/api/bulletin/update',base);
 if(!['http:','https:'].includes(url.protocol)) throw Error('invalid URL');
 const headers={'Content-Type':'application/json',Accept:'application/json'};
 if(options.request_id)headers['X-Correlation-Request-Id']=options.request_id;
 const response=await fetch(url,{method:'POST',headers,body:JSON.stringify(payload),signal:AbortSignal.timeout(10000)});
 const result=await response.json().catch(()=>null);
 if(!response.ok) { console.error(JSON.stringify({status:response.status,code:typeof result?.error?.code==='string'?result.error.code:null,update_id:options.update_id,commit:[400,409,413,415].includes(response.status)?'not_committed':'unknown'}));process.exitCode=1; }
 else if(response.headers.get('x-api-version')!=='2.0.0' || result?.api_version!=='2.0.0' || result.update_id!==options.update_id || !Number.isSafeInteger(result.version) || typeof result.replayed!=='boolean' || !Array.isArray(result.items)) {console.error(JSON.stringify({code:'INVALID_RESPONSE',update_id:options.update_id,commit:'unknown'}));process.exitCode=1;}
 else console.log(JSON.stringify({update_id:result.update_id,run_id:result.run_id,version:result.version,replayed:result.replayed,etag:response.headers.get('etag')}));
} catch {console.error(JSON.stringify({code:'NETWORK_OR_CONFIG_ERROR',update_id:options.update_id,commit:'unknown',instruction:'retry với cùng update_id qua API'}));process.exitCode=1;}
