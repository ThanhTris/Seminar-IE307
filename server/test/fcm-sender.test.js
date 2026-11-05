import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {validInput,payload,execute,appendEvent,verifyCommit} from '../src/fcm_sender.js';
const input={run_id:'run-1',mode:'PUSH',device_alias:'emu-1',update_id:'up-1',signal_id:'signal-1',version:7,ttl_ms:86400000};
const token='SYNTHETIC_TOKEN_NEVER_LOG';
const sample=(send)=>({verify:async()=>{},prepare:async()=>({token,send,close:async()=>{}}),write:()=>{}});
test('data-only, normal, giá trị data dạng chuỗi và TTL milliseconds',()=>{
 const m=payload(input,token);assert.deepEqual(Object.keys(m).sort(),['android','data','token']);assert.equal(m.android.priority,'normal');assert.equal(m.android.ttl,86400000);assert.equal(m.data.version_hint,'7');assert.equal(m.data.signal_id,'signal-1');assert.ok(Object.values(m.data).every(x=>typeof x==='string'));assert.equal(m.notification,undefined);assert.equal(m.android.notification,undefined);
 assert.equal(validInput({...input,ttl_ms:2419200000}),true);assert.equal(validInput({...input,ttl_ms:2419200001}),false);assert.equal(validInput({...input,version:1.2}),false);assert.equal(validInput({...input,mode:'PERIODIC'}),false);
});
test('SDK trả ID thật giả lập: event đầy đủ, không lộ token; retry giữ signal, thay attempt',async()=>{
 const rows=[],d=sample(async()=> 'projects/demo/messages/fixture-1');d.write=e=>rows.push(e);
 const one=await execute(input,d),two=await execute(input,d);assert.equal(one.status,'accepted');assert.equal(one.event.message_id,'projects/demo/messages/fixture-1');assert.equal(one.event.signal_ids[0],input.signal_id);assert.notEqual(one.event.send_attempt_id,two.event.send_attempt_id);assert.equal(one.event.event_type,'push_send_accepted');
 const keys=['schema_version','event_id','event_type','origin','run_id','mode','source','device_alias','timestamp_utc','elapsed_realtime_ms','boot_session_id','data_version','cached_version','version_hint','request_id','work_id','work_attempt','network_call_id','update_id','signal_ids','send_attempt_id','message_id','ttl_ms','http_status','provider_code','outcome','reason'];assert.deepEqual(Object.keys(one.event).sort(),keys.sort());assert.equal(JSON.stringify(rows).includes(token),false);
});
test('FCM từ chối xác định, network không rõ và thông tin lỗi nhạy cảm không xuất hiện',async()=>{
 let d=sample(async()=>{throw Object.assign(new Error(token),{code:'messaging/registration-token-not-registered'});});let r=await execute(input,d);assert.equal(r.status,'rejected');assert.equal(r.event.reason,'FCM_REJECTED');assert.equal(r.event.message_id,null);assert.equal(JSON.stringify(r).includes(token),false);
 d=sample(async()=>{throw Object.assign(new Error(token),{code:'messaging/server-unavailable'});});r=await execute(input,d);assert.equal(r.status,'unknown');assert.equal(r.event.event_type,'push_send_unknown');assert.equal(r.event.reason,'FCM_RESPONSE_UNKNOWN');assert.equal(r.event.message_id,null);
 d=sample(async()=>{throw Object.assign(new Error(token),{code:token});});r=await execute(input,d);assert.equal(r.event.provider_code,null);assert.equal(JSON.stringify(r).includes(token),false);
});
test('trước gửi lỗi store/cấu hình: local failure, không tạo attempt hoặc gọi send',async()=>{
 let called=0,d=sample(async()=>{called++;return 'id';});d.verify=async()=>{throw Error(token);};let r=await execute(input,d);assert.equal(r.status,'local_failure');assert.equal(r.event.data_version,null);assert.equal(r.event.send_attempt_id,null);assert.equal(called,0);
 d=sample(async()=>{called++;});d.prepare=async()=>{throw Error(token);};r=await execute(input,d);assert.equal(r.event.reason,'INVALID_FCM_CONFIG');assert.equal(r.event.send_attempt_id,null);assert.equal(called,0);
 assert.equal((await execute({...input,run_id:'bad id'},d)).event,null);
});
test('lỗi ghi log sau send không tạo nhầm rejected hoặc gửi lần hai',async()=>{
 let sends=0,writes=0;const d=sample(async()=>{sends++;return 'fixture-message-id';});d.write=()=>{writes++;throw Error('disk');};await assert.rejects(execute(input,d));assert.equal(sends,1);assert.equal(writes,1);
});
test('kiểm server version và server_updated trước khi gửi',async t=>{
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'sem35-')),f=path.join(dir,'server.jsonl');t.after(()=>fs.rmSync(dir,{recursive:true,force:true}));
 const e={schema_version:'2.0.0',event_type:'server_updated',origin:'SERVER',outcome:'updated',run_id:input.run_id,mode:input.mode,device_alias:input.device_alias,update_id:input.update_id,data_version:input.version};fs.writeFileSync(f,JSON.stringify(e)+'\n');
 const fetchImpl=async()=>new Response(JSON.stringify({api_version:'2.0.0',version:7,items:[]}),{status:200,headers:{'X-API-Version':'2.0.0'}});
 await verifyCommit(input,{serverEvents:f,baseUrl:'http://127.0.0.1:3000',fetchImpl});await assert.rejects(verifyCommit({...input,update_id:'other'},{serverEvents:f,baseUrl:'http://127.0.0.1:3000',fetchImpl}));await assert.rejects(verifyCommit({...input,version:8},{serverEvents:f,baseUrl:'http://127.0.0.1:3000',fetchImpl}));
 const log=path.join(dir,'sender.jsonl');appendEvent(log,{schema_version:'2.0.0',event_type:'fixture'});assert.equal(JSON.parse(fs.readFileSync(log,'utf8')).event_type,'fixture');
});
test('CLI validate-only không gửi và không nhận token qua argument',()=>{
 const args=['bin/fcm-sender.js','--validate-only','--run','run-1','--mode','PUSH','--device','emu-1','--update-id','up-1','--signal-id','sig-1','--version','7'];
 const r=spawnSync(process.execPath,args,{cwd:process.cwd(),encoding:'utf8'});assert.equal(r.status,0);const out=JSON.parse(r.stdout);assert.equal(out.status,'validated_locally');assert.equal(JSON.stringify(out).includes('TOKEN_NOT_SENT'),false);
 const bad=spawnSync(process.execPath,[...args,'--token',token],{cwd:process.cwd(),encoding:'utf8'});assert.notEqual(bad.status,0);assert.equal((bad.stdout+bad.stderr).includes(token),false);
});
test('CLI thực qua server cục bộ: chưa cấu hình Firebase tạo local failure, không gọi FCM',async t=>{
 const {SnapshotStore}=await import('../dist/snapshot_store.js');const {createServer}=await import('../dist/server.js');
 const {execFile}=await import('node:child_process');const {promisify}=await import('node:util');
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'sem35-cli-')),state=path.join(dir,'state.json'),events=path.join(dir,'server.jsonl'),out=path.join(dir,'sender.jsonl');
 const store=new SnapshotStore(state,events),server=createServer(store);await new Promise((resolve,reject)=>{server.once('error',reject);server.listen(0,'127.0.0.1',resolve);});
 t.after(async()=>{await new Promise(r=>server.close(r));store.close();fs.rmSync(dir,{recursive:true,force:true});});
 const body={update_id:'up-1',run_id:'run-1',mode:'PUSH',device_alias:'emu-1',title:'Test',body:'fixture'};store.update(body);
 const env={...process.env};delete env.GOOGLE_APPLICATION_CREDENTIALS;delete env.FIREBASE_PROJECT_ID;delete env.FCM_TOKEN_FILE;
 const args=['bin/fcm-sender.js','--send','--run','run-1','--mode','PUSH','--device','emu-1','--update-id','up-1','--signal-id','signal-1','--version','1','--base-url',`http://127.0.0.1:${server.address().port}`,'--server-events',events,'--events',out];
 let err;try {await promisify(execFile)(process.execPath,args,{cwd:process.cwd(),env});}catch(e){err=e;}assert.equal(err?.code,1);
 const row=JSON.parse(fs.readFileSync(out,'utf8'));assert.equal(row.event_type,'push_send_failed_local');assert.equal(row.reason,'INVALID_FCM_CONFIG');assert.equal(row.data_version,1);assert.equal(row.send_attempt_id,null);assert.equal(row.message_id,null);
});
test('event sender phù hợp validator SEM-24 cho accepted/rejected/unknown/local',async()=>{
 const rows=[];let d=sample(async()=> 'projects/demo/messages/fixture');d.write=e=>rows.push(e);await execute(input,d);
 d=sample(async()=>{throw Object.assign(new Error('fixture'),{code:'messaging/registration-token-not-registered'});});d.write=e=>rows.push(e);await execute(input,d);
 d=sample(async()=>{throw Error('fixture');});d.write=e=>rows.push(e);await execute(input,d);
 d=sample(async()=>{});d.verify=async()=>{throw Error('fixture');};d.write=e=>rows.push(e);await execute(input,d);
 const script='import sys,json;sys.path.insert(0,"../experiments/scripts");from export_logs import validate_event;[validate_event(e) for e in json.load(sys.stdin)]';
 const r=spawnSync('python3',['-c',script],{input:JSON.stringify(rows),encoding:'utf8',cwd:process.cwd()});assert.equal(r.status,0,r.stderr);
});
