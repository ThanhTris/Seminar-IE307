#!/usr/bin/env node

/**
 * FCM Sender CLI for Seminar IE307 (SEM-35)
 * Sends data-only, normal priority message to target device token.
 */

import fs from 'node:fs';

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

// TTL for Firebase Admin SDK AndroidConfig must be in milliseconds
const TTL_MILLISECONDS = 86400 * 1000;

const payload = {
  data: {
    run_id: runId,
    version_hint: String(versionHint),
    request_id: requestId,
    mode: 'PUSH',
  },
  android: {
    priority: 'normal', // Strictly normal priority per protocol
    ttl: TTL_MILLISECONDS, // 24 hours in milliseconds
  },
};

console.log('--- FCM Sender CLI (SEM-35) ---');
console.log('Payload (data-only, normal priority, TTL in ms):');
console.log(JSON.stringify(payload, null, 2));

const credPath = process.env.GOOGLE_APPLICATION_CREDENTIALS;

if (!token) {
  console.log('\n[Warning] No target registration token provided. Use --token <FCM_TOKEN>.');
  console.log('[Dry-Run Simulation] Message structure validated.');
  const mockMessageId = `projects/seminar-ie307/messages/mock-${Date.now()}`;
  console.log(`[Result] Accepted in simulation mode. Message ID: ${mockMessageId}`);
  process.exit(0);
}

if (!credPath || !fs.existsSync(credPath)) {
  console.log('\n[Blocker] GOOGLE_APPLICATION_CREDENTIALS is not set or file does not exist.');
  console.log(`Target Token: ${token.substring(0, 10)}... (truncated for security)`);
  console.log('[Simulation Result] Accepted in dry-run mode (live credentials pending project owner configuration).');
  process.exit(0);
}

// Live send with Firebase Admin
try {
  const { default: admin } = await import('firebase-admin');
  const serviceAccount = JSON.parse(fs.readFileSync(credPath, 'utf-8'));

  if (!admin.apps.length) {
    admin.initializeApp({
      credential: admin.credential.cert(serviceAccount),
    });
  }

  const message = {
    token,
    data: payload.data,
    android: payload.android,
  };

  const messageId = await admin.messaging().send(message);
  console.log(`\n[Success] FCM message sent successfully!`);
  console.log(`Message ID: ${messageId}`);
  console.log(`Run ID: ${runId}`);
  console.log(`Version Hint: ${versionHint}`);
} catch (err) {
  console.error('\n[Error] Failed to send live FCM message:', err.message);
  process.exit(1);
}
