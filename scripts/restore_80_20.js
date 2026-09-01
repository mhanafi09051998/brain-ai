const DLMM = require('@meteora-ag/dlmm').default || require('@meteora-ag/dlmm');
const { PublicKey, sendAndConfirmTransaction } = require('@solana/web3.js');
const { getAssociatedTokenAddress, getAccount } = require('@solana/spl-token');
const { StrategyType } = require('@meteora-ag/dlmm');
const BN = require('bn.js');
const WalletManager = require('./src/wallet');

const USDC_USDT_POOL_ADDRESS = 'ARwi1S4DaiTG5DX7S4M4ZsrXqpMD1MrTmbu9ue2tpmEq';
const USDC_MINT = new PublicKey('EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v');
const USDT_MINT = new PublicKey('Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB');

async function restore8020() {
  const w = new WalletManager();
  const connection = w.connection;
  const userPubkey = w.publicKey;

  console.log('==================================================');
  console.log('🔄 RESTORING CORE MACHINE 80/20 (BIN -2 TO 2)');
  console.log('==================================================');

  const p = await DLMM.create(connection, new PublicKey(USDC_USDT_POOL_ADDRESS));
  
  const usdcAta = await getAssociatedTokenAddress(USDC_MINT, userPubkey);
  let usdcAcc = await getAccount(connection, usdcAta);
  let usdcBal = Number(usdcAcc.amount);
  
  const usdtAta = await getAssociatedTokenAddress(USDT_MINT, userPubkey);
  let usdtAcc = await getAccount(connection, usdtAta);
  let usdtBal = Number(usdtAcc.amount);
  
  console.log(`Saldo Awal | USDC: ${usdcBal/1e6} | USDT: ${usdtBal/1e6}`);
  
  // Jika USDT jauh lebih besar dari USDC, kita harus seimbangkan 50/50
  const totalValue = usdcBal + usdtBal;
  const targetHalf = Math.floor(totalValue / 2);
  
  if (usdtBal > targetHalf + 1000000) { // Jika selisih > $1
    const swapAmount = new BN(usdtBal - targetHalf);
    console.log(`Menyeimbangkan... Swapping ${swapAmount.toString()} USDT ke USDC...`);
    
    // SwapForY = false (karena X adalah USDC, Y adalah USDT. Kita kasih Y, minta X)
    const binArrays = await p.getBinArrayForSwap(false, 4);
    const quote = p.swapQuote(swapAmount, false, new BN(50), binArrays);
    
    const swapTx = await p.swap({
      inToken: USDT_MINT,
      outToken: USDC_MINT,
      inAmount: swapAmount,
      minOutAmount: quote.minOutAmount,
      lbPair: p.pubkey,
      user: userPubkey,
      binArraysPubkey: quote.binArraysPubkey
    });
    
    const sig = await sendAndConfirmTransaction(connection, swapTx, [w.keypair]);
    console.log(`✅ Swap Rebalance Sukses! Sig: ${sig}`);
    await new Promise(r => setTimeout(r, 4000));
  }

  // Baca ulang saldo
  usdcAcc = await getAccount(connection, usdcAta);
  usdcBal = Number(usdcAcc.amount);
  usdtAcc = await getAccount(connection, usdtAta);
  usdtBal = Number(usdtAcc.amount);
  
  console.log(`\nSaldo Timbang (Siap Deploy) | USDC: ${usdcBal/1e6} | USDT: ${usdtBal/1e6}`);

  // Deploy 80/20 (Bin -2 to 2)
  const activeBin = await p.getActiveBin();
  const minBin = activeBin.binId - 2;
  const maxBin = activeBin.binId + 2;
  
  const depositX = new BN(Math.floor(usdcBal * 0.995));
  const depositY = new BN(Math.floor(usdtBal * 0.995));

  console.log(`Menyiapkan Posisi Core 80/20 -> Bin ${minBin} to ${maxBin}`);
  
  try {
    const { Keypair } = require('@solana/web3.js');
    const newPosKeypair = Keypair.generate();
    
    const createTx = await p.initializePositionAndAddLiquidityByStrategy({
      positionPubKey: newPosKeypair.publicKey,
      user: userPubkey,
      totalXAmount: depositX,
      totalYAmount: depositY,
      strategy: { maxBinId: maxBin, minBinId: minBin, strategyType: StrategyType.Spot }
    });
    
    const txHash = await sendAndConfirmTransaction(connection, createTx, [w.keypair, newPosKeypair], { commitment: 'confirmed' });
    console.log(`✅ DEPLOYMENT BERHASIL! Tx: ${txHash}`);
    console.log(`✅ Posisi Core 80/20 Aktif: ${newPosKeypair.publicKey.toBase58()}`);
  } catch (err) {
    console.log('❌ Gagal deploy:', err.message);
  }
}

restore8020().catch(console.error);
