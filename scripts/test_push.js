const { sendTelegramAlert } = require('./src/watcher/telegramBot');
const msg = `🤖 *SYSTEM PING DARI CLAUDIA*

Koneksi DM Anda sudah terbuka dan stabil.
Silakan Anda membalas pesan ini dengan mengetik perintah:

👉 /deposit 50000
👉 /saldo
👉 /status`;
sendTelegramAlert(msg, '***CHAT_ID_REMOVED***');
setTimeout(() => process.exit(0), 3000);
