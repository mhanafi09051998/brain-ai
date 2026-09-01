const fs = require('fs');

const path = '/home/ubuntu/apps/solana-trading-engine/auto_compound.js';
let code = fs.readFileSync(path, 'utf8');

const target = `  await new Promise(r => setTimeout(r, 4000));

  // 2. Cek Saldo`;

const replacement = `  await new Promise(r => setTimeout(r, 4000));

  // 1.5 Cek & Jual Kelebihan SOL (jika ada deposit SOL dari Phantom)
  try {
    const lamports = await connection.getBalance(userPubkey);
    const solBal = lamports / 1e9;
    if (solBal > 0.05) {
      const excessSol = solBal - 0.05;
      console.log(\`Mendeteksi kelebihan \${excessSol.toFixed(4)} SOL! Menjual ke USDC...\`);
      const JupiterClient = require('./src/jupiter');
      const jupiter = new JupiterClient();
      const quote = await jupiter.getQuote({ inputToken: 'SOL', outputToken: 'USDC', amount: excessSol, slippageBps: 100 });
      if (quote && quote.success) {
        const result = await jupiter.executeSwap({ quoteResponse: quote.quoteResponse, keypair: wallet.keypair, connection: wallet.connection });
        if (result && result.success) {
          console.log('✅ Berhasil mengkonversi SOL -> USDC. Tx:', result.txid);
          await new Promise(r => setTimeout(r, 4000)); // Wait for balance update
        }
      }
    }
  } catch (e) {
    console.log('❌ Gagal cek/swap SOL:', e.message);
  }

  // 2. Cek Saldo`;

code = code.replace(target, replacement);
fs.writeFileSync(path, code);
console.log('Patched auto_compound.js with SOL auto-sell!');
