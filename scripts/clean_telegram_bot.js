'use strict';

const https = require('https');
const fs = require('fs');
const path = require('path');
const { requestOtp } = require('./otpManager');
const { getUserByTelegramId, registerOrLinkUser, approveUser, rejectUser, loadUsers, saveUsers } = require('./userManager');

const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN || '***TELEGRAM_TOKEN_REMOVED***';
const ADMIN_CHAT_ID = '***CHAT_ID_REMOVED***';
const DATA_DIR = path.join(__dirname, '..', '..', 'data');
const WD_FILE = path.join(DATA_DIR, 'withdrawals.json');
const DLMM_STATE_FILE = path.join(DATA_DIR, 'dlmm_state.json');

const leanCommands = [
  { command: 'saldo', description: 'Cek saldo, modal & estimasi profit' },
  { command: 'deposit', description: 'Nomor BCA Virtual Account otomatis' },
  { command: 'status', description: 'Status posisi aktif & pool Meteora' },
  { command: 'panduan', description: 'Panduan lengkap: Jadi User, Topup, WD' },
  { command: 'password', description: 'Dapatkan kode OTP Login Web Portal' },
  { command: 'portal', description: 'Tautan resmi Web Portal Claudia Capital' },
  { command: 'daftar', description: 'Registrasi akun investor baru' },
  { command: 'help', description: 'Bantuan penggunaan & status akun' }
];

function setTelegramBotCommands() {
  if (!BOT_TOKEN) return;
  const scopes = [{ type: 'default' }, { type: 'all_private_chats' }, { type: 'all_group_chats' }, { type: 'all_chat_administrators' }];
  for (const scope of scopes) {
    const payload = JSON.stringify({ commands: leanCommands, scope });
    const req = https.request('https://api.telegram.org/bot' + BOT_TOKEN + '/setMyCommands', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(payload) },
      timeout: 5000
    }, () => {});
    req.on('error', () => {});
    req.write(payload);
    req.end();
  }
}

function sendTelegramAlert(text, customChatId = null) {
  const targetId = customChatId || ADMIN_CHAT_ID;
  if (!BOT_TOKEN || !targetId) return Promise.resolve(null);
  const payload = JSON.stringify({ chat_id: String(targetId), text: text, parse_mode: 'HTML', disable_web_page_preview: true });
  return new Promise((resolve) => {
    const req = https.request('https://api.telegram.org/bot' + BOT_TOKEN + '/sendMessage', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(payload) },
      timeout: 10000
    }, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        try {
          const parsed = JSON.parse(body);
          resolve(parsed.ok ? parsed.result : null);
        } catch (e) {
          resolve(null);
        }
      });
    });
    req.on('error', () => resolve(null));
    req.write(payload);
    req.end();
  });
}

function loadWithdrawals() {
  try { return fs.existsSync(WD_FILE) ? JSON.parse(fs.readFileSync(WD_FILE, 'utf8')) || [] : []; } catch (e) { return []; }
}
function saveWithdrawals(list) {
  try { fs.writeFileSync(WD_FILE, JSON.stringify(list, null, 2), 'utf8'); } catch (e) { console.error('TGBOT_ERROR:', e); }
}

async function handleOtpRequest(chatId) {
  const otpRes = requestOtp(chatId);
  if (!otpRes.success) return sendTelegramAlert(otpRes.message, chatId);

  const otpMsg = `🔐 <b>CLAUDIA CAPITAL • OTP LOGIN</b>\n───────────────\n` +
    `Password  : <code>${otpRes.otp}</code>\n` +
    `Investor  : <b>${otpRes.user.userName} (TG-${otpRes.user.telegramId})</b>\n` +
    `Masa Aktif: <b>120 Detik</b>\n───────────────\n` +
    `🌐 <b>https://sol.zolu.my.id</b>`;

  await sendTelegramAlert(otpMsg, chatId);
}

function getSaldoStatusMsg(chatId) {
  let dlmm = { totalUsd: 932.40, feeUsd: 0 };
  try {
    if (fs.existsSync(DLMM_STATE_FILE)) {
      dlmm = JSON.parse(fs.readFileSync(DLMM_STATE_FILE, 'utf8'));
    }
  } catch (e) {}

  const user = getUserByTelegramId(chatId);
  const name = user ? user.userName : 'Investor';
  const role = user ? user.role : 'USER';
  const rateIdr = 16250;
  const modalIdr = user && user.modalIdr ? user.modalIdr : 6543986;
  const totalIdr = Math.round((dlmm.totalUsd || 932) * rateIdr);

  return `📊 <b>PORTFOLIO STATUS • CLAUDIA DLMM</b>\n───────────────\n` +
    `👤 <b>Investor:</b> ${name} (${role})\n` +
    `💼 <b>Total Portfolio:</b> $${(dlmm.totalUsd || 932).toFixed(2)} (~Rp ${totalIdr.toLocaleString('id-ID')})\n` +
    `⚙️ <b>Active Strategy:</b> Symmetrical Core 80/20 (Spot)\n` +
    `📈 <b>Status Pool:</b> In Range 🟢 (Earning Fees)\n` +
    `───────────────\n` +
    `💳 <b>Deposit Baru:</b> Ketik <code>/deposit</code>\n` +
    `🌐 <b>Web Dashboard:</b> <b>https://sol.zolu.my.id</b>`;
}

let botUpdateOffset = 0;
function pollTelegram() {
  const req = https.request('https://api.telegram.org/bot' + BOT_TOKEN + '/getUpdates?offset=' + botUpdateOffset + '&timeout=10', (res) => {
    let data = '';
    res.on('data', chunk => data += chunk);
    res.on('end', async () => {
      try {
        const json = JSON.parse(data);
        if (json.ok && json.result) {
          for (const update of json.result) {
            botUpdateOffset = update.update_id + 1;
            const msgObj = update.message || update.edited_message || update.channel_post;
            if (!msgObj || !msgObj.text) continue;
            const text = msgObj.text.trim();
            const chatId = String(msgObj.chat.id);
            const parts = text.split(/\s+/);
            const cmd = parts[0].toLowerCase().split('@')[0];
            const args = parts.slice(1).join(' ').trim();
            const isAdmin = chatId === ADMIN_CHAT_ID;

            if (cmd === '/deposit' || cmd === '/topup') {
              const depMsg = `💳 <b>DEPOSIT VIRTUAL ACCOUNT (BCA)</b>\n───────────────\n` +
                `Silakan transfer nominal bebas (Min Rp 50.000) ke rekening VA berikut:\n\n` +
                `🏦 <b>Bank:</b> BCA Virtual Account\n` +
                `🔢 <b>No VA:</b> <code>1598284628342373</code>\n` +
                `👤 <b>Atas Nama:</b> Tokocrypto / Muhammad Hanafi\n` +
                `───────────────\n` +
                `⚡ <b>Otomatisasi Penuh:</b>\n` +
                `1. Uang masuk VA terdeteksi instan.\n` +
                `2. Sistem membeli USDT & otomatis transfer ke Phantom Wallet.\n` +
                `3. Mesin DLMM menyeimbangkan koin 50:50 & menginjeksi ke pool.`;
              await sendTelegramAlert(depMsg, chatId);
            } else if (cmd === '/saldo' || cmd === '/status' || cmd === '/balance') {
              const statusMsg = getSaldoStatusMsg(chatId);
              await sendTelegramAlert(statusMsg, chatId);
            } else if (cmd === '/daftar' || cmd === '/register') {
              const subParts = args.split(/\s+/);
              const waNumber = subParts.length > 1 ? subParts[subParts.length - 1] : '';
              const fullName = subParts.length > 1 ? subParts.slice(0, -1).join(' ') : args;
              if (!fullName || !waNumber || waNumber.length < 8) {
                await sendTelegramAlert(`⚠️ <b>FORMAT REGISTRASI</b>\n───────────────\nFormat: <code>/daftar &lt;Nama Lengkap&gt; &lt;No_WA&gt;</code>\nContoh: <code>/daftar Dimas Nugraha 081234567890</code>`, chatId);
                continue;
              }
              const regResult = registerOrLinkUser(chatId, fullName, waNumber);
              await sendTelegramAlert(regResult.message, chatId);
              if (regResult.success && regResult.isNew) {
                const adminAlert = `🔔 <b>PENDAFTARAN BARU</b>\n• Nama: ${regResult.user.userName}\n• WA: ${regResult.user.whatsapp}\n• ID: TG-${regResult.user.telegramId}\n\nSetujui: <code>/acc_user ${regResult.user.telegramId}</code>`;
                await sendTelegramAlert(adminAlert, ADMIN_CHAT_ID);
              }
            } else if (cmd === '/panduan' || cmd === '/guide') {
              const guideMsg = `📖 <b>PANDUAN PENGGUNA • CLAUDIA CAPITAL</b>\n───────────────\n1️⃣ <b>Deposit:</b> Ketik <code>/deposit</code> untuk melihat VA BCA.\n2️⃣ <b>Cek Saldo:</b> Ketik <code>/saldo</code> untuk memantau nilai portfolio.\n3️⃣ <b>Web Login:</b> Ketik <code>/password</code> untuk menerima OTP login ke <b>https://sol.zolu.my.id</b>.`;
              await sendTelegramAlert(guideMsg, chatId);
            } else if ((cmd === '/acc_user' || cmd === '/approve_user') && isAdmin) {
              const targetTid = args.replace('TG-', '').trim();
              const appRes = approveUser(targetTid);
              await sendTelegramAlert(appRes.message, ADMIN_CHAT_ID);
            } else if (cmd === '/password' || cmd === '/otp') {
              await handleOtpRequest(chatId);
            } else if (cmd === '/portal' || cmd === '/web' || cmd === '/login') {
              await sendTelegramAlert(`🌐 <b>CLAUDIA CAPITAL PORTAL</b>\n───────────────\n🔗 <b>https://sol.zolu.my.id</b>`, chatId);
            } else if (cmd === '/start' || cmd === '/help') {
              const user = getUserByTelegramId(chatId);
              const helpMsg = `🏛️ <b>CLAUDIA CAPITAL</b>\n───────────────\n` +
                `<b>Perintah Tersedia:</b>\n` +
                `💳 <code>/deposit</code> — Rekening BCA VA Otomatis\n` +
                `📊 <code>/saldo</code> — Cek total portfolio & status posisi\n` +
                `⚙️ <code>/status</code> — Status mesin on-chain\n` +
                `🔑 <code>/password</code> — Dapatkan OTP Login Web Portal\n` +
                `📖 <code>/panduan</code> — Panduan platform\n` +
                `🌐 <code>/portal</code> — Web Dashboard\n` +
                `───────────────\n` +
                `Status Akun: <b>${user ? user.status : 'ACTIVE'}</b>`;
              await sendTelegramAlert(helpMsg, chatId);
            }
          }
        }
      } catch (e) {
        console.error('TGBOT_ERROR:', e);
      }
      setTimeout(pollTelegram, 1000);
    });
  });
  req.on('error', () => setTimeout(pollTelegram, 3000));
  req.end();
}

let isPollingStarted = false;
function startBotPolling() {
  if (isPollingStarted) return;
  isPollingStarted = true;
  setTelegramBotCommands();
  pollTelegram();
  console.log('🤖 [TelegramBot] Polling listener active for @claudia_capital_bot');
}

module.exports = {
  sendTelegramAlert,
  leanCommands,
  startBotPolling
};
