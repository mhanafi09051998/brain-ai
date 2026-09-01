const fs = require('fs');
const path = require('path');
const https = require('https');
require('dotenv').config({ path: path.resolve(__dirname, '.env') });

const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
const CHAT_ID = process.env.TELEGRAM_CHAT_ID;
const statePath = path.resolve(__dirname, 'data/dlmm_state.json');

function sendMessage(text) {
  const payload = JSON.stringify({
    chat_id: CHAT_ID,
    text: text
  });

  const options = {
    hostname: 'api.telegram.org',
    port: 443,
    path: `/bot${BOT_TOKEN}/sendMessage`,
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Content-Length': Buffer.byteLength(payload)
    }
  };

  const req = https.request(options, (res) => {
    let d = '';
    res.on('data', chunk => d += chunk);
    res.on('end', () => console.log('Telegram Response:', d));
  });
  req.on('error', (e) => console.error('Error:', e));
  req.write(payload);
  req.end();
}

try {
  const state = JSON.parse(fs.readFileSync(statePath, 'utf8'));
  
  const currentCapital = state.totalCapitalUsd || 0;
  const initialCapital = state.initialCapitalUsd || 1003.30;
  
  const pnlValue = currentCapital - initialCapital;
  const pnlPct = initialCapital > 0 ? (pnlValue / initialCapital) * 100 : 0;
  const pnlSign = pnlValue >= 0 ? '+' : '';

  // Format Date to WIB
  const dateOpts = { timeZone: 'Asia/Jakarta', day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit', timeZoneName: 'short' };
  const dateStr = new Date().toLocaleString('id-ID', dateOpts).replace('.', ':');

  const msg = `LAPORAN STATUS LP METEORA (SOL/USDC)
------------------------------------
Waktu Sinkronisasi : ${dateStr}

PARAMETER HARGA & RANGE
Harga SOL Saat Ini : $${(state.midPrice || 0).toFixed(2)}
Batas Bawah Range  : $${(state.lowerBound || 96.94).toFixed(2)}
Batas Atas Range   : $${(state.upperBound || 107.12).toFixed(2)}

PARAMETER MODAL & PNL
Total Modal Aktif  : $${currentCapital.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}
Floating PnL       : ${pnlSign}$${Math.abs(pnlValue).toFixed(2)} (${pnlSign}${Math.abs(pnlPct).toFixed(2)}%)

PARAMETER KINERJA FEE
Fee Belum Diklaim  : $${(state.totalFeeEarnedUsd || 0).toFixed(2)} (Disapu Auto-Compound)
Total Fee Diklaim  : $${(state.totalFeeClaimed || 3.31).toFixed(2)} (Akumulasi)

PARAMETER DOMPET
Saldo Gas Fee      : ${(state.walletSolBalance || 0).toFixed(4)} SOL
Saldo Menganggur   : ${(state.walletUsdcBalance || 0).toFixed(2)} USDC
------------------------------------
*Pesan otomatis dikirim 1 menit pasca auto-compound`;

  sendMessage(msg);
} catch (err) {
  console.error('Error generating report:', err);
}
