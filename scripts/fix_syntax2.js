const fs = require('fs');

const path = '/home/ubuntu/apps/solana-trading-engine/src/watcher/telegramBot.js';
let content = fs.readFileSync(path, 'utf8');

// Due to $', we have a truncated function and a messed up file.
// Let's find exactly where it broke: '  const pnlPct = (pnlUsd / initialUsd) * 100;\n\n  // Formatting helpers\n  const fmtUsd = (v) => \''
const badSnippet = "  const fmtUsd = (v) => '\\nfunction buildDepositMessage() {";
if (content.includes(badSnippet)) {
  console.log("Found bad snippet, fixing...");
}

// Actually, it's safer to just rewrite the whole file manually.
// Wait, is it better to pull the old file from Git?
// I don't know if the user uses git here.
