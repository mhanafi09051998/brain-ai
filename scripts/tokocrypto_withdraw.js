const crypto = require('crypto');
const https = require('https');
const WalletManager = require('./src/wallet');
require('dotenv').config();

const API_KEY = process.env.TOKOCRYPTO_API_KEY;
const API_SECRET = process.env.TOKOCRYPTO_API_SECRET;

async function autoWithdraw() {
  const w = new WalletManager();
  const phantomAddress = w.publicKey.toBase58();
  
  console.log(`[Auto-Withdraw] Target Wallet: ${phantomAddress}`);
  
  // Parameter Penarikan USDC via Solana
  const params = new URLSearchParams({
    coin: 'USDC',
    network: 'SOL',
    address: phantomAddress,
    amount: '100', // Contoh statis, dalam praktiknya harus baca saldo
    timestamp: Date.now()
  });

  const signature = crypto
    .createHmac('sha256', API_SECRET)
    .update(params.toString())
    .digest('hex');
    
  params.append('signature', signature);

  const options = {
    hostname: 'www.tokocrypto.com',
    path: '/open/v1/withdraws?' + params.toString(), // Endpoint standar Binance Cloud
    method: 'POST',
    headers: {
      'X-MBX-APIKEY': API_KEY,
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  };

  console.log('[Auto-Withdraw] Mengeksekusi penarikan dari Tokocrypto...');
  
  const req = https.request(options, (res) => {
    let data = '';
    res.on('data', chunk => data += chunk);
    res.on('end', () => {
      console.log('[Auto-Withdraw] Response Tokocrypto:', data);
      console.log('Pastikan Anda sudah menonaktifkan Email/SMS OTP untuk Withdrawal via API di pengaturan keamanan Tokocrypto Anda (Whitelist Address).');
    });
  });

  req.on('error', (e) => console.error(e));
  req.end();
}

autoWithdraw();
