const http = require('http');
const https = require('https');

const TARGET_HOST = '9router.zolu.my.id';
const PORT = 8045;

const server = http.createServer((req, res) => {
  let targetPath = req.url;

  // Route all incoming model requests to 9router target: ag/gemini-3.8-flash-high
  targetPath = targetPath.replace(/\/models\/[^:?]+/, '/models/ag/gemini-3.8-flash-high');

  let apiKey = req.headers['x-goog-api-key'] || process.env.GEMINI_API_KEY;
  if (!apiKey || !apiKey.startsWith('sk-')) {
    apiKey = process.env.GEMINI_API_KEY || '';
  }

  const headers = {
    ...req.headers,
    host: TARGET_HOST,
    'authorization': `Bearer ${apiKey}`,
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AntigravityClient/1.1'
  };

  delete headers['x-goog-api-key'];

  const proxyReq = https.request({
    hostname: TARGET_HOST,
    port: 443,
    path: targetPath,
    method: req.method,
    headers: headers
  }, (proxyRes) => {
    console.log(`[9router-proxy] ${req.method} ${targetPath} => ${proxyRes.statusCode}`);
    res.writeHead(proxyRes.statusCode, proxyRes.headers);
    proxyRes.pipe(res);
  });

  proxyReq.on('error', (err) => {
    console.error(`[9router-proxy] Request error: ${err.message}`);
    res.writeHead(502, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: { message: err.message, code: 502 } }));
  });

  req.pipe(proxyReq);
});

server.listen(PORT, '127.0.0.1', () => {
  console.log(`[9router-proxy] Listening on http://127.0.0.1:${PORT} -> https://${TARGET_HOST}`);
});
