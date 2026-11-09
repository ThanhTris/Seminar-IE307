#!/usr/bin/env node
import {openSkipLog} from '../src/skip_push.js';
const aliases={'--update-id':'update_id','--run':'run_id','--mode':'mode','--device':'device_alias','--title':'title','--body':'body','--request-id':'request_id','--base-url':'base_url','--events':'events'};
const options={}; const args=process.argv.slice(2);
for(let i=0;i<args.length;i++) {
 if(args[i]==='--skip-push'){if(options.skip_push){console.error('INVALID_ARGUMENT');process.exit(2);}options.skip_push=true;continue;}
 const key=aliases[args[i]];
 if(!key || Object.hasOwn(options,key) || i+1>=args.length || args[i+1].startsWith('--')) { console.error('INVALID_ARGUMENT: kiểm tra tên tham số và giá trị.'); process.exit(2); }
 options[key]=args[++i];
}
const required=['update_id','run_id','mode','device_alias','title','body'];
if(!required.every(k=>Object.hasOwn(options,k))) {console.error('Thiếu tham số: --update-id --run --mode --device --title --body. Giữ update-id khi retry.');process.exit(2);}
const payload=Object.fromEntries(required.map(k=>[k,options[k]]));
if((options.skip_push && options.mode!=='HYBRID') || (options.events && !options.skip_push)){console.error('INVALID_ARGUMENT: --skip-push dùng cho HYBRID; --events chỉ dùng cùng --skip-push.');process.exit(2);}
let skipLog;
try {
 if(options.skip_push)skipLog=openSkipLog(options.events??'./.local/fault-injection/events.jsonl');
 const base=options.base_url??process.env.SERVER_URL??'http://127.0.0.1:3000';
 const url=new URL('/api/bulletin/update',base);
 if(!['http:','https:'].includes(url.protocol)) throw Error('invalid URL');
 const headers={'Content-Type':'application/json',Accept:'application/json'};
 if(options.request_id)headers['X-Correlation-Request-Id']=options.request_id;
 const response=await fetch(url,{method:'POST',headers,body:JSON.stringify(payload),signal:AbortSignal.timeout(10000)});
 const result=await response.json().catch(()=>null);
 if(!response.ok) { console.error(JSON.stringify({status:response.status,code:typeof result?.error?.code==='string'?result.error.code:null,update_id:options.update_id,commit:[400,409,413,415].includes(response.status)?'not_committed':'unknown'}));process.exitCode=1; }
 else if(response.headers.get('x-api-version')!=='2.0.0' || result?.api_version!=='2.0.0' || result.update_id!==options.update_id || !Number.isSafeInteger(result.version) || typeof result.replayed!=='boolean' || !Array.isArray(result.items)) {console.error(JSON.stringify({code:'INVALID_RESPONSE',update_id:options.update_id,commit:'unknown'}));process.exitCode=1;}
 else {
  const skipped=skipLog?.record(payload,result,response.headers.get('etag'));
  console.log(JSON.stringify({update_id:result.update_id,run_id:result.run_id,version:result.version,replayed:result.replayed,etag:response.headers.get('etag'),...(skipped?{fault_injection:true,push:'skipped',reason:skipped.reason,event_id:skipped.event_id,commit_timestamp_utc:result.last_modified_utc}:{})}));
 }
} catch {console.error(JSON.stringify({code:options.skip_push?'SKIP_NOT_CONFIRMED':'NETWORK_OR_CONFIG_ERROR',update_id:options.update_id,commit:'unknown',instruction:'retry với cùng update_id qua API'}));process.exitCode=1;}

finally {if(skipLog){try {skipLog.close();}catch{console.error('SKIP_LOG_CLEANUP_FAILED');process.exitCode=1;}}}
