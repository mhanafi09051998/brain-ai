const fs = require('fs');
const path = '/home/ubuntu/apps/solana-trading-engine/src/server.js';
let content = fs.readFileSync(path, 'utf8');

if (!content.includes('telegram_listener')) {
  content = content.replace(
    'dlmm.start();', 
    "dlmm.start();\nconst tg = require('./telegram_listener');\ntg.startPolling();"
  );
  fs.writeFileSync(path, content, 'utf8');
  console.log('Server.js patched.');
} else {
  console.log('Already patched.');
}
