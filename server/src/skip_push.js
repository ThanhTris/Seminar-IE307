import fs from 'node:fs';
import path from 'node:path';
import {randomUUID} from 'node:crypto';

// Independent of Firebase: this path records an intentional omission, never a send.
export function openSkipLog(file) {
 const absolute=path.resolve(file), dir=path.dirname(absolute);
 const store=path.resolve(process.env.STORE_DIR??'./.local/server');
 const real=p=>fs.existsSync(p)?fs.realpathSync(p):p;
 if(['state.json','events.jsonl'].some(name=>real(absolute)===real(path.join(store,name))))throw Error('LOG_PATH_CONFLICT');
 fs.mkdirSync(dir,{recursive:true});
 const lock=absolute+'.lock', lockFd=fs.openSync(lock,'wx',0o600);
 let fd;
 try {
  fs.writeFileSync(lockFd,String(process.pid));
  fd=fs.openSync(absolute,'a',0o600);
  const rows=fs.readFileSync(absolute,'utf8').split('\n').filter(Boolean).map(JSON.parse);
  if(rows.some(e=>e.schema_version!=='2.0.0' || e.event_type!=='push_send_skipped' || e.outcome!=='skipped' || e.reason!=='FAULT_INJECTION_SKIP'))throw Error('INVALID_SKIP_LOG');
  return {
   record(input,response,etag) {
    if(response.api_version!=='2.0.0' || response.run_id!==input.run_id || response.update_id!==input.update_id || !Number.isSafeInteger(response.version) || response.version<1 || etag!==`"v${response.version}"` || !Number.isFinite(Date.parse(response.last_modified_utc)))throw Error('INVALID_RESPONSE');
    const previous=rows.find(e=>e.update_id===input.update_id && e.run_id===input.run_id && e.device_alias===input.device_alias);
    if(previous) {if(previous.data_version!==response.version || previous.mode!==input.mode)throw Error('SKIP_LOG_CONFLICT');return previous;}
    const event={schema_version:'2.0.0',event_id:randomUUID(),event_type:'push_send_skipped',origin:'SERVER',run_id:input.run_id,mode:input.mode,source:'PUSH',device_alias:input.device_alias,timestamp_utc:new Date().toISOString(),elapsed_realtime_ms:null,boot_session_id:null,data_version:response.version,cached_version:null,version_hint:null,request_id:null,work_id:null,work_attempt:null,network_call_id:null,update_id:input.update_id,signal_ids:[],send_attempt_id:null,message_id:null,ttl_ms:null,http_status:null,provider_code:null,outcome:'skipped',reason:'FAULT_INJECTION_SKIP'};
    fs.writeFileSync(fd,JSON.stringify(event)+'\n');fs.fsyncSync(fd);rows.push(event);return event;
   },
   close(){fs.closeSync(fd);fs.closeSync(lockFd);fs.unlinkSync(lock);}
  };
 } catch(e) {if(fd!==undefined)fs.closeSync(fd);fs.closeSync(lockFd);fs.unlinkSync(lock);throw e;}
}
