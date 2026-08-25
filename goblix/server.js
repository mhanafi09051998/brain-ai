const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');
const crypto = require('crypto');

const PORT = process.env.PORT || 3016;
const JWT_SECRET = process.env.JWT_SECRET || 'goblix-secret-key-quantum-auth-2026';
const PUBLIC_DIR = path.join(__dirname, 'public');
const DATA_DIR = path.join(__dirname, 'data');
const MOVIES_FILE = path.join(DATA_DIR, 'movies.json');
const USERS_FILE = path.join(DATA_DIR, 'users.json');

// Ensure data directory exists
if (!fs.existsSync(DATA_DIR)) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
}

// -------------------------------------------------------------
// CRYPTO & JWT HELPERS (Zero-Dependency Production Grade)
// -------------------------------------------------------------
function hashPassword(password, salt = crypto.randomBytes(16).toString('hex')) {
  const hash = crypto.pbkdf2Sync(password, salt, 100000, 64, 'sha512').toString('hex');
  return { hash, salt };
}

function verifyPassword(password, hash, salt) {
  const verifyHash = crypto.pbkdf2Sync(password, salt, 100000, 64, 'sha512').toString('hex');
  return crypto.timingSafeEqual(Buffer.from(hash, 'hex'), Buffer.from(verifyHash, 'hex'));
}

function generateToken(payload) {
  const header = Buffer.from(JSON.stringify({ alg: 'HS256', typ: 'JWT' })).toString('base64url');
  const exp = Math.floor(Date.now() / 1000) + (60 * 60 * 24 * 7); // 7 Days
  const body = Buffer.from(JSON.stringify({ ...payload, exp })).toString('base64url');
  const signature = crypto.createHmac('sha256', JWT_SECRET).update(`${header}.${body}`).digest('base64url');
  return `${header}.${body}.${signature}`;
}

function verifyToken(token) {
  if (!token) return null;
  const parts = token.split('.');
  if (parts.length !== 3) return null;
  const [header, body, signature] = parts;
  const expectedSig = crypto.createHmac('sha256', JWT_SECRET).update(`${header}.${body}`).digest('base64url');
  if (signature !== expectedSig) return null;
  try {
    const decoded = JSON.parse(Buffer.from(body, 'base64url').toString());
    if (decoded.exp && decoded.exp < Math.floor(Date.now() / 1000)) return null;
    return decoded;
  } catch (e) {
    return null;
  }
}

// -------------------------------------------------------------
// DATABASE REPOSITORIES
// -------------------------------------------------------------
function getUsersDB() {
  try {
    if (fs.existsSync(USERS_FILE)) {
      return JSON.parse(fs.readFileSync(USERS_FILE, 'utf-8'));
    }
  } catch (e) {
    console.error("[DB ERROR] Failed to read users:", e);
  }
  const defaultAdmin = {
    id: "usr_admin",
    name: "Admin Goblix",
    email: "admin@goblix.com",
    role: "admin",
    createdAt: new Date().toISOString(),
    watchProgress: {},
    ...hashPassword("admin12345")
  };
  fs.writeFileSync(USERS_FILE, JSON.stringify([defaultAdmin], null, 2));
  return [defaultAdmin];
}

function saveUsersDB(users) {
  fs.writeFileSync(USERS_FILE, JSON.stringify(users, null, 2));
}

function getMoviesDB() {
  try {
    if (fs.existsSync(MOVIES_FILE)) {
      return JSON.parse(fs.readFileSync(MOVIES_FILE, 'utf-8'));
    }
  } catch (e) {
    console.error("[DB ERROR] Failed to read movies:", e);
  }
  return [];
}

function parseBody(req) {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', chunk => {
      body += chunk.toString();
      if (body.length > 1e6) req.connection.destroy();
    });
    req.on('end', () => {
      try {
        resolve(body ? JSON.parse(body) : {});
      } catch (err) {
        reject(err);
      }
    });
    req.on('error', reject);
  });
}

const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css',
  '.js': 'application/javascript',
  '.json': 'application/json',
  '.vtt': 'text/vtt; charset=utf-8',
  '.srt': 'text/plain; charset=utf-8',
  '.mp4': 'video/mp4',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
  '.webmanifest': 'application/manifest+json'
};

// -------------------------------------------------------------
// MAIN HTTP SERVER
// -------------------------------------------------------------
const server = http.createServer(async (req, res) => {
  const parsedUrl = url.parse(req.url, true);
  const pathname = parsedUrl.pathname;

  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization, Range');
  res.setHeader('X-Content-Type-Options', 'nosniff');

  if (req.method === 'OPTIONS') {
    res.writeHead(204);
    res.end();
    return;
  }

  const authHeader = req.headers['authorization'] || '';
  const token = authHeader.startsWith('Bearer ') ? authHeader.substring(7) : null;
  const user = verifyToken(token);

  // 1. REGISTER: POST /api/auth/register
  if (pathname === '/api/auth/register' && req.method === 'POST') {
    try {
      const { name, email, password } = await parseBody(req);
      if (!name || !email || !password) {
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ success: false, error: 'Semua kolom wajib diisi.' }));
        return;
      }

      if (password.length < 6) {
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ success: false, error: 'Password minimal 6 karakter.' }));
        return;
      }

      const users = getUsersDB();
      const existingUser = users.find(u => u.email.toLowerCase() === email.toLowerCase().trim());
      if (existingUser) {
        res.writeHead(409, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ success: false, error: 'Email sudah terdaftar. Silakan login.' }));
        return;
      }

      const { hash, salt } = hashPassword(password);
      const newUser = {
        id: "usr_" + Date.now().toString(36),
        name: name.trim(),
        email: email.toLowerCase().trim(),
        role: "member",
        createdAt: new Date().toISOString(),
        watchProgress: {},
        hash,
        salt
      };

      users.push(newUser);
      saveUsersDB(users);

      const authToken = generateToken({ id: newUser.id, email: newUser.email, name: newUser.name, role: newUser.role });

      res.writeHead(201, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({
        success: true,
        message: 'Registrasi berhasil.',
        token: authToken,
        user: { id: newUser.id, name: newUser.name, email: newUser.email, role: newUser.role }
      }));
      return;
    } catch (e) {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ success: false, error: 'Terjadi kesalahan pada server.' }));
      return;
    }
  }

  // 2. LOGIN: POST /api/auth/login
  if (pathname === '/api/auth/login' && req.method === 'POST') {
    try {
      const { email, password } = await parseBody(req);
      if (!email || !password) {
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ success: false, error: 'Email dan Password wajib diisi.' }));
        return;
      }

      const users = getUsersDB();
      const userFound = users.find(u => u.email.toLowerCase() === email.toLowerCase().trim());
      if (!userFound || !verifyPassword(password, userFound.hash, userFound.salt)) {
        res.writeHead(401, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ success: false, error: 'Email atau kata sandi salah.' }));
        return;
      }

      const authToken = generateToken({ id: userFound.id, email: userFound.email, name: userFound.name, role: userFound.role });

      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({
        success: true,
        message: 'Login berhasil.',
        token: authToken,
        user: { id: userFound.id, name: userFound.name, email: userFound.email, role: userFound.role }
      }));
      return;
    } catch (e) {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ success: false, error: 'Gagal memproses login.' }));
      return;
    }
  }

  // 3. ME: GET /api/auth/me
  if (pathname === '/api/auth/me' && req.method === 'GET') {
    if (!user) {
      res.writeHead(401, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ success: false, error: 'Sesi habis atau tidak valid.' }));
      return;
    }
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ success: true, user }));
    return;
  }

  // 4. WATCH PROGRESS: POST /api/user/progress
  if (pathname === '/api/user/progress' && req.method === 'POST') {
    if (!user) {
      res.writeHead(401, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ success: false, error: 'Unauthorized' }));
      return;
    }
    try {
      const { movieId, currentTime, duration } = await parseBody(req);
      const users = getUsersDB();
      const userIdx = users.findIndex(u => u.id === user.id);
      if (userIdx !== -1) {
        if (!users[userIdx].watchProgress) users[userIdx].watchProgress = {};
        users[userIdx].watchProgress[movieId] = {
          movieId,
          currentTime: Number(currentTime) || 0,
          duration: Number(duration) || 0,
          percent: Math.min(100, Math.round(((Number(currentTime) || 0) / (Number(duration) || 1)) * 100)),
          updatedAt: new Date().toISOString()
        };
        saveUsersDB(users);
      }
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ success: true }));
      return;
    } catch (e) {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ success: false, error: 'Gagal menyimpan progress' }));
      return;
    }
  }

  // 5. GET WATCH PROGRESS: GET /api/user/progress
  if (pathname === '/api/user/progress' && req.method === 'GET') {
    if (!user) {
      res.writeHead(401, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ success: false, error: 'Unauthorized' }));
      return;
    }
    const users = getUsersDB();
    const userFound = users.find(u => u.id === user.id);
    const progress = userFound && userFound.watchProgress ? userFound.watchProgress : {};
    res.writeHead(200, { 'Content-Type': 'application/json', 'Cache-Control': 'no-cache' });
    res.end(JSON.stringify({ success: true, progress }));
    return;
  }

  // 6. MOVIES API
  if (pathname === '/api/movies' && req.method === 'GET') {
    const movies = getMoviesDB();
    res.writeHead(200, { 'Content-Type': 'application/json', 'Cache-Control': 'no-cache' });
    res.end(JSON.stringify({ success: true, count: movies.length, data: movies }));
    return;
  }

  if (pathname.startsWith('/api/movies/') && req.method === 'GET') {
    const slug = pathname.replace('/api/movies/', '');
    const movies = getMoviesDB();
    const movie = movies.find(m => m.slug === slug || m.id === slug);
    if (!movie) {
      res.writeHead(404, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ success: false, error: 'Film tidak ditemukan' }));
      return;
    }
    res.writeHead(200, { 'Content-Type': 'application/json', 'Cache-Control': 'no-cache' });
    res.end(JSON.stringify({ success: true, data: movie }));
    return;
  }

  if (pathname.startsWith('/api/subtitles/')) {
    const subFile = path.join(PUBLIC_DIR, 'sub_indo.vtt');
    fs.readFile(subFile, (err, data) => {
      if (err) {
        res.writeHead(404, { 'Content-Type': 'text/plain' });
        res.end('Subtitle tidak ditemukan');
        return;
      }
      res.writeHead(200, {
        'Content-Type': 'text/vtt; charset=utf-8',
        'Content-Disposition': 'inline; filename="subtitle_indonesia.vtt"'
      });
      res.end(data);
    });
    return;
  }

  // 7. STATIC FILES WITH NO-CACHE FOR INSTANT UPDATES
  let reqPath = pathname === '/' ? '/index.html' : pathname;
  const filePath = path.join(PUBLIC_DIR, reqPath);

  fs.stat(filePath, (err, stats) => {
    if (!err && stats.isFile()) {
      const ext = path.extname(filePath).toLowerCase();
      const contentType = MIME_TYPES[ext] || 'application/octet-stream';
      res.writeHead(200, {
        'Content-Type': contentType,
        'Content-Length': stats.size,
        'Cache-Control': 'no-cache, no-store, must-revalidate'
      });
      fs.createReadStream(filePath).pipe(res);
    } else {
      const indexPath = path.join(PUBLIC_DIR, 'index.html');
      fs.readFile(indexPath, (errIndex, data) => {
        if (errIndex) {
          res.writeHead(404, { 'Content-Type': 'text/plain' });
          res.end('Goblix: 404 Not Found');
        } else {
          res.writeHead(200, {
            'Content-Type': 'text/html; charset=utf-8',
            'Cache-Control': 'no-cache, no-store, must-revalidate'
          });
          res.end(data);
        }
      });
    }
  });
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`[GOBLIX PRODUCTION FULLSTACK] Active on port ${PORT}`);
});
