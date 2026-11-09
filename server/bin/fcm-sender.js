#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import {validInput,payload,execute,appendEvent,verifyCommit,prepareFirebase} from '../src/fcm_sender.js';
const names={'--run':'run_id','--mode':'mode','--device':'device_alias','--update-id':'update_id','--signal-id':'signal_id','--version':'version','--ttl-ms':'ttl_ms','--base-url':'baseUrl','--server-events':'serverEvents','--events':'events','--token-file':'tokenFile'};
const flags=new Set(['--send','--validate-only']);const args=process.argv.slice(2), raw={};let choice=null;
for(let i=0;i<args.length;i++) {
 if(flags.has(args[i])){if(choice){console.error('INVALID_ARGUMENT');process.exit(2);}choice=args[i];continue;}
 const key=names[args[i]];if(!key || Object.hasOwn(raw,key) || i+1>=args.length || args[i+1].startsWith('--')){console.error('INVALID_ARGUMENT');process.exit(2);}raw[key]=args[++i];
}
const number=s=>typeof s==='string' && /^(0|[1-9]\d*)$/.test(s) ? Number(s):NaN;
const o={run_id:raw.run_id,mode:raw.mode,device_alias:raw.device_alias,update_id:raw.update_id,signal_id:raw.signal_id,version:number(raw.version),ttl_ms:raw.ttl_ms===undefined?86400000:number(raw.ttl_ms)};
if(!choice || !validInput(o)){console.error('INVALID_ARGUMENT: thiếu hoặc sai tham số; xem docs/setup/FCM_SENDER.md');process.exit(2);}
if(choice==='--validate-only') {const msg=payload(o,'<TOKEN_NOT_SENT>');delete msg.token;console.log(JSON.stringify({status:'validated_locally',message:msg}));process.exit(0);}
const baseUrl=raw.baseUrl??process.env.SERVER_URL??'http://127.0.0.1:3000';
const serverEvents=path.resolve(raw.serverEvents??path.join(process.env.STORE_DIR??'./.local/server','events.jsonl'));
const output=path.resolve(raw.events??'./.local/fcm-sender/events.jsonl');
try {
 const u=new URL(baseUrl);const resolved=p=>fs.existsSync(p)?fs.realpathSync(p):p;
 if(!['http:','https:'].includes(u.protocol) || [serverEvents,path.join(path.dirname(serverEvents),'state.json')].some(p=>resolved(output)===resolved(p)))throw Error();
 // Probe the output before a send so missing permissions do not trigger FCM.
 fs.mkdirSync(path.dirname(output),{recursive:true});const fd=fs.openSync(output,'a',0o600);fs.closeSync(fd);
 const result=await execute(o,{
  verify:()=>verifyCommit(o,{serverEvents,baseUrl}),
  prepare:()=>prepareFirebase({tokenFile:raw.tokenFile??process.env.FCM_TOKEN_FILE,projectId:process.env.FIREBASE_PROJECT_ID,credentialPath:process.env.GOOGLE_APPLICATION_CREDENTIALS}),
  write:e=>appendEvent(output,e)
 });
 console.log(JSON.stringify({status:result.status,signal_id:o.signal_id,send_attempt_id:result.event?.send_attempt_id??null}));
 if(result.status!=='accepted')process.exitCode=1;
} catch {console.error('LOCAL_LOG_OR_CONFIG_ERROR: không xác nhận kết quả; kiểm tra log riêng trước khi retry.');process.exitCode=1;}
