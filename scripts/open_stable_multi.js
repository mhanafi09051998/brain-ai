const bs58 = require('bs58').default || require('bs58');
const { Connection, Keypair, PublicKey, sendAndConfirmTransaction } = require('@solana/web3.js');
const { getAssociatedTokenAddress, getAccount } = require('@solana/spl-token');
const DLMM = require('@meteora-ag/dlmm').default || require('@meteora-ag/dlmm');
const { StrategyType } = require('@meteora-ag/dlmm');
const BN = require('bn.js');

const USDC_USDT_POOL_ADDRESS = 'ARwi1S4DaiTG5DX7S4M4ZsrXqpMD1MrTmbu9ue2tpmEq'; // Meteora DLMM USDC/USDT
const USDC_MINT = new PublicKey('EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v');
const USDT_MINT = new PublicKey('Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB');

async function openStableMultiStrategy() {
  // Gunakan key yang sama dengan bot (harap ganti dengan sistem env yang lebih aman jika produksi)
  const secret = 'mHwmzEZq5oNN9M1VdSCMZDfsLEXyWDzLNPyH2o9DfjdbkvNUivUr4a2HoXzrjvcZ87CJjCpbKCxdaUNGyrSaxPB';
  const decodeFn = bs58.decode ? bs58.decode : bs58;
  const keypair = Keypair.fromSecretKey(decodeFn(secret));
  const userPubkey = keypair.publicKey;

  console.log('==================================================');
  console.log('🚀 DEPLOYING STABLECOIN MULTI-STRATEGY (USDC/USDT)');
  console.log('Wallet:', userPubkey.toBase58());
  console.log('==================================================');

  const connection = new Connection('https://api.mainnet-beta.solana.com', 'confirmed');
  
  // Ambil saldo SOL (hanya dicek untuk gas)
  const solBalance = await connection.getBalance(userPubkey) / 1e9;
  console.log(`Saldo SOL (Gas) : ${solBalance} SOL`);
  if (solBalance < 0.02) {
    throw new Error('Saldo SOL terlalu rendah untuk membayar Gas (Minimal 0.02 SOL)');
  }

  // Ambil saldo USDC & USDT
  let usdcBalance = 0;
  let usdtBalance = 0;
  try {
    const usdcAta = await getAssociatedTokenAddress(USDC_MINT, userPubkey);
    const usdcAcc = await getAccount(connection, usdcAta);
    usdcBalance = Number(usdcAcc.amount) / 1e6;
    
    const usdtAta = await getAssociatedTokenAddress(USDT_MINT, userPubkey);
    const usdtAcc = await getAccount(connection, usdtAta);
    usdtBalance = Number(usdtAcc.amount) / 1e6;
  } catch (e) {
    console.log('Warning: Gagal mengambil saldo token (Mungkin ATA belum dibuat)');
  }
  
  console.log(`Saldo USDC      : $${usdcBalance}`);
  console.log(`Saldo USDT      : $${usdtBalance}`);

  if (usdcBalance < 1 || usdtBalance < 1) {
    console.log('⚠️ Saldo USDC/USDT terlalu kecil untuk dibagi. Memasukkan dummy amounts untuk testing / pastikan Anda topup.');
    usdcBalance = 100; // Contoh statis jika 0
    usdtBalance = 100;
  }

  const dlmmPool = await DLMM.create(connection, new PublicKey(USDC_USDT_POOL_ADDRESS));
  const activeBin = await dlmmPool.getActiveBin();
  console.log('\nTitik Tengah (Active Bin ID):', activeBin.binId, '| Live Price:', activeBin.price);

  // Perhitungan Alokasi (80% Core, 20% Jaring)
  const usdcCore = new BN(Math.floor((usdcBalance * 0.8) * 1e6));
  const usdtCore = new BN(Math.floor((usdtBalance * 0.8) * 1e6));
  const usdcJaring = new BN(Math.floor((usdcBalance * 0.2) * 1e6));
  const usdtJaring = new BN(Math.floor((usdtBalance * 0.2) * 1e6));

  console.log('\n--- EKSKUSI 1: CORE ENGINE (80%) ---');
  const minBinCore = activeBin.binId - 2;
  const maxBinCore = activeBin.binId + 2;
  console.log(`Range: Bin ${minBinCore} to ${maxBinCore} (Super Ketat)`);
  
  const corePositionKeypair = Keypair.generate();
  console.log('Membangun transaksi Core...');
  const createCoreTx = await dlmmPool.initializePositionAndAddLiquidityByStrategy({
    positionPubKey: corePositionKeypair.publicKey,
    user: userPubkey,
    totalXAmount: usdcCore,
    totalYAmount: usdtCore,
    strategy: { maxBinId: maxBinCore, minBinId: minBinCore, strategyType: StrategyType.Spot }
  });

  console.log('Menyiarkan transaksi Core ke Blockchain...');
  const txHashCore = await sendAndConfirmTransaction(connection, createCoreTx, [keypair, corePositionKeypair], { skipPreflight: false, commitment: 'confirmed' });
  console.log('✅ Core Engine Aktif! Tx:', txHashCore);

  console.log('\n--- EKSKUSI 2: JARING WHALE (20%) ---');
  const minBinJaring = activeBin.binId - 5;
  const maxBinJaring = activeBin.binId + 5;
  console.log(`Range: Bin ${minBinJaring} to ${maxBinJaring} (Melebar - BidAsk)`);
  
  const jaringPositionKeypair = Keypair.generate();
  console.log('Membangun transaksi Jaring...');
  const createJaringTx = await dlmmPool.initializePositionAndAddLiquidityByStrategy({
    positionPubKey: jaringPositionKeypair.publicKey,
    user: userPubkey,
    totalXAmount: usdcJaring,
    totalYAmount: usdtJaring,
    strategy: { maxBinId: maxBinJaring, minBinId: minBinJaring, strategyType: StrategyType.BidAsk }
  });

  console.log('Menyiarkan transaksi Jaring ke Blockchain...');
  const txHashJaring = await sendAndConfirmTransaction(connection, createJaringTx, [keypair, jaringPositionKeypair], { skipPreflight: false, commitment: 'confirmed' });
  console.log('✅ Jaring Whale Aktif! Tx:', txHashJaring);

  console.log('\n==================================================');
  console.log('🎉 DEPLOYMENT SELESAI!');
  console.log('Solana Gas Fee (SOL) diamankan di dompet.');
  console.log('==================================================');
}

openStableMultiStrategy().catch(err => {
  console.error('\n❌ Execution Error:', err.message);
});
