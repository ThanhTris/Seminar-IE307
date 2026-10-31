import http from 'node:http';
import { URL } from 'node:url';
import { defaultStore } from './snapshot_store.js';

const PORT = process.env.PORT ? parseInt(process.env.PORT, 10) : 3000;
const HOST = process.env.HOST || '0.0.0.0';
const startTime = Date.now();

function parseJsonBody(req) {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', chunk => {
      body += chunk;
      if (body.length > 1e6) { // 1MB limit
        reject(new Error('Payload too large'));
      }
    });
    req.on('end', () => {
      if (!body.trim()) return resolve({});
      try {
        resolve(JSON.parse(body));
      } catch (err) {
        reject(new Error('Invalid JSON'));
      }
    });
    req.on('error', reject);
  });
}

function sendJson(res, statusCode, data, headers = {}) {
  const json = JSON.stringify(data);
  res.writeHead(statusCode, {
    'Content-Type': 'application/json; charset=utf-8',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, If-None-Match, X-Correlation-Request-Id',
    ...headers,
  });
  res.end(json);
}

export function createServer(store = defaultStore) {
  return http.createServer(async (req, res) => {
    const parsedUrl = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
    const pathname = parsedUrl.pathname;
    const method = req.method;
    const reqId = req.headers['x-correlation-request-id'] || null;

    // Handle CORS preflight
    if (method === 'OPTIONS') {
      res.writeHead(204, {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, If-None-Match, X-Correlation-Request-Id',
      });
      return res.end();
    }

    const commonHeaders = {};
    if (reqId) {
      commonHeaders['X-Correlation-Request-Id'] = reqId;
    }

    try {
      // 1. Health check
      if (method === 'GET' && pathname === '/health') {
        const uptime = (Date.now() - startTime) / 1000;
        return sendJson(res, 200, {
          status: 'ok',
          uptime_seconds: uptime,
          server_time_utc: new Date().toISOString(),
        }, commonHeaders);
      }

      // 2. GET Bulletin snapshot
      if (method === 'GET' && pathname === '/api/bulletin') {
        const snapshot = store.getSnapshot();
        const currentVersion = Number(snapshot.version);
        const ifNoneMatch = req.headers['if-none-match'];
        const sinceVersionParam = parsedUrl.searchParams.get('since_version');

        const clientVersion = ifNoneMatch
          ? parseInt(ifNoneMatch.replace(/^"v?|"$/g, ''), 10)
          : (sinceVersionParam ? parseInt(sinceVersionParam, 10) : null);

        commonHeaders['ETag'] = `"v${currentVersion}"`;

        if (clientVersion !== null && !isNaN(clientVersion) && clientVersion >= currentVersion) {
          res.writeHead(304, {
            'Access-Control-Allow-Origin': '*',
            ...commonHeaders,
          });
          return res.end();
        }

        return sendJson(res, 200, snapshot, commonHeaders);
      }

      // 3. POST Bulletin update
      if (method === 'POST' && pathname === '/api/bulletin/update') {
        const body = await parseJsonBody(req);
        const updated = store.updateSnapshot({
          title: body.title,
          body: body.body,
          runId: body.run_id,
        });

        console.log(`[Update] Version bumped to v${updated.version}: ${body.title || 'Untitled'}`);
        commonHeaders['ETag'] = `"v${updated.version}"`;
        return sendJson(res, 200, updated, commonHeaders);
      }

      // 4. 404 Not Found
      return sendJson(res, 404, {
        error: {
          code: 'NOT_FOUND',
          message: `Endpoint ${method} ${pathname} not found.`,
        },
      }, commonHeaders);

    } catch (err) {
      console.error('[Server Error]', err);
      return sendJson(res, 500, {
        error: {
          code: 'INTERNAL',
          message: err.message || 'Internal server error',
        },
      }, commonHeaders);
    }
  });
}

// Auto-start when executed directly
if (process.argv[1] && process.argv[1].endsWith('server.js')) {
  const server = createServer();
  server.listen(PORT, HOST, () => {
    console.log(`===============================================`);
    console.log(` Seminar IE307 Snapshot Server running on:`);
    console.log(` - Local:    http://127.0.0.1:${PORT}`);
    console.log(` - Emulator: http://10.0.2.2:${PORT}`);
    console.log(`===============================================`);
  });
}
