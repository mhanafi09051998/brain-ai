const fs = require('fs');

const path = '/home/ubuntu/apps/solana-trading-engine/src/watcher/telegramBot.js';
let content = fs.readFileSync(path, 'utf8');

// Replace string parts
content = content.replace(
  /Diposisikan \(Pool\)/g,
  "Diposisikan (SOL/USDC)"
);
content = content.replace(
  /USDC \$\$\{usdcFree\.toFixed\(2\)\}\s+\|\s+USDT \$\$\{usdtFree\.toFixed\(2\)\}/g,
  "$${usdcFree.toFixed(2)} USDC"
);
content = content.replace(
  /💵 <b>Idle<\/b>/g,
  "💵 <b>Uang Dingin (Idle)</b>"
);
content = content.replace(
  /⛽ <b>Gas Fee<\/b>/g,
  "⛽ <b>Cadangan Gas (SOL)</b>"
);

// We can also add SOL / USDC split under positioned if we had the data, but for now we'll just fix the labels.
fs.writeFileSync(path, content, 'utf8');
console.log('Fixed Telegram labels!');
