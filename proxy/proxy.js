#!/usr/bin/env node
/**
 * GitCode Proxy Server for CANN Recipes Blog
 *
 * Why needed:
 *   web-api.gitcode.com sets Access-Control-Allow-Origin: https://gitcode.com,
 *   so a browser on any other origin (file://, localhost, etc.) is blocked.
 *   This proxy forwards the request server-side and re-serves the file content
 *   with permissive CORS headers.
 *
 * How to start:
 *   node proxy.js
 *
 * Then open index.html in any browser.
 */

const http  = require('http');
const https = require('https');

const PORT = 8081;

function fetchFile(repo, filePath, branch) {
  return new Promise((resolve, reject) => {
    const ns      = 'cann';
    const repoId  = `${ns}%2F${repo}`;
    const apiUrl  =
      `https://web-api.gitcode.com/api/v2/projects/${repoId}/repository/files` +
      `?repoId=${encodeURIComponent(repoId)}` +
      `&ref=${encodeURIComponent(branch)}` +
      `&file_path=${encodeURIComponent(filePath)}` +
      `&ref_replace_web=${encodeURIComponent(branch)}`;

    const req = https.request(apiUrl, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Origin':   'https://gitcode.com',
        'Referer':  `https://gitcode.com/${ns}/${repo}/blob/${branch}/${filePath}`,
      },
    }, res => {
      const chunks = [];
      res.on('data', c => chunks.push(c));
      res.on('end', () => {
        try {
          const json = JSON.parse(Buffer.concat(chunks).toString('utf-8'));
          if (!json.content) {
            return reject(new Error('No content field – response: ' +
              JSON.stringify(json).substring(0, 200)));
          }
          const buf  = Buffer.from(json.content, 'base64');
          const type = json.file_type || 'application/octet-stream';
          resolve({ buf, type });
        } catch (e) {
          reject(e);
        }
      });
    });
    req.on('error', reject);
    req.end();
  });
}

function fetchTree(repo, filePath, branch) {
  return new Promise((resolve, reject) => {
    const ns      = 'cann';
    const repoId  = `${ns}%2F${repo}`;
    const apiUrl  =
      `https://web-api.gitcode.com/api/v2/projects/${repoId}/repository/upper_files_tree` +
      `?repoId=${encodeURIComponent(repoId)}` +
      `&ref_name=${encodeURIComponent(branch)}` +
      `&file_path=${encodeURIComponent(filePath)}`;

    const req = https.request(apiUrl, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Origin':   'https://gitcode.com',
        'Referer':  `https://gitcode.com/${ns}/${repo}/tree/${branch}/${filePath}`,
      },
    }, res => {
      const chunks = [];
      res.on('data', c => chunks.push(c));
      res.on('end', () => {
        try {
          const json = JSON.parse(Buffer.concat(chunks).toString('utf-8'));
          // Normalize to [{name, type}] — handle array or wrapped response
          const raw = Array.isArray(json) ? json : (json.data || json.trees || json.items || []);
          const items = raw
            .map(item => ({
              name: item.name || item.fileName || item.file_name || '',
              type: item.type === 'blob' ? 'blob'
                  : item.type === 'tree' ? 'tree'
                  : (item.name || '').includes('.') ? 'blob' : 'tree',
            }))
            .filter(item => item.name);
          resolve(items);
        } catch (e) {
          reject(new Error('Tree parse error: ' + e.message));
        }
      });
    });
    req.on('error', reject);
    req.end();
  });
}

http.createServer(async (req, res) => {
  // Allow any local origin (file://, localhost, etc.)
  res.setHeader('Access-Control-Allow-Origin',  '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', '*');

  if (req.method === 'OPTIONS') {
    res.writeHead(204);
    res.end();
    return;
  }

  if (req.method !== 'GET') {
    res.writeHead(405, { 'Content-Type': 'text/plain' });
    res.end('Method Not Allowed');
    return;
  }

  const q = Object.fromEntries(new URL(req.url, 'http://localhost').searchParams);

  if (!q.repo || !q.path) {
    res.writeHead(400, { 'Content-Type': 'text/plain' });
    res.end('Missing required query params: repo, path\n' +
            'Example: /?repo=cann-recipes-infer&path=docs/models/deepseek-r1/deepseek_r1_decode_optimization.md&branch=master');
    return;
  }

  if (q.action === 'tree') {
    try {
      const items = await fetchTree(q.repo, q.path, q.branch || 'master');
      const json  = JSON.stringify(items);
      res.writeHead(200, {
        'Content-Type':   'application/json',
        'Content-Length': Buffer.byteLength(json),
      });
      res.end(json);
    } catch (err) {
      console.error('[proxy] tree error:', err.message);
      res.writeHead(502, { 'Content-Type': 'text/plain' });
      res.end('Tree fetch failed: ' + err.message);
    }
    return;
  }

  try {
    const { buf, type } = await fetchFile(q.repo, q.path, q.branch || 'master');
    res.writeHead(200, {
      'Content-Type':   type,
      'Content-Length': buf.length,
    });
    res.end(buf);
  } catch (err) {
    console.error('[proxy] error:', err.message);
    res.writeHead(502, { 'Content-Type': 'text/plain' });
    res.end('Upstream fetch failed: ' + err.message);
  }

}).listen(PORT, '127.0.0.1', () => {
  console.log(`\nGitCode Proxy running at http://localhost:${PORT}`);
  console.log('Open index.html in your browser.\n');
});
