'use strict';

const https = require('https');
const fs = require('fs');
const path = require('path');

const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN || '***TELEGRAM_TOKEN_REMOVED***';
const ADMIN_CHAT_ID = '***CHAT_ID_REMOVED***';
const DATA_DIR = path.join(__dirname, '..', '..', 'data');
const DLMM_STATE_FILE = path.join(DATA_DIR, 'dlmm_state.json');
const FEE_HISTORY_FILE = path.join(DATA_DIR, 'fee_history.json');

const leanCommands = [
  { command: 'saldo', description: 'Cek saldo, posisi, gas fee & PnL real-time' },
  { command: 'deposit', description: 'Nomor Virtual Account BCA (Tokocrypto)' }
];

function setTelegramBotCommands() {
  if (!BOT_TOKEN) return;
  const scopes = [{ type: 'default' }, { type: 'all_private_chats' }, { type: 'all_group_chats' }];
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
  const payload = JSON.stringify({ chat_id: String(targetId), text, parse_mode: 'HTML', disable_web_page_preview: true });
  return new Promise((resolve) => {
    const req = https.request('https://api.telegram.org/bot' + BOT_TOKEN + '/sendMessage', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(payload) },
      timeout: 10000
    }, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        try { resolve(JSON.parse(body).ok ? JSON.parse(body).result : null); }
        catch (e) { resolve(null); }
      });
    });
    req.on('error', () => resolve(null));
    req.write(payload);
    req.end();
  });
}

// ─── Fee History Helpers ───
function loadFeeHistory() {
  try {
    if (fs.existsSync(FEE_HISTORY_FILE)) return JSON.parse(fs.readFileSync(FEE_HISTORY_FILE, 'utf8')) || [];
  } catch (e) {}
  return [];
}

function getFeeSince(history, currentFee, msAgo) {
  if (!history.length) return currentFee;
  const cutoff = Date.now() - msAgo;
  // Find the earliest entry at or after the cutoff
  let closest = history[0];
  for (const entry of history) {
    if (entry.ts <= cutoff) closest = entry;
    else break;
  }
  return Math.max(0, currentFee - (closest.fee || 0));
}

function fmtUsd(v) {
  const sign = v >= 0 ? '+' : '';
  return sign + '$' + Math.abs(v).toFixed(4);
}

function fmtIdr(v) {
  const sign = v >= 0 ? '+' : '-';
  return sign + 'Rp ' + Math.abs(Math.round(v)).toLocaleString('id-ID');
}

// ─── /saldo ───
function buildSaldoMessage() {
  let st = {};
  try {
    if (fs.existsSync(DLMM_STATE_FILE)) st = JSON.parse(fs.readFileSync(DLMM_STATE_FILE, 'utf8'));
  } catch (e) {}

  const RATE = 16250;
  const initialUsd = Number(st.initialCapitalUsd) || 932.40;
  const totalUsd = Number(st.totalCapitalUsd) || 0;
  const solBal = Number(st.walletSolBalance) || 0;
  const usdcFree = Number(st.walletUsdcBalance) || 0;
  const usdtFree = Number(st.walletUsdtBalance) || 0;
  const currentFee = Number(st.totalFeeEarnedUsd) || 0;
  const solPrice = 102;
  const gasFeeUsd = solBal * solPrice;
  const idleFunds = usdcFree + usdtFree;

  // PnL from fee history
  const history = loadFeeHistory();
  const MS_24H = 86400000;
  const MS_7D = 604800000;
  const MS_30D = 2592000000;

  const pnl24h = getFeeSince(history, currentFee, MS_24H);
  const pnl7d = getFeeSince(history, currentFee, MS_7D);
  const pnl30d = getFeeSince(history, currentFee, MS_30D);
  const pnlAll = currentFee;

  const poolStatus = st.status === 'ACTIVE' ? '🟢 In Range' : '🔴 Out of Range';
  const syncTime = st.lastSyncTime
    ? new Date(st.lastSyncTime).toLocaleString('id-ID', { timeZone: 'Asia/Jakarta', day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
    : '-';

  return `📊  <b>S A L D O</b>\n` +
    `━━━━━━━━━━━━━━━━━━\n\n` +

    `💰 <b>Modal Awal</b>\n` +
    `     $${initialUsd.toFixed(2)}  (~Rp ${Math.round(initialUsd * RATE).toLocaleString('id-ID')})\n\n` +

    `🏦 <b>Diposisikan (Pool)</b>\n` +
    `     $${totalUsd.toFixed(2)}  (~Rp ${Math.round(totalUsd * RATE).toLocaleString('id-ID')})\n\n` +

    `💵 <b>Idle</b>\n` +
    `     USDC $${usdcFree.toFixed(2)}  |  USDT $${usdtFree.toFixed(2)}\n\n` +

    `⛽ <b>Gas Fee</b>\n` +
    `     ${solBal.toFixed(4)} SOL  (~$${gasFeeUsd.toFixed(2)})\n\n` +

    `━━━━━━━━━━━━━━━━━━\n` +
    `📈  <b>P R O F I T</b>\n` +
    `━━━━━━━━━━━━━━━━━━\n\n` +

    `  24h    ${fmtUsd(pnl24h)}  (${fmtIdr(pnl24h * RATE)})\n` +
    `    7d    ${fmtUsd(pnl7d)}  (${fmtIdr(pnl7d * RATE)})\n` +
    `  30d    ${fmtUsd(pnl30d)}  (${fmtIdr(pnl30d * RATE)})\n` +
    `    All    ${fmtUsd(pnlAll)}  (${fmtIdr(pnlAll * RATE)})\n\n` +

    `⚙️ ${poolStatus}\n` +
    `🕐 ${syncTime} WIB`;
}

// ─── /deposit ───
function buildDepositMessage() {
  return `💳  <b>D E P O S I T</b>\n` +
    `━━━━━━━━━━━━━━━━━━\n\n` +
    `Transfer nominal bebas (Min Rp 50.000):\n\n` +
    `🏦 <b>Bank:</b> BCA Virtual Account\n` +
    `🔢 <b>No VA:</b> <code>1598284628342373</code>\n` +
    `👤 <b>A/N:</b> Tokocrypto / Muhammad Hanafi\n\n` +
    `━━━━━━━━━━━━━━━━━━\n` +
    `<i>Beli SOL di Tokocrypto → Kirim ke Phantom.\nMesin otomatis konversi & suntik ke pool.</i>`;
}

// ─── Polling ───
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
            const cmd = msgObj.text.trim().split(/\s+/)[0].toLowerCase().split('@')[0];
            const chatId = String(msgObj.chat.id);

            if (cmd === '/saldo' || cmd === '/status' || cmd === '/balance') {
              await sendTelegramAlert(buildSaldoMessage(), chatId);
            } else if (cmd === '/deposit' || cmd === '/topup') {
              await sendTelegramAlert(buildDepositMessage(), chatId);
            } else if (cmd === '/start' || cmd === '/help') {
              await sendTelegramAlert(
                `🏛️ <b>CLAUDIA CAPITAL</b>\n━━━━━━━━━━━━━━━━━━\n\n` +
                `📊  /saldo  —  Portfolio & PnL\n` +
                `💳  /deposit  —  VA BCA`, chatId);
            }
          }
        }
      } catch (e) {
        console.error('TGBOT_ERR:', e.message);
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
  console.log('🤖 [TelegramBot] Active — /saldo & /deposit');
}

module.exports = { sendTelegramAlert, leanCommands, startBotPolling };
