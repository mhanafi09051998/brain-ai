const { Connection, Keypair, PublicKey, sendAndConfirmTransaction } = require('@solana/web3.js');
const { getAssociatedTokenAddress, getAccount } = require('@solana/spl-token');
const DLMM = require('@meteora-ag/dlmm').default || require('@meteora-ag/dlmm');
const { StrategyType } = require('@meteora-ag/dlmm');
const BN = require('bn.js');

const WalletManager = require('./src/wallet');
const JupiterClient = require('./src/jupiter');

const USDC_MINT = new PublicKey('EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v');
const USDT_MINT = new PublicKey('Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB');
const USDC_USDT_POOL_ADDRESS = 'ARwi1S4DaiTG5DX7S4M4ZsrXqpMD1MrTmbu9ue2tpmEq';

async function deployAutoAll() {
  const wallet = new WalletManager();
  const jupiter = new JupiterClient();
  const connection = wallet.connection;
  const userPubkey = wallet.keypair.publicKey;

  console.log('==================================================');
  console.log('🤖 AUTO-PREPARATION & DEPLOYMENT INITIATED');
  console.log('Wallet:', userPubkey.toBase58());
  console.log('==================================================');

  // 1. SWAP USDC -> SOL UNTUK RENT & GAS (Biaya aman)
  console.log('\n[Tahap 1] Mengamankan Gas & Rent (Swap 15 USDC -> SOL)...');
  const quoteSol = await jupiter.getQuote({ inputToken: 'USDC', outputToken: 'SOL', amount: 15, slippageBps: 200 });
  if (quoteSol.success) {
    const swapSol = await jupiter.executeSwap({ quoteResponse: quoteSol.quoteResponse, keypair: wallet.keypair, connection });
    console.log('✅ Gas SOL Diamankan! Tx:', swapSol.txid);
  } else {
    throw new Error('Gagal mendapatkan quote SOL');
  }

  // 2. CEK SALDO USDC SISA
  console.log('\n[Tahap 2] Membelah Saldo USDC ke USDT (50:50)...');
  await new Promise(r => setTimeout(r, 5000)); // Tunggu RPC update
  const usdcAta = await getAssociatedTokenAddress(USDC_MINT, userPubkey);
  const usdcAcc = await getAccount(connection, usdcAta);
  const usdcSisa = Number(usdcAcc.amount) / 1e6;
  const usdcToSwap = Math.floor(usdcSisa / 2);
  
  console.log(`Sisa USDC: $${usdcSisa}. Menukar $${usdcToSwap} menjadi USDT...`);
  
  const quoteUsdt = await jupiter.getQuote({ inputToken: 'USDC', outputToken: 'USDT', amount: usdcToSwap, slippageBps: 50 });
  if (quoteUsdt.success) {
    const swapUsdt = await jupiter.executeSwap({ quoteResponse: quoteUsdt.quoteResponse, keypair: wallet.keypair, connection });
    console.log('✅ Saldo 50:50 Tersedia! Tx:', swapUsdt.txid);
  } else {
    throw new Error('Gagal mendapatkan quote USDT');
  }

  // 3. DEPLOY DLMM
  console.log('\n[Tahap 3] Mengeksekusi Multi-Strategy DLMM (Core + Jaring)...');
  await new Promise(r => setTimeout(r, 8000)); // Tunggu RPC update lagi
  
  const finalUsdcAcc = await getAccount(connection, usdcAta);
  const usdtAta = await getAssociatedTokenAddress(USDT_MINT, userPubkey);
  const finalUsdtAcc = await getAccount(connection, usdtAta);
  
  const finalUsdcBalance = Number(finalUsdcAcc.amount) / 1e6;
  const finalUsdtBalance = Number(finalUsdtAcc.amount) / 1e6;
  
  console.log(`Balance Tersedia | USDC: $${finalUsdcBalance} | USDT: $${finalUsdtBalance}`);

  const dlmmPool = await DLMM.create(connection, new PublicKey(USDC_USDT_POOL_ADDRESS));
  const activeBin = await dlmmPool.getActiveBin();
  console.log('Active Bin ID:', activeBin.binId, '| Live Price:', activeBin.price);

  const safeBalance = Math.min(finalUsdcBalance, finalUsdtBalance) * 0.99; // 99% safety margin
  
  const usdcCore = new BN(Math.floor((safeBalance * 0.8) * 1e6));
  const usdtCore = new BN(Math.floor((safeBalance * 0.8) * 1e6));
  const usdcJaring = new BN(Math.floor((safeBalance * 0.2) * 1e6));
  const usdtJaring = new BN(Math.floor((safeBalance * 0.2) * 1e6));

  const minBinCore = activeBin.binId - 2;
  const maxBinCore = activeBin.binId + 2;
  console.log(`\nMenyiapkan Posisi Core (80%) -> Bin ${minBinCore} to ${maxBinCore}`);
  
  const coreKeypair = Keypair.generate();
  const createCoreTx = await dlmmPool.initializePositionAndAddLiquidityByStrategy({
    positionPubKey: coreKeypair.publicKey, user: userPubkey, totalXAmount: usdcCore, totalYAmount: usdtCore,
    strategy: { maxBinId: maxBinCore, minBinId: minBinCore, strategyType: StrategyType.Spot }
  });
  const txCore = await sendAndConfirmTransaction(connection, createCoreTx, [wallet.keypair, coreKeypair], { commitment: 'confirmed' });
  console.log('✅ Core Engine Berhasil! Tx:', txCore);

  const minBinJaring = activeBin.binId - 6;
  const maxBinJaring = activeBin.binId + 6;
  console.log(`\nMenyiapkan Posisi Jaring (20%) -> Bin ${minBinJaring} to ${maxBinJaring}`);
  
  const jaringKeypair = Keypair.generate();
  const createJaringTx = await dlmmPool.initializePositionAndAddLiquidityByStrategy({
    positionPubKey: jaringKeypair.publicKey, user: userPubkey, totalXAmount: usdcJaring, totalYAmount: usdtJaring,
    strategy: { maxBinId: maxBinJaring, minBinId: minBinJaring, strategyType: StrategyType.BidAsk }
  });
  const txJaring = await sendAndConfirmTransaction(connection, createJaringTx, [wallet.keypair, jaringKeypair], { commitment: 'confirmed' });
  console.log('✅ Jaring Whale Berhasil! Tx:', txJaring);

  console.log('\n==================================================');
  console.log('🎉 SEMUA TUGAS SELESAI. UANG ANDA SEDANG BEKERJA.');
  console.log('==================================================');
}

deployAutoAll().catch(console.error);
