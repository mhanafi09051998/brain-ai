require('dotenv').config();
const W = require('./src/wallet');
const w = new W();
w.getBalances().then(b => {
  console.log('SOL:', b.sol);
  console.log('USDC:', b.usdc);
  console.log('USDT:', b.usdt);
  process.exit(0);
}).catch(e => { console.error(e.message); process.exit(1); });
