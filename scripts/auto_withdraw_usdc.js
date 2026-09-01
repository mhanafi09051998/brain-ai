const crypto = require('crypto');
const https = require('https');
const WalletManager = require('./src/wallet');
require('dotenv').config();

const API_KEY = process.env.TOKOCRYPTO_API_KEY;
const API_SECRET = process.env.TOKOCRYPTO_API_SECRET;

async function autoWithdraw() {
  const w = new WalletManager();
  const phantomAddress = w.publicKey.toBase58();
  
  console.log(`[Auto-Withdraw] Mengecek saldo USDC di Tokocrypto...`);
  // Logika pengecekan saldo memerlukan endpoint /open/v1/account
  // Untuk keamanan, skrip ini menembakkan penarikan secara eksplisit

  const timestamp = Date.now();
  const params = new URLSearchParams({
    coin: 'USDC',
    network: 'SOL',
    address: phantomAddress,
    amount: '100', // Ganti dengan jumlah yang ingin ditarik, atau logika baca saldo
    timestamp: timestamp
  });

  const signature = crypto.createHmac('sha256', API_SECRET).update(params.toString()).digest('hex');
  params.append('signature', signature);

  const options = {
    hostname: 'www.tokocrypto.com',
    port: 443,
    path: `/open/v1/withdraws?${params.toString()}`, 
    method: 'POST',
    headers: {
      'X-MBX-APIKEY': API_KEY,
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  };

  const req = https.request(options, (res) => {
    let data = '';
    res.on('data', chunk => data += chunk);
    res.on('end', () => {
      console.log('[Auto-Withdraw] Respon Tokocrypto:', data);
    });
  });

  req.on('error', (e) => console.error('[Error]', e.message));
  req.end();
}

autoWithdraw();
