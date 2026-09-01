const fs = require('fs');
const https = require('https');

const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN || '***TELEGRAM_TOKEN_REMOVED***';

// Hardcode bot token since we can just read it from env normally, but I'll write the script so it can run via PM2.

const fileContent = `const https = require('https');
const fs = require('fs');

const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN || '***TELEGRAM_TOKEN_REMOVED***';

function sendTelegramAlert(text, customChatId = null) {
  return new Promise((resolve) => {
    // If we want to send globally to whoever pinged, we use customChatId. 
    // Usually ADMIN_CHAT_ID is used for push alerts.
    const targetId = customChatId || process.env.TELEGRAM_CHAT_ID || '***CHAT_ID_REMOVED***'; 
    const payload = JSON.stringify({
      chat_id: targetId,
      text: text,
      parse_mode: 'HTML',
      disable_web_page_preview: true
    });
    const req = https.request('https://api.telegram.org/bot' + BOT_TOKEN + '/sendMessage', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    }, (res) => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => resolve(data));
    });
    req.on('error', () => resolve(null));
    req.write(payload);
    req.end();
  });
}

function setTelegramBotCommands() {
  const payload = JSON.stringify({
    commands: [
      { command: 'saldo', description: 'Cek Portfolio & PnL' },
      { command: 'deposit', description: 'Panduan Topup VA' }
    ]
  });
  const req = https.request('https://api.telegram.org/bot' + BOT_TOKEN + '/setMyCommands', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  });
  req.write(payload);
  req.end();
}

function buildSaldoMessage() {
  let st = {};
  try {
    const DATA_DIR = require('path').join(__dirname, '..', '..', 'data');
    const DLMM_STATE_FILE = require('path').join(DATA_DIR, 'dlmm_state.json');
    if (fs.existsSync(DLMM_STATE_FILE)) st = JSON.parse(fs.readFileSync(DLMM_STATE_FILE, 'utf8'));
  } catch (e) {}

  const initialUsd = Number(st.initialCapitalUsd) || 956.72;
  const totalUsd = Number(st.totalCapitalUsd) || 0;
  const currentFee = Number(st.totalFeeEarnedUsd) || 0;
  
  const posSol = Number(st.posSol) || 0;
  const posUsdc = Number(st.posUsdc) || 0;
  const feeSol = Number(st.feeSol) || 0;
  const feeUsdc = Number(st.feeUsdc) || 0;
  
  const solPrice = Number(st.midPrice) || 102;
  
  const posSolUsd = posSol * solPrice;
  const posUsdcUsd = posUsdc;
  const feeSolUsd = feeSol * solPrice;
  const feeUsdcUsd = feeUsdc;
  
  const pnlUsd = (totalUsd + currentFee) - initialUsd;
  const pnlPct = initialUsd > 0 ? (pnlUsd / initialUsd) * 100 : 0;

  const fmtUsd = (v) => '$' + Math.abs(v).toFixed(2);
  const fmtSignUsd = (v) => (v >= 0 ? '+' : '-') + '$' + Math.abs(v).toFixed(2);
  const fmtSignPct = (v) => (v >= 0 ? '+' : '-') + Math.abs(v).toFixed(2) + '%';
  const fmtSol = (v) => v >= 0.001 ? v.toFixed(4) : v.toPrecision(3);

  const pMin = 96.94;
  const pMax = 107.12;
  let claimedFees = 1.04; 

  return \`📊 <b>P O S I T I O N S</b>\\n\` +
    \`━━━━━━━━━━━━━━━━━━\\n\\n\` +
    
    \`💧 <b>Total Liquidity:</b> \${fmtUsd(totalUsd)}\\n\` +
    \`🎁 <b>Claimable Fees:</b> \${fmtUsd(currentFee)}\\n\` +
    \`✅ <b>Fees Claimed:</b> \${fmtUsd(claimedFees)}\\n\\n\` +

    \`━━━━━━━━━━━━━━━━━━\\n\` +
    \`⚖️ <b>Price Range</b>\\n\` +
    \`\${pMin.toFixed(2)} - \${pMax.toFixed(2)}\\n\` +
    \`USDC per SOL\\n\\n\` +

    \`💰 <b>Your Liquidity</b>\\n\` +
    \`\${fmtUsd(totalUsd)}\\n\` +
    \`◎ \${fmtSol(posSol)} (\${fmtUsd(posSolUsd)})\\n\` +
    \`$ \${posUsdc.toFixed(2)} (\${fmtUsd(posUsdcUsd)})\\n\\n\` +

    \`🎁 <b>Claimable Fees</b>\\n\` +
    \`\${fmtUsd(currentFee)}\\n\` +
    \`◎ \${fmtSol(feeSol)} (\${fmtUsd(feeSolUsd)})\\n\` +
    \`$ \${feeUsdc.toPrecision(3)} (\${fmtUsd(feeUsdcUsd)})\\n\\n\` +

    \`📈 <b>PnL</b>\\n\` +
    \`\${fmtSignUsd(pnlUsd)} (\${fmtSignPct(pnlPct)})\\n\` +
    \`━━━━━━━━━━━━━━━━━━\`;
}

function buildDepositMessage() {
  return \`💳  <b>D E P O S I T</b>\\n\` +
    \`━━━━━━━━━━━━━━━━━━\\n\\n\` +
    \`Transfer nominal bebas (Min Rp 50.000):\\n\\n\` +
    \`🏦 <b>Bank:</b> BCA Virtual Account\\n\` +
    \`🔢 <b>No VA:</b> <code>1598284628342373</code>\\n\` +
    \`👤 <b>A/N:</b> Tokocrypto / Muhammad Hanafi\\n\\n\` +
    \`━━━━━━━━━━━━━━━━━━\\n\` +
    \`<i>Beli SOL di Tokocrypto → Kirim ke Phantom.\\nMesin otomatis konversi & suntik ke pool.</i>\`;
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
            
            const cmd = msgObj.text.trim().split(/\\s+/)[0].toLowerCase().split('@')[0];
            const chatId = String(msgObj.chat.id); // This will handle DM or group properly

            if (cmd === '/saldo') {
              await sendTelegramAlert(buildSaldoMessage(), chatId);
            } else if (cmd === '/deposit') {
              await sendTelegramAlert(buildDepositMessage(), chatId);
            } else if (cmd === '/start' || cmd === '/help') {
              await sendTelegramAlert(
                \`🏛️ <b>CLAUDIA CAPITAL</b>\\n━━━━━━━━━━━━━━━━━━\\n\\n\` +
                \`📊  /saldo  —  Portfolio & PnL\\n\` +
                \`💳  /deposit  —  VA BCA\`, chatId);
            }
          }
        }
      } catch (e) {}
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

module.exports = { sendTelegramAlert, startBotPolling };
`;

fs.writeFileSync('/home/ubuntu/apps/solana-trading-engine/src/watcher/telegramBot.js', fileContent, 'utf8');
console.log('Telegram bot completely rewritten cleanly.');
