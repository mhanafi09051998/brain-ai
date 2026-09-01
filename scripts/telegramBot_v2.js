'use strict';

const https = require('https');
const fs = require('fs');
const path = require('path');

const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN || '***TELEGRAM_TOKEN_REMOVED***';
const ADMIN_CHAT_ID = '***CHAT_ID_REMOVED***';
const DATA_DIR = path.join(__dirname, '..', '..', 'data');
const DLMM_STATE_FILE = path.join(DATA_DIR, 'dlmm_state.json');

// ─── Only 2 commands ───
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

// ─── Send message via Telegram API ───
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

// ─── /saldo: Real-time portfolio from dlmm_state.json ───
function buildSaldoMessage() {
  let st = {};
  try {
    if (fs.existsSync(DLMM_STATE_FILE)) st = JSON.parse(fs.readFileSync(DLMM_STATE_FILE, 'utf8'));
  } catch (e) {}

  const RATE = 16250; // USD/IDR approximate
  const INITIAL_USD = 932.40; // Modal awal yang dimasukkan ke pool

  const totalUsd    = Number(st.totalCapitalUsd) || 0;
  const solBal      = Number(st.walletSolBalance) || 0;
  const usdcFree    = Number(st.walletUsdcBalance) || 0;
  const usdtFree    = Number(st.walletUsdtBalance) || 0;
  const feeEarned   = Number(st.totalFeeEarnedUsd) || 0;
  const solPrice    = 102; // approximate

  const gasFeeUsd   = solBal * solPrice;
  const idleFunds   = usdcFree + usdtFree;
  const positionUsd = totalUsd; // capital in pool
  const pnlUsd      = totalUsd + idleFunds + gasFeeUsd - INITIAL_USD;

  const totalIdr    = Math.round(totalUsd * RATE);
  const initialIdr  = Math.round(INITIAL_USD * RATE);
  const pnlIdr      = Math.round(pnlUsd * RATE);
  const gasFeeIdr   = Math.round(gasFeeUsd * RATE);
  const idleIdr     = Math.round(idleFunds * RATE);

  const pnlEmoji    = pnlUsd >= 0 ? '📈' : '📉';
  const pnlSign     = pnlUsd >= 0 ? '+' : '';
  const poolStatus  = st.status === 'ACTIVE' ? '🟢 In Range (Earning Fees)' : '🔴 Out of Range';

  const syncTime    = st.lastSyncTime ? new Date(st.lastSyncTime).toLocaleString('id-ID', { timeZone: 'Asia/Jakarta' }) : '-';

  return `📊 <b>SALDO • CLAUDIA CAPITAL</b>\n` +
    `───────────────\n` +
    `💰 <b>Modal Awal:</b>\n` +
    `    $${INITIAL_USD.toFixed(2)} (~Rp ${initialIdr.toLocaleString('id-ID')})\n\n` +
    `🏦 <b>Saldo di Pool (Diposisikan):</b>\n` +
    `    $${positionUsd.toFixed(2)} (~Rp ${totalIdr.toLocaleString('id-ID')})\n\n` +
    `💵 <b>Saldo Idle (Belum Masuk Pool):</b>\n` +
    `    USDC $${usdcFree.toFixed(2)} | USDT $${usdtFree.toFixed(2)}\n` +
    `    Total: $${idleFunds.toFixed(2)} (~Rp ${idleIdr.toLocaleString('id-ID')})\n\n` +
    `⛽ <b>Gas Fee (SOL):</b>\n` +
    `    ${solBal.toFixed(4)} SOL (~$${gasFeeUsd.toFixed(2)} / Rp ${gasFeeIdr.toLocaleString('id-ID')})\n\n` +
    `${pnlEmoji} <b>PnL (Profit & Loss):</b>\n` +
    `    ${pnlSign}$${pnlUsd.toFixed(2)} (${pnlSign}Rp ${pnlIdr.toLocaleString('id-ID')})\n\n` +
    `⚙️ <b>Pool:</b> ${st.pair || 'USDC/USDT'} | ${poolStatus}\n` +
    `🕐 <b>Sync:</b> ${syncTime} WIB`;
}

// ─── /deposit: Static VA BCA ───
function buildDepositMessage() {
  return `💳 <b>DEPOSIT • VIRTUAL ACCOUNT BCA</b>\n` +
    `───────────────\n` +
    `Transfer nominal bebas (Min Rp 50.000):\n\n` +
    `🏦 <b>Bank:</b> BCA Virtual Account\n` +
    `🔢 <b>No VA:</b> <code>1598284628342373</code>\n` +
    `👤 <b>Atas Nama:</b> Tokocrypto / Muhammad Hanafi\n` +
    `───────────────\n` +
    `<i>Setelah transfer, beli SOL di Tokocrypto lalu kirim ke Phantom Wallet. Mesin akan otomatis mengkonversi & menyuntikkan ke pool.</i>`;
}

// ─── Polling Loop ───
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
                `🏛️ <b>CLAUDIA CAPITAL</b>\n───────────────\n` +
                `📊 <code>/saldo</code> — Cek saldo, posisi & PnL real-time\n` +
                `💳 <code>/deposit</code> — Nomor VA BCA untuk top-up`, chatId);
            }
          }
        }
      } catch (e) {
        console.error('TGBOT_POLL_ERR:', e.message);
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
  console.log('🤖 [TelegramBot] Active — /saldo & /deposit only');
}

module.exports = { sendTelegramAlert, leanCommands, startBotPolling };
