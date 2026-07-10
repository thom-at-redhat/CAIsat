// Assisted by: cursor, claude
// Local stub APIs for Playwright MT-R3a (enhance :8080, detection :8081).

import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import Busboy from 'busboy';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const FRONTEND_ORIGIN = 'http://localhost:3000';
const POST_DELAY_MS = 200;

const ENHANCE_PREVIEW_PATH = path.join(__dirname, 'e2e-fixtures', 'enhance-preview.jpg');
const ENHANCE_PREVIEW_B64 = fs.readFileSync(ENHANCE_PREVIEW_PATH).toString('base64');

const ENHANCE_ROUTES = {
  '/health': { status: 'healthy' },
  '/api/capabilities': {
    default_crop: 256,
    max_crop: 256,
    scale_factor: 4,
    gpu_exclusive: false,
    gpu_tier: 'cpu',
    tiling_enabled: false,
    infer_timeout_seconds: 300,
  },
  '/api/stats': { total_enhancements: 0 },
};

const DETECTION_ROUTES = {
  '/health': { status: 'healthy', gpu_exclusive: false },
};

const ENHANCE_POST_BODY = {
  preview: ENHANCE_PREVIEW_B64,
  media_type: 'image/jpeg',
  width: 1024,
  height: 1024,
  preview_width: 512,
  preview_height: 512,
};

const DETECTION_POST_BODY = {
  detections: [{ class: 'ship', confidence: 0.9, box: [10, 10, 200, 200] }],
  count: 1,
  image_size: { width: 1024, height: 1024 },
  sahi_slices: 1,
};

function corsHeaders() {
  return {
    'Access-Control-Allow-Origin': FRONTEND_ORIGIN,
    'Access-Control-Allow-Credentials': 'true',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
  };
}

function sendJson(res, statusCode, body) {
  const payload = JSON.stringify(body);
  res.writeHead(statusCode, {
    'Content-Type': 'application/json',
    ...corsHeaders(),
  });
  res.end(payload);
}

function handleOptions(res) {
  res.writeHead(204, corsHeaders());
  res.end();
}

function parseMultipart(req) {
  return new Promise((resolve, reject) => {
    const busboy = Busboy({ headers: req.headers });
    busboy.on('finish', () => resolve());
    busboy.on('error', reject);
    req.pipe(busboy);
  });
}

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function createServer({ port, name, getRoutes, postBody }) {
  const server = http.createServer(async (req, res) => {
    const url = req.url?.split('?')[0] ?? '/';

    if (req.method === 'OPTIONS') {
      handleOptions(res);
      return;
    }

    if (req.method === 'GET') {
      const routes = getRoutes();
      if (routes[url]) {
        sendJson(res, 200, routes[url]);
        return;
      }
      sendJson(res, 404, { error: 'not found' });
      return;
    }

    if (req.method === 'POST') {
      try {
        await parseMultipart(req);
        await delay(POST_DELAY_MS);
        sendJson(res, 200, postBody);
      } catch (error) {
        sendJson(res, 400, { error: error.message });
      }
      return;
    }

    sendJson(res, 405, { error: 'method not allowed' });
  });

  server.listen(port, () => {
    console.log(`${name} stub listening on http://localhost:${port}`);
  });

  return server;
}

createServer({
  port: 8080,
  name: 'Enhance',
  getRoutes: () => ENHANCE_ROUTES,
  postBody: ENHANCE_POST_BODY,
});

createServer({
  port: 8081,
  name: 'Detection',
  getRoutes: () => DETECTION_ROUTES,
  postBody: DETECTION_POST_BODY,
});
