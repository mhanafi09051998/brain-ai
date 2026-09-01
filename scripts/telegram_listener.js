const https = require('https');
const { exec } = require('child_process');
const path = require('path');
require('dotenv').config({ path: path.resolve(__dirname, '../../.env') });

const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
let lastUpdateId = 0;

function pollTelegram() {
  if (!BOT_TOKEN) return setTimeout(pollTelegram, 5000);

  const url = `https://api.telegram.org/bot${BOT_TOKEN}/getUpdates?offset=${lastUpdateId + 1}&timeout=30`;
  
  https.get(url, (res) => {
    let data = '';
    res.on('data', chunk => data += chunk);
    res.on('end', () => {
      try {
        const json = JSON.parse(data);
        if (json.ok && json.result.length > 0) {
          for (const update of json.result) {
            lastUpdateId = update.update_id;
            const text = update.message?.text || '';
            const chatId = update.message?.chat?.id;
            
            // Only respond to /status
            if (text.includes('/status')) {
              console.log(`[Telegram] Command /status diterima dari ${chatId}`);
              // Eksekusi script laporan yang sudah jadi
              exec('node /home/ubuntu/apps/solana-trading-engine/push_telegram.js', (err) => {
                if (err) console.error('[Telegram] Gagal merespons /status:', err);
              });
            }
          }
        }
      } catch (e) { }
      pollTelegram(); 
    });
  }).on('error', (e) => {
    setTimeout(pollTelegram, 5000);
  });
}

function startPolling() {
  console.log('🤖 Telegram Menu Listener ACTIVE - Hanya melayani /status');
  pollTelegram();
}

module.exports = { startPolling };
