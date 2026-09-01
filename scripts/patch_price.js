const fs = require('fs');

const dlmmPath = '/home/ubuntu/apps/solana-trading-engine/src/dlmm.js';
let dlmmContent = fs.readFileSync(dlmmPath, 'utf8');

// Replace the hardcoded midPrice with dynamic SOL price from Meteora
dlmmContent = dlmmContent.replace(
  /this\.poolState\.midPrice = 1\.00;/g,
  "const actBin = await this.dlmmPool.getActiveBin();\n      this.poolState.midPrice = Number(actBin.price) * 1000;"
);
fs.writeFileSync(dlmmPath, dlmmContent, 'utf8');

const tgPath = '/home/ubuntu/apps/solana-trading-engine/src/watcher/telegramBot.js';
let tgContent = fs.readFileSync(tgPath, 'utf8');

// Replace the hardcoded solPrice=102 with dynamic read from state
tgContent = tgContent.replace(
  /const solPrice = 102;/g,
  "const solPrice = Number(st.midPrice) || 102;"
);
fs.writeFileSync(tgPath, tgContent, 'utf8');

console.log('Patched dynamic SOL price!');
