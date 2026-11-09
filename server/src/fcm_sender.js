import fs from 'node:fs';
import path from 'node:path';
import {randomUUID} from 'node:crypto';
import {applicationDefault, initializeApp, deleteApp} from 'firebase-admin/app';
import {getMessaging} from 'firebase-admin/messaging';

const ID=/^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$/;
const SAFE_CODE=/^messaging\/[a-z][a-z0-9-]{0,63}$/;
const MAX_TTL=2419200000;
const REJECTED=new Set(['messaging/registration-token-not-registered','messaging/mismatched-credential']);
export function validInput(o) {
 return o && ['run_id','device_alias','update_id','signal_id'].every(k=>typeof o[k]==='string' && ID.test(o[k])) && ['PUSH','HYBRID'].includes(o.mode) && Number.isSafeInteger(o.version) && o.version>=0 && Number.isSafeInteger(o.ttl_ms) && o.ttl_ms>=0 && o.ttl_ms<=MAX_TTL;
}
export function payload(o, token) {
 return {token,data:{run_id:o.run_id,mode:o.mode,source:'PUSH',version_hint:String(o.version),signal_id:o.signal_id},android:{priority:'normal',ttl:o.ttl_ms}};
}
function event(o,type,outcome,reason,attempt=null,code=null,message=null) {
 return {schema_version:'2.0.0',event_id:randomUUID(),event_type:type,origin:'SERVER',run_id:o.run_id,mode:o.mode,source:'PUSH',device_alias:o.device_alias,timestamp_utc:new Date().toISOString(),elapsed_realtime_ms:null,boot_session_id:null,data_version:o.version,cached_version:null,version_hint:o.version,request_id:null,work_id:null,work_attempt:null,network_call_id:null,update_id:o.update_id,signal_ids:[o.signal_id],send_attempt_id:attempt,message_id:message,ttl_ms:o.ttl_ms,http_status:null,provider_code:code,outcome,reason};
}
export function appendEvent(file, e) {
 fs.mkdirSync(path.dirname(path.resolve(file)),{recursive:true});
 const fd=fs.openSync(file,'a',0o600); try {fs.writeFileSync(fd,JSON.stringify(e)+'\n');fs.fsyncSync(fd);} finally {fs.closeSync(fd);}
}
export async function verifyCommit(o,{serverEvents,baseUrl,fetchImpl=fetch}) {
 const response=await fetchImpl(new URL('/api/bulletin',baseUrl),{headers:{Accept:'application/json'},signal:AbortSignal.timeout(5000)});
 if(!response.ok || response.headers.get('x-api-version')!=='2.0.0')throw Error('preflight');
 const snapshot=await response.json();
 if(snapshot.api_version!=='2.0.0' || !Number.isSafeInteger(snapshot.version) || snapshot.version<o.version)throw Error('preflight');
 const lines=fs.readFileSync(serverEvents,'utf8').split('\n').filter(Boolean);
 const found=lines.some(line=>{const e=JSON.parse(line);return e.schema_version==='2.0.0' && e.event_type==='server_updated' && e.outcome==='updated' && e.origin==='SERVER' && e.update_id===o.update_id && e.run_id===o.run_id && e.mode===o.mode && e.device_alias===o.device_alias && e.data_version===o.version;});
 if(!found)throw Error('preflight');
}
export async function execute(o, deps) {
 if(!validInput(o))return {status:'invalid',event:null};
 const write=e=>deps.write(e);
 try {await deps.verify();} catch {const e=event(o,'push_send_failed_local','failure','STORE_UNAVAILABLE');e.data_version=null;write(e);return {status:'local_failure',event:e};}
 let ready;
 try {ready=await deps.prepare();} catch {const e=event(o,'push_send_failed_local','failure','INVALID_FCM_CONFIG');write(e);return {status:'local_failure',event:e};}
 const attempt=randomUUID(); let e;
 try {
  const id=await ready.send(payload(o,ready.token));
  e=typeof id==='string' && id.length>=1 && id.length<=512 && !id.includes(ready.token)
   ? event(o,'push_send_accepted','accepted',null,attempt,null,id)
   : event(o,'push_send_unknown','unknown','FCM_RESPONSE_UNKNOWN',attempt);
 } catch(err) {
  // Do not classify generic SDK, authentication or transport errors as a provider rejection.
  const code=typeof err?.code==='string' && SAFE_CODE.test(err.code)?err.code:null;
  const rejected=code!==null && REJECTED.has(code);
  e=event(o,rejected?'push_send_rejected':'push_send_unknown',rejected?'rejected':'unknown',rejected?'FCM_REJECTED':'FCM_RESPONSE_UNKNOWN',attempt,code);
 } finally {try {await ready.close();} catch {}}
 // A log failure must not turn a successful FCM response into a fabricated rejection.
 write(e);return {status:e.outcome,event:e};
}
export async function prepareFirebase({tokenFile,projectId,credentialPath}) {
 if(!tokenFile || !credentialPath || !projectId || !/^[a-z][a-z0-9-]{4,28}[a-z0-9]$/.test(projectId) || !fs.statSync(credentialPath).isFile())throw Error('config');
 const token=fs.readFileSync(tokenFile,'utf8').trim();if(!token || /\s/.test(token) || token.length>8192)throw Error('config');
 const credential=applicationDefault();let app;
 try {app=initializeApp({credential,projectId},`sem35-${randomUUID()}`);await credential.getAccessToken();}
 catch {if(app)await deleteApp(app);throw Error('config');}
 return {token,send:message=>getMessaging(app).send(message),close:()=>deleteApp(app)};
}
