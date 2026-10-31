import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { SnapshotStore } from '../src/snapshot_store.js';
import { createServer } from '../src/server.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const TEST_DATA_FILE = path.join(__dirname, 'test_snapshot.json');

test.beforeEach(() => {
  if (fs.existsSync(TEST_DATA_FILE)) {
    fs.unlinkSync(TEST_DATA_FILE);
  }
});

test.afterEach(() => {
  if (fs.existsSync(TEST_DATA_FILE)) {
    fs.unlinkSync(TEST_DATA_FILE);
  }
});

test('SnapshotStore starts at initial version and increments monotonically', () => {
  const store = new SnapshotStore(TEST_DATA_FILE);
  const initial = store.getSnapshot();
  assert.equal(initial.version, 1);
  assert.equal(initial.items.length, 1);

  const updated1 = store.updateSnapshot({ title: 'New 1', body: 'Body 1' });
  assert.equal(updated1.version, 2);
  assert.equal(updated1.items.length, 2);
  assert.equal(updated1.items[0].title, 'New 1');

  // Re-read from disk
  const reloaded = store.getSnapshot();
  assert.equal(reloaded.version, 2);
});

test('Server returns health status 200', async () => {
  const store = new SnapshotStore(TEST_DATA_FILE);
  const server = createServer(store);

  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const port = server.address().port;

  try {
    const res = await fetch(`http://127.0.0.1:${port}/health`);
    assert.equal(res.status, 200);
    const data = await res.json();
    assert.equal(data.status, 'ok');
    assert.ok(data.uptime_seconds >= 0);
  } finally {
    server.close();
  }
});

test('Server returns 200 on new snapshot and 304 on If-None-Match', async () => {
  const store = new SnapshotStore(TEST_DATA_FILE);
  const server = createServer(store);

  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const port = server.address().port;

  try {
    // 1. Initial fetch
    const res1 = await fetch(`http://127.0.0.1:${port}/api/bulletin`, {
      headers: { 'X-Correlation-Request-Id': 'req-test-1' }
    });
    assert.equal(res1.status, 200);
    assert.equal(res1.headers.get('etag'), '"v1"');
    assert.equal(res1.headers.get('x-correlation-request-id'), 'req-test-1');
    const data1 = await res1.json();
    assert.equal(data1.version, 1);

    // 2. Fetch with matching If-None-Match
    const res2 = await fetch(`http://127.0.0.1:${port}/api/bulletin`, {
      headers: { 'If-None-Match': '"v1"' }
    });
    assert.equal(res2.status, 304);

    // 3. Post update
    const resUpdate = await fetch(`http://127.0.0.1:${port}/api/bulletin/update`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: 'Test 2', body: 'Content 2' }),
    });
    assert.equal(resUpdate.status, 200);
    const updated = await resUpdate.json();
    assert.equal(updated.version, 2);

    // 4. Fetch with old If-None-Match -> gets 200 with new version
    const res3 = await fetch(`http://127.0.0.1:${port}/api/bulletin`, {
      headers: { 'If-None-Match': '"v1"' }
    });
    assert.equal(res3.status, 200);
    const data3 = await res3.json();
    assert.equal(data3.version, 2);
  } finally {
    server.close();
  }
});
