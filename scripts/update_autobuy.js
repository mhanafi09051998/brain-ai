const fs = require('fs');
const path = '/home/ubuntu/apps/solana-trading-engine/src/autoBuyTokocrypto.js';

let code = fs.readFileSync(path, 'utf8');

const withdrawFunc = `
async function executeAutoWithdraw(amountStr, coin = 'USDT') {
  return new Promise((resolve) => {
    const timestamp = Date.now();
    const phantomAddress = '9xmAeFDMqCuAUTyzgrCrxt3w65maSoja9YueqtmkSVyb';
    
    const params = new URLSearchParams({
      coin: coin,
      network: 'SOL',
      address: phantomAddress,
      amount: amountStr,
      timestamp: timestamp
    });

    const signature = crypto.createHmac('sha256', API_SECRET).update(params.toString()).digest('hex');
    params.append('signature', signature);

    const options = {
      hostname: 'www.tokocrypto.com',
      port: 443,
      path: \`/open/v1/withdraws?\${params.toString()}\`,
      method: 'POST',
      headers: {
        'X-MBX-APIKEY': API_KEY,
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    };

    console.log(\`[Tokocrypto AutoWithdraw] Initiating withdrawal of \${amountStr} \${coin} to \${phantomAddress}...\`);
    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        console.log('[Tokocrypto AutoWithdraw] Response:', data);
        resolve({ success: true, response: data });
      });
    });

    req.on('error', (err) => resolve({ success: false, error: err.message }));
    req.end();
  });
}
`;

if (!code.includes('executeAutoWithdraw')) {
  code = code.replace('module.exports = {', withdrawFunc + '\nmodule.exports = {\n  executeAutoWithdraw,');
  fs.writeFileSync(path, code);
  console.log('autoBuyTokocrypto.js updated');
}
