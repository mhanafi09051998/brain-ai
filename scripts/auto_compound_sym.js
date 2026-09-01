const { PublicKey, sendAndConfirmTransaction } = require('@solana/web3.js');
const { getAssociatedTokenAddress, getAccount } = require('@solana/spl-token');
const DLMM = require('@meteora-ag/dlmm').default || require('@meteora-ag/dlmm');
const { StrategyType } = require('@meteora-ag/dlmm');
const BN = require('bn.js');
const WalletManager = require('./src/wallet');

const USDC_USDT_POOL_ADDRESS = 'ARwi1S4DaiTG5DX7S4M4ZsrXqpMD1MrTmbu9ue2tpmEq';
const USDC_MINT = new PublicKey('EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v');
const USDT_MINT = new PublicKey('Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB');

async function autoCompound() {
  const wallet = new WalletManager();
  const connection = wallet.connection;
  const userPubkey = wallet.keypair.publicKey;

  console.log(`\n[${new Date().toISOString()}] 🚀 STARTING AUTO-COMPOUND (SYMMETRICAL 80/20)`);
  const dlmmPool = await DLMM.create(connection, new PublicKey(USDC_USDT_POOL_ADDRESS));
  
  const { userPositions } = await dlmmPool.getPositionsByUserAndLbPair(userPubkey);
  if (!userPositions || userPositions.length === 0) return console.log('Tidak ada posisi.');

  // 1. Claim Fees
  for (const pos of userPositions) {
    try {
      const claimTx = await dlmmPool.claimSwapFee({ position: pos, owner: userPubkey });
      const txs = Array.isArray(claimTx) ? claimTx : [claimTx];
      for (let tx of txs) {
        await sendAndConfirmTransaction(connection, tx, [wallet.keypair], { commitment: 'confirmed' });
      }
      console.log(`✅ Fee diklaim dari ${pos.publicKey.toBase58()}`);
    } catch (err) {}
  }

  await new Promise(r => setTimeout(r, 4000));

  // 2. Cek Saldo
  let freeUsdc = 0, freeUsdt = 0;
  try {
    const usdcAta = await getAssociatedTokenAddress(USDC_MINT, userPubkey);
    freeUsdc = Number((await getAccount(connection, usdcAta)).amount) / 1e6;
    const usdtAta = await getAssociatedTokenAddress(USDT_MINT, userPubkey);
    freeUsdt = Number((await getAccount(connection, usdtAta)).amount) / 1e6;
  } catch (e) {}

  console.log(`Saldo Awal: USDC $${freeUsdc.toFixed(4)} | USDT $${freeUsdt.toFixed(4)}`);

  // 3. Auto-Rebalance untuk Dana Top-up Besar (> $10 selisih)
  const diff = Math.abs(freeUsdc - freeUsdt);
  if (diff > 10) {
    const swapAmount = new BN(Math.floor((diff / 2) * 1e6));
    const swapForY = freeUsdc > freeUsdt; // Jika USDC > USDT, kita swap USDC ke USDT
    console.log(`Mendeteksi Top-Up! Melakukan Auto-Rebalance $${diff/2} ke koin pasangannya...`);
    
    try {
      const binArrays = await dlmmPool.getBinArrayForSwap(swapForY, 4);
      const quote = dlmmPool.swapQuote(swapAmount, swapForY, new BN(50), binArrays);
      const inTokenMint = swapForY ? USDC_MINT : USDT_MINT;
      const outTokenMint = swapForY ? USDT_MINT : USDC_MINT;
      
      const swapTx = await dlmmPool.swap({
        inToken: inTokenMint, outToken: outTokenMint,
        inAmount: swapAmount, minOutAmount: quote.minOutAmount,
        lbPair: dlmmPool.pubkey, user: userPubkey, binArraysPubkey: quote.binArraysPubkey
      });
      await sendAndConfirmTransaction(connection, swapTx, [wallet.keypair]);
      console.log('✅ Rebalance Sukses!');
      await new Promise(r => setTimeout(r, 4000));
      
      // Baca ulang
      freeUsdc = Number((await getAccount(connection, usdcAta)).amount) / 1e6;
      freeUsdt = Number((await getAccount(connection, usdtAta)).amount) / 1e6;
      console.log(`Saldo Seimbang: USDC $${freeUsdc.toFixed(4)} | USDT $${freeUsdt.toFixed(4)}`);
    } catch (e) {
      console.log('❌ Gagal Rebalance:', e.message);
    }
  }

  // 4. Reinvest Symmetrical ke Posisi
  if (freeUsdc < 0.1 && freeUsdt < 0.1) return console.log('Saldo terlalu kecil.');

  let corePosition = userPositions[0]; 
  const addAmount = Math.min(freeUsdc, freeUsdt) * 0.95;
  if (addAmount < 0.01) return console.log('Butuh akumulasi simetris.');

  const depositX = new BN(Math.floor(addAmount * 1e6));
  const depositY = new BN(Math.floor(addAmount * 1e6)); 

  console.log(`Suntik $${(addAmount*2).toFixed(4)} ke posisi Core...`);
  try {
    const addLiquidityTx = await dlmmPool.addLiquidityByStrategy({
      positionPubKey: corePosition.publicKey,
      user: userPubkey,
      totalXAmount: depositX,
      totalYAmount: depositY,
      strategy: { maxBinId: corePosition.positionData.upperBinId, minBinId: corePosition.positionData.lowerBinId, strategyType: StrategyType.Spot }
    });
    
    const txs = Array.isArray(addLiquidityTx) ? addLiquidityTx : [addLiquidityTx];
    for (let tx of txs) {
      await sendAndConfirmTransaction(connection, tx, [wallet.keypair], { commitment: 'confirmed' });
      console.log('✅ SNOWBALL COMPOUND BERHASIL!');
    }
  } catch (err) {
    console.log('❌ Gagal Reinvestasi:', err.message);
  }
}
autoCompound().catch(console.error);
