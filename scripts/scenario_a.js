const { Connection, PublicKey, sendAndConfirmTransaction } = require('@solana/web3.js');
const { getAssociatedTokenAddress, getAccount } = require('@solana/spl-token');
const DLMM = require('@meteora-ag/dlmm').default || require('@meteora-ag/dlmm');
const { StrategyType } = require('@meteora-ag/dlmm');
const BN = require('bn.js');
const WalletManager = require('./src/wallet');

const USDC_USDT_POOL_ADDRESS = 'ARwi1S4DaiTG5DX7S4M4ZsrXqpMD1MrTmbu9ue2tpmEq';
const USDC_MINT = new PublicKey('EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v');
const USDT_MINT = new PublicKey('Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB');

async function executeScenarioA() {
  const wallet = new WalletManager();
  const connection = wallet.connection;
  const userPubkey = wallet.keypair.publicKey;

  console.log('==================================================');
  console.log('🔄 MIGRATION INITIATED: MOVING TO SCENARIO A (FULL BIN -6 TO 6)');
  console.log('==================================================');

  const dlmmPool = await DLMM.create(connection, new PublicKey(USDC_USDT_POOL_ADDRESS));
  
  // 1. Withdraw all liquidity from existing positions in this pool
  const { userPositions } = await dlmmPool.getPositionsByUserAndLbPair(userPubkey);
  console.log(`Ditemukan ${userPositions.length} posisi lama. Memulai penutupan...`);

  for (const pos of userPositions) {
    console.log(`Menutup posisi ${pos.publicKey.toBase58()}...`);
    try {
      const removeLiquidityTxs = await dlmmPool.removeLiquidity({
        position: pos.publicKey,
        user: userPubkey,
        binIds: pos.positionData.positionBinData.map(b => b.binId),
        bps: 10000,
        shouldClaimAndClose: true
      });
      const txList = Array.isArray(removeLiquidityTxs) ? removeLiquidityTxs : [removeLiquidityTxs];
      for (const tx of txList) {
        await sendAndConfirmTransaction(connection, tx, [wallet.keypair], { commitment: 'confirmed' });
      }
      console.log(`✅ Posisi ${pos.publicKey.toBase58()} berhasil ditutup.`);
    } catch (e) {
      console.log(`Gagal menutup posisi ${pos.publicKey.toBase58()}:`, e.message);
    }
  }

  // 2. Tunggu sebentar untuk finalisasi blockchain
  console.log('\nMenunggu RPC Finalization...');
  await new Promise(r => setTimeout(r, 8000));

  // 3. Ambil saldo baru (100% modal)
  const usdcAta = await getAssociatedTokenAddress(USDC_MINT, userPubkey);
  const usdcAcc = await getAccount(connection, usdcAta);
  const usdcBal = Number(usdcAcc.amount) / 1e6;
  
  const usdtAta = await getAssociatedTokenAddress(USDT_MINT, userPubkey);
  const usdtAcc = await getAccount(connection, usdtAta);
  const usdtBal = Number(usdtAcc.amount) / 1e6;

  console.log(`Saldo Terkumpul | USDC: $${usdcBal.toFixed(4)} | USDT: $${usdtBal.toFixed(4)}`);

  // 4. Deploy Posisi Baru (Scenario A)
  const activeBin = await dlmmPool.getActiveBin();
  console.log(`\nActive Bin ID: ${activeBin.binId}`);
  
  // Karena user ingin tenang, gunakan batas aman: 99% dari free balance yang terendah
  const safeBalance = Math.min(usdcBal, usdtBal) * 0.99;
  const depositX = new BN(Math.floor(safeBalance * 1e6));
  const depositY = new BN(Math.floor(safeBalance * 1e6));

  const minBin = activeBin.binId - 6;
  const maxBin = activeBin.binId + 6;

  console.log(`\nMenyiapkan 1 POSISI FULL (Spot) -> Bin ${minBin} to ${maxBin}`);
  
  try {
    const { Keypair } = require('@solana/web3.js');
    const newPosKeypair = Keypair.generate();
    const createTx = await dlmmPool.initializePositionAndAddLiquidityByStrategy({
      positionPubKey: newPosKeypair.publicKey,
      user: userPubkey,
      totalXAmount: depositX,
      totalYAmount: depositY,
      strategy: { maxBinId: maxBin, minBinId: minBin, strategyType: StrategyType.Spot }
    });
    const txHash = await sendAndConfirmTransaction(connection, createTx, [wallet.keypair, newPosKeypair], { commitment: 'confirmed' });
    console.log(`✅ DEPLOYMENT BERHASIL! Tx: ${txHash}`);
    console.log(`✅ Posisi Baru: ${newPosKeypair.publicKey.toBase58()}`);
  } catch (err) {
    console.log('❌ Gagal deploy posisi baru:', err.message);
  }

  console.log('==================================================');
  console.log('🎉 MIGRASI KE SKENARIO A SELESAI.');
  console.log('==================================================');
}

executeScenarioA().catch(console.error);
