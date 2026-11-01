#!/usr/bin/env node

import http from 'node:http';
import { defaultStore } from '../src/snapshot_store.js';

const args = process.argv.slice(2);
let title = null;
let body = null;
let runId = null;

for (let i = 0; i < args.length; i++) {
  if (args[i] === '--title' || args[i] === '-t') {
    title = args[++i];
  } else if (args[i] === '--body' || args[i] === '-b') {
    body = args[++i];
  } else if (args[i] === '--run' || args[i] === '-r') {
    runId = args[++i];
  } else if (!title) {
    title = args[i];
  } else if (!body) {
    body = args[i];
  }
}

const current = defaultStore.getSnapshot();
const targetVersion = Number(current.version || 0) + 1;

title = title || `Bản tin v${targetVersion} [Cập nhật tự động]`;
body = body || `Nội dung phát hành lúc ${new Date().toISOString()} cho thử nghiệm đồng bộ.`;
runId = runId || `cli-run-${Date.now()}`;

// Try sending via HTTP first if server is running
const postData = JSON.stringify({ title, body, run_id: runId });

const req = http.request({
  hostname: '127.0.0.1',
  port: process.env.PORT || 3000,
  path: '/api/bulletin/update',
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Content-Length': Buffer.byteLength(postData),
  },
  timeout: 1000,
}, (res) => {
  let responseData = '';
  res.on('data', chunk => { responseData += chunk; });
  res.on('end', () => {
    try {
      const json = JSON.parse(responseData);
      console.log(`[Success via HTTP] Snapshot updated to version v${json.version}`);
      console.log(`Title: ${title}`);
      console.log(`Total items: ${json.items.length}`);
    } catch {
      console.log(`[Success via HTTP] HTTP status: ${res.statusCode}`);
    }
  });
});

req.on('error', (err) => {
  // If server is not running on port 3000, update store directly on disk
  console.log(`(Server HTTP port 3000 not reachable: updating snapshot file directly...)`);
  const updated = defaultStore.updateSnapshot({ title, body, runId });
  console.log(`[Success via Disk] Snapshot updated to version v${updated.version}`);
  console.log(`Title: ${title}`);
  console.log(`Total items: ${updated.items.length}`);
});

req.write(postData);
req.end();
