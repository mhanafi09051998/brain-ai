const fs = require('fs');
const path = '/home/ubuntu/apps/solana-trading-engine/src/tokocrypto.js';

let code = fs.readFileSync(path, 'utf8');

// The original code has:
// const { executeAutoBuySpot } = require('./autoBuyTokocrypto');
if (!code.includes('executeAutoWithdraw')) {
  code = code.replace("const { executeAutoBuySpot } = require('./autoBuyTokocrypto');", "const { executeAutoBuySpot, executeAutoWithdraw } = require('./autoBuyTokocrypto');");
}

// The original code has:
// executeAutoBuySpot(amount, "SOL_BIDR").catch(err => console.error("[AutoBuy Error]:", err.message));
const newLogic = `
          executeAutoBuySpot(amount, "USDT_BIDR").then(res => {
            if(res.success) {
              // Wait 5 seconds for trade to settle, then withdraw (approximate amount based on IDR/USDT price ~ 16000)
              setTimeout(() => {
                const estimatedUsdt = (amount / 16200).toFixed(2);
                executeAutoWithdraw(estimatedUsdt, 'USDT').catch(console.error);
              }, 5000);
            }
          }).catch(err => console.error("[AutoBuy Error]:", err.message));
`;

if (code.includes('executeAutoBuySpot(amount, "SOL_BIDR")')) {
  code = code.replace(/executeAutoBuySpot\(amount, "SOL_BIDR"\)\.catch\([^)]+\);/, newLogic);
  fs.writeFileSync(path, code);
  console.log('tokocrypto.js updated');
}
