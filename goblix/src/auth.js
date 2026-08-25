// ===================================================================
// GOBLIX AUTHENTICATION MODULE (auth.js)
// Token Generation, Verification & User Persistence
// Max ~85 lines • Standard Crypto Library
// ===================================================================

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const USERS_FILE = path.join(__dirname, '..', 'data', 'users.json');
const SECRET_KEY = '***GOBLIX_SECRET_REMOVED***';

function getUsersDB() {
  try {
    if (!fs.existsSync(USERS_FILE)) return [];
    return JSON.parse(fs.readFileSync(USERS_FILE, 'utf8') || '[]');
  } catch (e) {
    return [];
  }
}

function saveUsersDB(users) {
  try {
    const dir = path.dirname(USERS_FILE);
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(USERS_FILE, JSON.stringify(users, null, 2), 'utf8');
  } catch (e) {
    console.error('[AUTH ERROR] Failed to save users:', e);
  }
}

function hashPassword(password) {
  return crypto.createHmac('sha256', SECRET_KEY).update(password).digest('hex');
}

function generateToken(user) {
  const payload = {
    id: user.id,
    email: user.email,
    name: user.name,
    exp: Date.now() + (7 * 24 * 60 * 60 * 1000)
  };
  const str = Buffer.from(JSON.stringify(payload)).toString('base64url');
  const signature = crypto.createHmac('sha256', SECRET_KEY).update(str).digest('base64url');
  return `${str}.${signature}`;
}

function verifyToken(token) {
  if (!token || typeof token !== 'string') return null;
  const parts = token.split('.');
  if (parts.length !== 2) return null;
  const [str, sig] = parts;
  const expectedSig = crypto.createHmac('sha256', SECRET_KEY).update(str).digest('base64url');
  if (sig !== expectedSig) return null;
  try {
    const payload = JSON.parse(Buffer.from(str, 'base64url').toString('utf8'));
    if (payload.exp && Date.now() > payload.exp) return null;
    return payload;
  } catch (e) {
    return null;
  }
}

function getAuthUser(req) {
  const authHeader = req.headers['authorization'];
  if (!authHeader || !authHeader.startsWith('Bearer ')) return null;
  const token = authHeader.split(' ')[1];
  return verifyToken(token);
}

module.exports = {
  getUsersDB,
  saveUsersDB,
  hashPassword,
  generateToken,
  verifyToken,
  getAuthUser
};
