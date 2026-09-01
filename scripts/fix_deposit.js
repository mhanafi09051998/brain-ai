const fs = require('fs');
const path = '/home/ubuntu/apps/solana-trading-engine/src/watcher/telegramBot.js';
let code = fs.readFileSync(path, 'utf8');

const newDepositLogic = `
            } else if (cmd === '/deposit' || cmd === '/topup') {
              const msg = \`💳 <b>DEPOSIT VIRTUAL ACCOUNT</b>\\n───────────────\\nSilakan transfer nominal berapapun (Min Rp 50.000) ke rekening Virtual Account berikut:\\n\\n🏦 <b>Bank:</b> BCA Virtual Account\\n🔢 <b>No VA:</b> <code>1598284628342373</code>\\n👤 <b>Atas Nama:</b> Tokocrypto / Muhammad Hanafi\\n───────────────\\n✅ <i>Sistem akan otomatis mendeteksi transfer Anda, membelikan USDT, dan mengirimkannya ke Phantom Wallet.</i>\`;
              sendTelegramAlert(msg, chatId);
`;

code = code.replace(/} else if \(cmd === '\/deposit' \|\| cmd === '\/topup'\) \{[\s\S]*?catch\(err => \{[\s\S]*?\}\);/m, newDepositLogic.trim());

fs.writeFileSync(path, code);
console.log('telegramBot.js updated for static /deposit');
