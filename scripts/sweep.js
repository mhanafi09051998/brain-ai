const WalletManager = require('./src/wallet');
const DLMM = require('@meteora-ag/dlmm');
const { PublicKey } = require('@solana/web3.js');
const BN = require('bn.js');
const fs = require('fs');

async function sweepAndInject() {
  const wallet = new WalletManager();
  const DLMMClass = DLMM.default || DLMM;
  const dlmmPool = await DLMMClass.create(wallet.connection, new PublicKey('ARwi1S4DaiTG5DX7S4M4ZsrXqpMD1MrTmbu9ue2tpmEq'));

  const b = await wallet.getBalances();
  const depositUsdc = Math.floor(b.usdc * 0.98 * 1e6);
  const depositUsdt = Math.floor(b.usdt * 0.98 * 1e6);
  
  // We need at least ~$800 to consider it a sweep
  if (depositUsdc < 800 * 1e6 || depositUsdt < 800 * 1e6) {
    return console.log('Belum ada dana besar di dompet. Tunggu user menutup posisi lama...');
  }

  const depositEach = Math.min(depositUsdc, depositUsdt);
  console.log(`Menginjeksi ${depositEach/1e6} USDC/USDT ke Ultra-Sniper...`);

  const activeSniperPubKey = new PublicKey('G8N9nkk1uqGT56h5VuHQPPxCAFzYByTq7upa1DpW4gcS');
  const activeBin = await dlmmPool.getActiveBin();

  try {
    const addTx = await dlmmPool.addLiquidityByStrategy({
      positionPubKey: activeSniperPubKey,
      user: wallet.publicKey,
      totalXAmount: new BN(depositEach),
      totalYAmount: new BN(depositEach),
      strategy: { maxBinId: activeBin.binId + 1, minBinId: activeBin.binId - 1, strategyType: 0 }
    });
    
    let txs = Array.isArray(addTx) ? addTx : [addTx];
    for (const tx of txs) {
      tx.feePayer = wallet.publicKey;
      const { blockhash } = await wallet.connection.getLatestBlockhash('confirmed');
      tx.recentBlockhash = blockhash;
      tx.sign(wallet.keypair);
      const sig = await wallet.connection.sendRawTransaction(tx.serialize());
      await wallet.connection.confirmTransaction(sig, 'confirmed');
      console.log('SUKSES INJEKSI:', sig);
    }
  } catch(e) {
    console.log('GAGAL INJEKSI:', e.message);
  }
}

sweepAndInject().catch(console.error);
