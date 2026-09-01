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

  console.log(`\n[${new Date().toISOString()}] 🚀 STARTING AUTO-COMPOUND`);
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

  await new Promise(r => setTimeout(r, 5000));

  // 2. Cek Saldo
  let freeUsdc = 0, freeUsdt = 0;
  try {
    const usdcAta = await getAssociatedTokenAddress(USDC_MINT, userPubkey);
    freeUsdc = Number((await getAccount(connection, usdcAta)).amount);
    const usdtAta = await getAssociatedTokenAddress(USDT_MINT, userPubkey);
    freeUsdt = Number((await getAccount(connection, usdtAta)).amount);
  } catch (e) {}

  console.log(`Saldo: USDC $${freeUsdc/1e6} | USDT $${freeUsdt/1e6}`);

  // 3. Auto Swap USDC Fee -> USDT karena jaring kita hanya makan USDT
  // Sisakan $1.5 USDC untuk dust
  const swapAmount = new BN(freeUsdc - 1500000);
  if (swapAmount.gten(1000000)) { // Swap jika USDC fee nganggur > $1
    console.log(`Auto-Swapping USDC Fee ke USDT via DLMM...`);
    try {
      const binArrays = await dlmmPool.getBinArrayForSwap(true, 4);
      const quote = dlmmPool.swapQuote(swapAmount, true, new BN(50), binArrays);
      const swapTx = await dlmmPool.swap({
        inToken: USDC_MINT, outToken: USDT_MINT,
        inAmount: swapAmount, minOutAmount: quote.minOutAmount,
        lbPair: dlmmPool.pubkey, user: userPubkey, binArraysPubkey: quote.binArraysPubkey
      });
      await sendAndConfirmTransaction(connection, swapTx, [wallet.keypair]);
      console.log('✅ Swap fee sukses!');
      
      const usdtAta = await getAssociatedTokenAddress(USDT_MINT, userPubkey);
      freeUsdt = Number((await getAccount(connection, usdtAta)).amount);
    } catch(e) { console.log('Swap fee gagal:', e.message); }
  }

  // 4. Reinvest USDT ke Posisi
  if (freeUsdt < 100000) return console.log('Saldo USDT terlalu kecil untuk di-reinvest.');

  let corePosition = userPositions[0]; // EocN...
  
  const depositX = new BN(0);
  const depositY = new BN(Math.floor(freeUsdt * 0.99)); 

  console.log(`Suntik USDT ke posisi...`);
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
