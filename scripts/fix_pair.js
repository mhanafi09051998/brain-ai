const fs = require('fs');
const f = '/home/ubuntu/apps/solana-trading-engine/src/watcher/telegramBot.js';
let c = fs.readFileSync(f, 'utf8');
c = c.replace(/`⚙️ <b>Pool:<\/b> \$\{st\.pair \|\| 'USDC\/USDT'\} \| \$\{poolStatus\}\\n` \+/, "`⚙️ <b>Status:</b> ${poolStatus}\\n` +");
fs.writeFileSync(f, c);
console.log('Done: removed pair name from /saldo');
