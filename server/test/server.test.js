import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {spawnSync,execFile} from 'node:child_process';
import {promisify} from 'node:util';
import {SnapshotStore} from '../dist/snapshot_store.js';
import {createServer} from '../dist/server.js';
const update=(id='up-1')=>({update_id:id,run_id:'run-1',mode:'PERIODIC',device_alias:'emulator',title:'Thông báo',body:'Body'});
async function setup(t) {
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'sem27-')), file=path.join(dir,'state.json'), events=path.join(dir,'events.jsonl');
 const store=new SnapshotStore(file,events), server=createServer(store);
 await new Promise((resolve,reject)=>{server.once('error',reject);server.listen(0,'127.0.0.1',resolve);});
 t.after(async()=>{await new Promise(r=>server.close(r));store.close();fs.rmSync(dir,{recursive:true,force:true});});
 const base=`http://127.0.0.1:${server.address().port}`, request=(u,opts)=>fetch(base+u,opts);
 const post=(v,headers={})=>request('/api/bulletin/update',{method:'POST',headers:{'content-type':'application/json',...headers},body:JSON.stringify(v)});
 return {dir,file,events,store,server,base,request,post};
}
test('v0, ETag, JSONL, retry response gốc và phục hồi export sau restart',async t=>{
 const x=await setup(t);let r=await x.request('/health');assert.equal(r.status,200);assert.equal(r.headers.get('x-api-version'),'2.0.0');
 r=await x.request('/api/bulletin');assert.equal(r.headers.get('etag'),'"v0"');assert.deepEqual((await r.json()).items,[]);
 r=await x.post(update(),{'X-Correlation-Request-Id':'req-1'});assert.equal(r.status,200);const first=await r.json();assert.equal(first.version,1);
 r=await x.post(update('up-2'));assert.equal((await r.json()).version,2);
 r=await x.request('/api/bulletin',{headers:{'If-None-Match':'W/"v2", "v9"'}});assert.equal(r.status,304);assert.equal(await r.text(),'');
 r=await x.request('/api/bulletin',{headers:{'If-None-Match':'W/"v2", bad'}});assert.equal(r.status,200);
 r=await x.request('/api/bulletin',{headers:{'If-None-Match':'*'}});assert.equal(r.status,304);
 const lines=fs.readFileSync(x.events,'utf8').trim().split('\n').map(JSON.parse);assert.equal(lines.length,2);assert.equal(lines[0].request_id,'req-1');assert.equal(lines[0].data_version,1);
 x.store.close();fs.unlinkSync(x.events);const restarted=new SnapshotStore(x.file,x.events);t.after(()=>restarted.close());
 const replay=restarted.update(update());assert.equal(replay.version,1);assert.equal(replay.replayed,true);assert.deepEqual(replay.items,first.items);assert.equal(restarted.snapshot().version,2);assert.equal(fs.readFileSync(x.events,'utf8').trim().split('\n').length,2);
 assert.throws(()=>restarted.update({...update(),body:'khác'}),{code:'UPDATE_ID_CONFLICT'});
});
test('cập nhật đồng thời và cùng id không mất version/event',async t=>{
 const x=await setup(t);const replies=await Promise.all(Array.from({length:25},(_,i)=>x.post(update(`id-${i}`))));
 const versions=await Promise.all(replies.map(async r=>{assert.equal(r.status,200);return (await r.json()).version;}));assert.deepEqual(versions.sort((a,b)=>a-b),Array.from({length:25},(_,i)=>i+1));
 const same=await Promise.all(Array.from({length:8},()=>x.post(update('same'))));const data=await Promise.all(same.map(r=>r.json()));assert.equal(data.filter(v=>!v.replayed).length,1);assert.ok(data.every(v=>v.version===26));assert.equal(fs.readFileSync(x.events,'utf8').trim().split('\n').length,26);
});
test('validation, duplicate JSON, media, kích thước, lỗi an toàn',async t=>{
 const x=await setup(t);
 for(const payload of [{...update(),extra:1},{...update(),title:' '},{...update(),update_id:'bad id'}]) {const r=await x.post(payload);assert.equal(r.status,400);assert.equal((await r.json()).error.code,'INVALID_ARGUMENT');}
 let r=await x.request('/api/bulletin/update',{method:'POST',headers:{'content-type':'application/json'},body:'{"title":"x","title":"y"}'});assert.equal((await r.json()).error.code,'INVALID_JSON');
 r=await x.request('/api/bulletin/update',{method:'POST',headers:{'content-type':'text/plain'},body:'{}'});assert.equal(r.status,415);
 r=await x.request('/api/bulletin/update',{method:'POST',headers:{'content-type':'application/json'},body:'x'.repeat(1048577)});assert.equal(r.status,413);
 r=await x.request('/health',{method:'POST'});assert.equal(r.status,405);assert.equal(r.headers.get('allow'),'GET');
 r=await x.request('/health',{headers:{'X-Correlation-Request-Id':'bad id'}});assert.equal(r.status,400);assert.equal(r.headers.get('x-correlation-request-id'),null);assert.equal((await r.json()).error.request_id,null);
 r=await x.request('/missing');assert.equal(r.status,404);assert.equal((await r.json()).api_version,'2.0.0');assert.equal(x.store.snapshot().version,0);
});
test('đầy 100 item vẫn replay được, từ chối ID mới',async t=>{
 const x=await setup(t);for(let i=0;i<100;i++){const r=await x.post(update(`id-${i}`));assert.equal(r.status,200);}
 let r=await x.post(update('id-0'));assert.equal(r.status,200);assert.equal((await r.json()).replayed,true);
 r=await x.post(update('id-100'));assert.equal(r.status,409);assert.equal((await r.json()).error.code,'SNAPSHOT_FULL');
});
test('store mất/hỏng không bị reset; chỉ một server giữ lock',async t=>{
 const x=await setup(t);await x.post(update());assert.throws(()=>new SnapshotStore(x.file,x.events),{code:'STORE_LOCKED'});
 fs.writeFileSync(x.file,'{}');let r=await x.request('/health');assert.equal(r.status,503);assert.equal((await r.json()).error.code,'STORE_UNAVAILABLE');
 fs.unlinkSync(x.file);r=await x.request('/api/bulletin');assert.equal(r.status,503);assert.equal(fs.existsSync(x.file),false);
});
test('CLI dùng API và không fallback ra file',async t=>{
 const x=await setup(t),args=['bin/update-cli.js','--base-url',x.base,'--update-id','cli-1','--run','run-1','--mode','PUSH','--device','emulator','--title','Title','--body','Body'];
 const run=promisify(execFile);const result=await run(process.execPath,args,{cwd:process.cwd()});assert.equal(JSON.parse(result.stdout).version,1);
 const again=await run(process.execPath,args,{cwd:process.cwd()});assert.equal(JSON.parse(again.stdout).replayed,true);
 const failed=spawnSync(process.execPath,['bin/update-cli.js','--base-url','http://127.0.0.1:1',...args.slice(3)],{cwd:process.cwd(),encoding:'utf8'});assert.notEqual(failed.status,0);assert.match(failed.stderr,/"commit":"unknown"/);assert.equal(x.store.snapshot().version,1);
});
test('không khởi tạo đè thư mục có snapshot v1',()=>{
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'sem27-old-'));
 try {fs.writeFileSync(path.join(dir,'snapshot.json'),'{"version":1}');assert.throws(()=>new SnapshotStore(path.join(dir,'state.json'),path.join(dir,'events.jsonl')),{code:'STORE_UNAVAILABLE'});assert.equal(fs.existsSync(path.join(dir,'state.json')),false);} finally {fs.rmSync(dir,{recursive:true,force:true});}
});
test('process bị dừng đột ngột: phục hồi state và outbox sau khi xác minh/gỡ lock cũ',async t=>{
 const {spawn}=await import('node:child_process');const {once}=await import('node:events');const readline=await import('node:readline');
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'sem27-crash-')),file=path.join(dir,'state.json'),events=path.join(dir,'events.jsonl');
 const program=`import {SnapshotStore} from './dist/snapshot_store.js'; import {createServer} from './dist/server.js'; const store=new SnapshotStore(process.env.STATE,process.env.EVENTS); const s=createServer(store); s.listen(0,'127.0.0.1',()=>console.log(s.address().port));`;
 const child=spawn(process.execPath,['--input-type=module','-e',program],{cwd:process.cwd(),env:{...process.env,STATE:file,EVENTS:events},stdio:['ignore','pipe','pipe']});
 t.after(()=>{if(child.exitCode===null && child.signalCode===null)child.kill('SIGKILL');fs.rmSync(dir,{recursive:true,force:true});});
 const lines=readline.createInterface({input:child.stdout}); const [port]=await once(lines,'line');
 const r=await fetch(`http://127.0.0.1:${port}/api/bulletin/update`,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(update())});assert.equal(r.status,200);
 child.kill('SIGKILL');await once(child,'exit');assert.equal(fs.existsSync(`${file}.lock`),true);
 assert.throws(()=>new SnapshotStore(file,events),{code:'STORE_LOCKED'});fs.unlinkSync(`${file}.lock`);fs.unlinkSync(events);
 const recovered=new SnapshotStore(file,events);assert.equal(recovered.snapshot().version,1);assert.equal(recovered.update(update()).replayed,true);assert.equal(fs.readFileSync(events,'utf8').trim().split('\n').length,1);recovered.close();
});
