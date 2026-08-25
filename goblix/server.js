// ===================================================================
// GOBLIX AUTONOMOUS PRODUCTION BACKEND (server.js)
// Modular Micro-Kernel Architecture • Zero Framework Bloat
// Clean Architecture: streamer.js, auth.js, subtitles.js
// ===================================================================

const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');

const { streamVideoFile } = require('./src/streamer');
const { getUsersDB, saveUsersDB, hashPassword, generateToken, getAuthUser } = require('./src/auth');
const { serveSanitizedSubtitle } = require('./src/subtitles');

const PORT = process.env.PORT || 3070;
const PUBLIC_DIR = path.join(__dirname, 'public');
const MOVIES_FILE = path.join(__dirname, 'data', 'movies.json');

const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif': 'image/gif',
  '.svg': 'image/svg+xml',
  '.vtt': 'text/vtt; charset=utf-8',
  '.mp4': 'video/mp4',
  '.mkv': 'video/x-matroska'
};

function getMoviesDB() {
  try {
    if (!fs.existsSync(MOVIES_FILE)) return [];
    return JSON.parse(fs.readFileSync(MOVIES_FILE, 'utf8') || '[]');
  } catch (e) {
    return [];
  }
}

function parseJSONBody(req) {
  return new Promise((resolve) => {
    let body = '';
    req.on('data', chunk => { body += chunk.toString(); });
    req.on('end', () => {
      try { resolve(JSON.parse(body || '{}')); }
      catch (e) { resolve({}); }
    });
  });
}

const server = http.createServer(async (req, res) => {
  const parsedUrl = url.parse(req.url, true);
  const pathname = parsedUrl.pathname;

  // CORS Headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization, Range');
  res.setHeader('X-Content-Type-Options', 'nosniff');

  if (req.method === 'OPTIONS') {
    res.writeHead(204);
    res.end();
    return;
  }

  // 1. VIDEO STREAMING ENDPOINT (HTTP 206 Byte Range)
  if (pathname.startsWith('/stream/')) {
    const videoFileName = pathname.replace('/stream/', '');
    const videoFilePath = path.join(PUBLIC_DIR, 'stream', videoFileName);
    const contentType = videoFileName.endsWith('.mkv') ? 'video/x-matroska' : 'video/mp4';
    streamVideoFile(req, res, videoFilePath, contentType);
    return;
  }

  // 2. SUBTITLES ENDPOINT (Sanitized Anti-Judi/Anti-Promo)
  if (pathname.startsWith('/api/subtitles/') || pathname.startsWith('/subtitles/') || pathname === '/sub_indo.vtt') {
    let subFileName = 'sub_indo.vtt';
    if (pathname.startsWith('/api/subtitles/')) {
      const slug = pathname.replace('/api/subtitles/', '');
      subFileName = `${slug}.vtt`;
    } else if (pathname.startsWith('/subtitles/')) {
      subFileName = pathname.replace('/subtitles/', '');
    }
    let subFile = path.join(PUBLIC_DIR, 'subtitles', subFileName);
    if (!fs.existsSync(subFile)) {
      subFile = path.join(PUBLIC_DIR, subFileName);
    }
    if (!fs.existsSync(subFile)) {
      subFile = path.join(PUBLIC_DIR, 'sub_indo.vtt');
    }
    serveSanitizedSubtitle(req, res, subFile);
    return;
  }

  // 3. MOVIES CATALOG API
  if (pathname === '/api/movies' && req.method === 'GET') {
    res.writeHead(200, { 'Content-Type': 'application/json', 'Cache-Control': 'no-cache' });
    res.end(JSON.stringify({ success: true, data: getMoviesDB() }));
    return;
  }

  if (pathname.startsWith('/api/movies/') && req.method === 'GET') {
    const slug = pathname.replace('/api/movies/', '');
    const movie = getMoviesDB().find(m => m.slug === slug || m.id === slug);
    if (!movie) {
      res.writeHead(404, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ success: false, error: 'Film tidak ditemukan' }));
      return;
    }
    res.writeHead(200, { 'Content-Type': 'application/json', 'Cache-Control': 'no-cache' });
    res.end(JSON.stringify({ success: true, data: movie }));
    return;
  }

  // 4. WATCH PROGRESS API
  if (pathname === '/api/user/progress') {
    const authUser = getAuthUser(req);
    if (!authUser) {
      res.writeHead(401, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ success: false, error: 'Unauthorized' }));
      return;
    }

    const users = getUsersDB();
    const userIndex = users.findIndex(u => u.id === authUser.id);
    if (userIndex === -1) {
      res.writeHead(404, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ success: false, error: 'User tidak ditemukan' }));
      return;
    }

    if (req.method === 'GET') {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ success: true, progress: users[userIndex].watchProgress || {} }));
      return;
    }

    if (req.method === 'POST') {
      const body = await parseJSONBody(req);
      const { movieId, currentTime, duration } = body;
      if (!users[userIndex].watchProgress) users[userIndex].watchProgress = {};
      users[userIndex].watchProgress[movieId] = {
        movieId,
        currentTime: Math.floor(currentTime || 0),
        duration: Math.floor(duration || 0),
        percent: Math.min(100, Math.round((currentTime / (duration || 1)) * 100)),
        updatedAt: new Date().toISOString()
      };
      saveUsersDB(users);
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ success: true, progress: users[userIndex].watchProgress[movieId] }));
      return;
    }
  }

  // 5. AUTHENTICATION API
  if (pathname === '/api/auth/register' && req.method === 'POST') {
    const { name, email, password } = await parseJSONBody(req);
    if (!name || !email || !password || password.length < 6) {
      res.writeHead(400, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ success: false, error: 'Data pendaftaran tidak valid' }));
      return;
    }
    const users = getUsersDB();
    if (users.some(u => u.email.toLowerCase() === email.toLowerCase())) {
      res.writeHead(400, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ success: false, error: 'Email sudah terdaftar' }));
      return;
    }
    const newUser = {
      id: 'usr_' + Date.now() + Math.random().toString(36).substr(2, 4),
      name: name.trim(),
      email: email.toLowerCase().trim(),
      passwordHash: hashPassword(password),
      role: 'user',
      watchProgress: {},
      createdAt: new Date().toISOString()
    };
    users.push(newUser);
    saveUsersDB(users);
    const token = generateToken(newUser);
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ success: true, token, user: { id: newUser.id, name: newUser.name, email: newUser.email, role: newUser.role } }));
    return;
  }

  if (pathname === '/api/auth/login' && req.method === 'POST') {
    const { email, password } = await parseJSONBody(req);
    const users = getUsersDB();
    const user = users.find(u => u.email.toLowerCase() === (email || '').toLowerCase().trim());
    if (!user || user.passwordHash !== hashPassword(password)) {
      res.writeHead(401, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ success: false, error: 'Email atau kata sandi salah' }));
      return;
    }
    const token = generateToken(user);
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ success: true, token, user: { id: user.id, name: user.name, email: user.email, role: user.role } }));
    return;
  }

  if (pathname === '/api/auth/me' && req.method === 'GET') {
    const authUser = getAuthUser(req);
    if (!authUser) {
      res.writeHead(401, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ success: false, error: 'Unauthorized' }));
      return;
    }
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ success: true, user: authUser }));
    return;
  }

  // 6. STATIC FILE SERVING & SPA FALLBACK
  let safeSuffix = path.normalize(pathname).replace(/^(\.\.[\/\\])+/, '');
  let filePath = path.join(PUBLIC_DIR, safeSuffix);

  fs.stat(filePath, (err, stats) => {
    if (!err && stats.isFile()) {
      const ext = path.extname(filePath).toLowerCase();
      const contentType = MIME_TYPES[ext] || 'application/octet-stream';
      res.writeHead(200, { 'Content-Type': contentType });
      fs.createReadStream(filePath).pipe(res);
    } else {
      // SPA Fallback to index.html
      const indexPath = path.join(PUBLIC_DIR, 'index.html');
      fs.readFile(indexPath, (indexErr, data) => {
        if (indexErr) {
          res.writeHead(404, { 'Content-Type': 'text/plain' });
          res.end('404 Not Found');
          return;
        }
        res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
        res.end(data);
      });
    }
  });
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`[GOBLIX PRODUCTION] Server online di http://0.0.0.0:${PORT}`);
});
