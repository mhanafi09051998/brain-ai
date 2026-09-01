const fs = require('fs');
const path = '/home/ubuntu/apps/solana-trading-engine/src/watcher/telegramBot.js';
let code = fs.readFileSync(path, 'utf8');

const depositLogic = `
            } else if (cmd === '/deposit' || cmd === '/topup') {
              const amountStr = args.replace(/[^0-9]/g, '');
              const amountIdr = parseInt(amountStr);
              if (isNaN(amountIdr) || amountIdr < 50000) {
                sendTelegramAlert('⚠️ <b>FORMAT DEPOSIT SALAH</b>\\n───────────────\\nFormat: <code>/deposit &lt;Nominal_Rupiah&gt;</code>\\nContoh: <code>/deposit 1000000</code>\\n\\n<i>*Minimal deposit adalah Rp 50.000</i>', chatId);
                continue;
              }
              const TokocryptoBridge = require('../tokocrypto');
              const tkx = new TokocryptoBridge();
              const user = getUserByTelegramId(chatId);
              const userName = user ? user.userName : 'Investor';
              
              tkx.createVirtualAccount({ telegramId: chatId, bank: 'BCA', amountIdr, userName })
                .then(res => {
                  let msg = \`💳 <b>INVOICE DEPOSIT TERCIPTA</b>\\n───────────────\\n👤 <b>Nama:</b> \${res.userName}\\n🏦 <b>Bank:</b> BCA Virtual Account\\n🔢 <b>No VA:</b> <code>\${res.vaNumber}</code>\\n💵 <b>Nominal:</b> Rp \${Number(res.amountIdr).toLocaleString('id-ID')}\\n🔖 <b>Ref ID:</b> <code>\${res.referenceId}</code>\\n───────────────\\n✅ <i>Silakan transfer tepat sesuai nominal. Uang akan otomatis diubah menjadi USDT dan dikirim ke Phantom Wallet Anda.</i>\`;
                  sendTelegramAlert(msg, chatId);
                })
                .catch(err => {
                  sendTelegramAlert('❌ Gagal membuat Virtual Account: ' + err.message, chatId);
                });
`;

if (!code.includes("cmd === '/deposit'")) {
  code = code.replace("} else if (cmd === '/daftar'", depositLogic + "            } else if (cmd === '/daftar'");
  fs.writeFileSync(path, code);
  console.log('telegramBot.js updated with /deposit');
} else {
  console.log('Already updated.');
}
