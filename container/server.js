// Standalone Node.js server for running this site outside Netlify (e.g. in a
// Docker container on Beget). Serves the static site and reuses the exact
// same lead-handling logic from netlify/functions/send-lead.js — no
// duplicated business logic, no new dependencies.

const http = require('http');
const fs = require('fs');
const path = require('path');
const { handler } = require('../netlify/functions/send-lead.js');

const ROOT = path.join(__dirname, '..');
const PORT = process.env.PORT || 8080;

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css',
  '.js': 'application/javascript',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.webp': 'image/webp',
  '.ico': 'image/x-icon',
  '.woff2': 'font/woff2',
  '.xml': 'application/xml',
  '.txt': 'text/plain; charset=utf-8',
};

function serveStatic(req, res) {
  let urlPath = decodeURIComponent(req.url.split('?')[0]);
  if (urlPath === '/') urlPath = '/index.html';

  // clean-URL support, matching Netlify's default behaviour: /offer -> /offer.html
  if (!path.extname(urlPath)) {
    const htmlCandidate = path.join(ROOT, urlPath + '.html');
    if (fs.existsSync(htmlCandidate)) urlPath += '.html';
  }

  const filePath = path.normalize(path.join(ROOT, urlPath));
  if (!filePath.startsWith(ROOT)) {
    res.writeHead(403);
    res.end('Forbidden');
    return;
  }

  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
      res.end('Not found');
      return;
    }
    const ext = path.extname(filePath);
    res.writeHead(200, { 'Content-Type': MIME[ext] || 'application/octet-stream' });
    res.end(data);
  });
}

const server = http.createServer((req, res) => {
  if (req.url.startsWith('/.netlify/functions/send-lead') && req.method === 'POST') {
    let body = '';
    req.on('data', (chunk) => (body += chunk));
    req.on('end', async () => {
      try {
        const result = await handler({ httpMethod: 'POST', body });
        res.writeHead(result.statusCode, { 'Content-Type': 'text/plain; charset=utf-8' });
        res.end(result.body);
      } catch {
        res.writeHead(500, { 'Content-Type': 'text/plain; charset=utf-8' });
        res.end('Server error');
      }
    });
    return;
  }
  serveStatic(req, res);
});

server.listen(PORT, () => {
  console.log(`sergeynasyrow-site listening on :${PORT}`);
});
