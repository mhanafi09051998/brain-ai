const fs = require('fs');
const path = '/home/ubuntu/apps/solana-trading-engine/src/watcher/telegramBot.js';
let code = fs.readFileSync(path, 'utf8');

code = code.replace(/\} catch \(e\) \{\}/g, "} catch (e) { console.error('TGBOT_ERROR:', e); }");

// Also add a log when an update is received
if (!code.includes("console.log('Update received:', update.update_id);")) {
  code = code.replace("for (const update of json.result) {", "for (const update of json.result) { console.log('Update received:', update.update_id);");
}

fs.writeFileSync(path, code);
console.log('Patched telegramBot.js with logging');
