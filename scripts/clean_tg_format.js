const fs = require('fs');

const path = '/home/ubuntu/apps/solana-trading-engine/src/watcher/telegramBot.js';
let content = fs.readFileSync(path, 'utf8');

// Remove emojis and align text
content = content.replace(/💰 <b>Modal Awal<\/b>\\n` \+/g, "<b>Modal Awal</b>\\n` +");
content = content.replace(/🏦 <b>Diposisikan \(SOL\/USDC\)<\/b>\\n` \+/g, "<b>Diposisikan (SOL/USDC)</b>\\n` +");
content = content.replace(/💵 <b>Uang Dingin \(Idle\)<\/b>\\n` \+/g, "<b>Uang Dingin (Idle)</b>\\n` +");
content = content.replace(/⛽ <b>Cadangan Gas \(SOL\)<\/b>\\n` \+/g, "<b>Cadangan Gas (SOL)</b>\\n` +");

// Remove leading spaces for the values to make them flush left (straight)
content = content.replace(/`     \$\$\{initialUsd/g, "`$${initialUsd");
content = content.replace(/`     \$\$\{totalUsd/g, "`$${totalUsd");
content = content.replace(/`     \$\$\{usdcFree/g, "`$${usdcFree");
content = content.replace(/`     \$\{solBal/g, "`${solBal");

// Re-align the profit table to be straight too
content = content.replace(/`  24h    \$\{fmtUsd/g, "`24h      ${fmtUsd");
content = content.replace(/`    7d    \$\{fmtUsd/g, "`7d       ${fmtUsd");
content = content.replace(/`  30d    \$\{fmtUsd/g, "`30d      ${fmtUsd");
content = content.replace(/`    All    \$\{fmtUsd/g, "`All      ${fmtUsd");

fs.writeFileSync(path, content, 'utf8');
console.log('Cleaned up formatting!');
