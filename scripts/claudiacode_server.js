const express = require('express');
const compression = require('compression');
const cors = require('cors');
const path = require('path');
const fs = require('fs');
const Database = require('better-sqlite3');

const app = express();
const PORT = process.env.PORT || 3021;
const DB_PATH = path.join(__dirname, 'claudiacode_users.db');

// SQLite WAL Database initialization
const db = new Database(DB_PATH);
db.pragma('journal_mode = WAL');

db.exec(`
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    name TEXT,
    plan TEXT DEFAULT 'Apex Free',
    downloads_count INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );
  CREATE TABLE IF NOT EXISTS downloads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    os_type TEXT,
    ip_address TEXT,
    downloaded_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );
`);

app.use(compression());
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Serve custom register / login page
app.get('/login', (req, res) => {
  res.sendFile(path.join(__dirname, 'claudiacode_login.html'));
});
app.get('/register', (req, res) => {
  res.sendFile(path.join(__dirname, 'claudiacode_login.html'));
});
app.get('/oauth', (req, res) => {
  res.sendFile(path.join(__dirname, 'claudiacode_login.html'));
});

// API: Register User (Gating)
app.post('/api/register', (req, res) => {
  try {
    const { name, username, email, password, os_type } = req.body;
    if (!username || !email || !password) {
      return res.status(400).json({ error: 'Username, email, and password are required.' });
    }

    const cleanUser = username.trim().toLowerCase();
    const cleanEmail = email.trim().toLowerCase();

    const checkStmt = db.prepare('SELECT id FROM users WHERE username = ? OR email = ?');
    const existing = checkStmt.get(cleanUser, cleanEmail);
    if (existing) {
      return res.status(400).json({ error: 'Username or email already registered. Please sign in.' });
    }

    const insertStmt = db.prepare(`
      INSERT INTO users (name, username, email, password_hash, plan)
      VALUES (?, ?, ?, ?, 'Apex Master')
    `);
    const info = insertStmt.run(name || cleanUser, cleanUser, cleanEmail, password);

    // Record download / gating activity
    const dlStmt = db.prepare('INSERT INTO downloads (user_id, os_type, ip_address) VALUES (?, ?, ?)');
    dlStmt.run(info.lastInsertRowid, os_type || 'windows', req.ip || '127.0.0.1');

    const sessionId = 'session_' + Buffer.from(`${cleanUser}:${Date.now()}`).toString('hex');
    res.json({
      success: true,
      message: 'Account created successfully!',
      user: { id: info.lastInsertRowid, username: cleanUser, email: cleanEmail, plan: 'Apex Master' },
      sessionId
    });
  } catch (err) {
    res.status(500).json({ error: 'Database error: ' + err.message });
  }
});

// API: Login User
app.post('/api/login', (req, res) => {
  try {
    const { identifier, password } = req.body;
    if (!identifier || !password) {
      return res.status(400).json({ error: 'Username/email and password are required.' });
    }

    const cleanId = identifier.trim().toLowerCase();
    const stmt = db.prepare('SELECT * FROM users WHERE (username = ? OR email = ?) AND password_hash = ?');
    const user = stmt.get(cleanId, cleanId, password);

    if (!user) {
      return res.status(401).json({ error: 'Invalid credentials. Check your username/password.' });
    }

    db.prepare('UPDATE users SET last_login_at = CURRENT_TIMESTAMP WHERE id = ?').run(user.id);

    const sessionId = 'session_' + Buffer.from(`${user.username}:${Date.now()}`).toString('hex');
    res.json({
      success: true,
      user: { id: user.id, username: user.username, email: user.email, plan: user.plan || 'Apex Master' },
      sessionId
    });
  } catch (err) {
    res.status(500).json({ error: 'Database error: ' + err.message });
  }
});

// API: Realtime User Stats
app.get('/api/stats', (req, res) => {
  try {
    const totalUsers = db.prepare('SELECT COUNT(*) as count FROM users').get().count;
    const totalDownloads = db.prepare('SELECT COUNT(*) as count FROM downloads').get().count;
    const recentUsers = db.prepare('SELECT id, username, email, plan, created_at FROM users ORDER BY id DESC LIMIT 10').all();
    res.json({
      totalUsers,
      totalDownloads,
      recentUsers
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// API: Status
app.get('/api/status', (req, res) => {
  res.json({
    status: 'online',
    app: 'Claudia Code Official Gateway',
    version: '5.0.0 Apex',
    engine: 'Claudia Ultra Quantum Apex',
    oauthPortal: 'https://claudiacode.zolu.my.id/login',
    installWindows: 'irm https://get.zolu.my.id/win | iex',
    installUnix: 'curl -fsSL https://get.zolu.my.id | bash',
    repository: 'https://github.com/mhanafi09051998/claudia-code'
  });
});

app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'claudiacode_login.html'));
});

app.listen(PORT, '0.0.0.0', () => {
  console.log('[CLAUDIA CODE WEB] Centralized Database & Gating Portal running on http://0.0.0.0:' + PORT);
});
