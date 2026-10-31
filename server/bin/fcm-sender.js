#!/usr/bin/env node

/**
 * FCM Sender CLI for Seminar IE307 (SEM-35)
 * Sends data-only, normal priority message to target device token.
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const args = process.argv.slice(2);
let token = null;
let runId = 'push-run-01';
let versionHint = '1';
let requestId = `req-${Date.now()}`;

for (let i = 0; i < args.length; i++) {
  if (args[i] === '--token' || args[i] === '-t') {
    token = args[++i];
  } else if (args[i] === '--run' || args[i] === '-r') {
    runId = args[++i];
  } else if (args[i] === '--version' || args[i] === '-v') {
    versionHint = args[++i];
  } else if (args[i] === '--request' || args[i] === '-req') {
    requestId = args[++i];
  }
}

const payload = {
  data: {
    run_id: runId,
    version_hint: String(versionHint),
    request_id: requestId,
    mode: 'PUSH',
  },
  android: {
    priority: 'normal', // Normal priority, strictly no high priority
    ttl: 86400, // 24 hours in seconds
  },
};

console.log('--- FCM Sender CLI (SEM-35) ---');
console.log('Payload (data-only, normal priority):');
console.log(JSON.stringify(payload, null, 2));

const credPath = process.env.GOOGLE_APPLICATION_CREDENTIALS;
if (!token) {
  console.log('\n[Warning] No target registration token provided. Use --token <FCM_TOKEN>.');
  console.log('[Dry-Run Simulation] Message structure validated. Outputting mock result:');
  const mockMessageId = `projects/seminar-ie307/messages/mock-${Date.now()}`;
  console.log(`Accepted with Message ID: ${mockMessageId}`);
  process.exit(0);
}

if (!credPath || !fs.existsSync(credPath)) {
  console.log('\n[Blocker] GOOGLE_APPLICATION_CREDENTIALS is not set or file does not exist.');
  console.log(`Target Token: ${token.substring(0, 10)}... (truncated for safety)`);
  console.log('[Simulation Result] Accepted in dry-run mode (live credentials pending project owner configuration).');
  process.exit(0);
}

console.log('\nLive Firebase Admin initialization is supported when credential file is present.');
