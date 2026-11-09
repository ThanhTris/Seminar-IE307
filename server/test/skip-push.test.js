import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {execFile,spawnSync} from 'node:child_process';
import {promisify} from 'node:util';
import {SnapshotStore} from '../dist/snapshot_store.js';
import {createServer} from '../dist/server.js';
import {openSkipLog} from '../src/skip_push.js';
const run=promisify(execFile);
async function setup(t) {
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'sem40-')),file=path.join(dir,'state.json'),events=path.join(dir,'server.jsonl'),skip=path.join(dir,'skip.jsonl');
 const store=new SnapshotStore(file,events),server=createServer(store);
 await new Promise((resolve,reject)=>{server.once('error',reject);server.listen(0,'127.0.0.1',resolve);});
 t.after(async()=>{await new Promise(r=>server.close(r));store.close();fs.rmSync(dir,{recursive:true,force:true});});
 const args=['bin/update-cli.js','--base-url',`http://127.0.0.1:${server.address().port}`,'--skip-push','--events',skip,'--update-id','skip-1','--run','e06-test','--mode','HYBRID','--device','emulator-test','--title','Test','--body','fixture'];
 return {dir,file,events,skip,store,server,args};
}
test('CLI skip: update thật, replay không tăng version/nhân event; không có accepted, schema hợp lệ',async t=>{
 const x=await setup(t);
 const first=JSON.parse((await run(process.execPath,x.args)).stdout);assert.equal(first.version,1);assert.equal(first.push,'skipped');assert.equal(first.reason,'FAULT_INJECTION_SKIP');
 const replay=JSON.parse((await run(process.execPath,x.args)).stdout);assert.equal(replay.version,1);assert.equal(replay.replayed,true);assert.equal(replay.event_id,first.event_id);
 const rows=fs.readFileSync(x.skip,'utf8').trim().split('\n').map(JSON.parse);assert.equal(rows.length,1);const e=rows[0];assert.equal(e.event_type,'push_send_skipped');assert.equal(e.data_version,1);assert.equal(e.update_id,'skip-1');assert.equal(e.run_id,'e06-test');assert.equal(e.mode,'HYBRID');assert.equal(e.message_id,null);assert.equal(e.send_attempt_id,null);assert.deepEqual(e.signal_ids,[]);
 const all=[...rows,...fs.readFileSync(x.events,'utf8').trim().split('\n').map(JSON.parse)];assert.equal(all.some(e=>e.event_type==='push_send_accepted'),false);
 const python=process.env.PYTHON||(process.platform==='win32'?'python':'python3');const v=spawnSync(python,['-c','import sys,json;sys.path.insert(0,"../experiments/scripts");from export_logs import validate_event;[validate_event(e) for e in json.load(sys.stdin)]'],{input:JSON.stringify(all),encoding:'utf8'});assert.equal(v.status,0,v.error?.message??v.stderr);
 await new Promise(r=>x.server.close(r));x.store.close();const recovered=new SnapshotStore(x.file,x.events);assert.equal(recovered.snapshot().version,1);assert.equal(recovered.snapshot().items[0].title,'Test');recovered.close();
});
test('update xung đột không ghi skip; thiếu log sau commit được phục hồi bằng retry cùng update_id',async t=>{
 const x=await setup(t);await run(process.execPath,x.args);
 const conflict=[...x.args];conflict[conflict.indexOf('--title')+1]='Different';await assert.rejects(run(process.execPath,conflict));assert.equal(x.store.snapshot().version,1);assert.equal(fs.readFileSync(x.skip,'utf8').trim().split('\n').length,1);
 fs.unlinkSync(x.skip);const retry=JSON.parse((await run(process.execPath,x.args)).stdout);assert.equal(retry.replayed,true);assert.equal(retry.version,1);assert.equal(JSON.parse(fs.readFileSync(x.skip,'utf8')).event_type,'push_send_skipped');
});
test('log bị lock/hỏng hoặc sai mode bị từ chối trước update',async t=>{
 const x=await setup(t),log=openSkipLog(x.skip);try {await assert.rejects(run(process.execPath,x.args));assert.equal(x.store.snapshot().version,0);}finally{log.close();}
 fs.writeFileSync(x.skip,'bad json\n');await assert.rejects(run(process.execPath,x.args));assert.equal(x.store.snapshot().version,0);
 const wrong=[...x.args];wrong[wrong.indexOf('--mode')+1]='PUSH';await assert.rejects(run(process.execPath,wrong));assert.equal(x.store.snapshot().version,0);
});
test('HTTP không kết nối thì không tạo event skip, không fallback ghi store',async t=>{
 const x=await setup(t),args=[...x.args];args[args.indexOf('--base-url')+1]='http://127.0.0.1:1';await assert.rejects(run(process.execPath,args));assert.equal(x.store.snapshot().version,0);assert.equal(fs.readFileSync(x.skip,'utf8'),'');
});
