const { Connection, PublicKey, sendAndConfirmTransaction } = require('@solana/web3.js');
const { getAssociatedTokenAddress, getAccount } = require('@solana/spl-token');
const DLMM = require('@meteora-ag/dlmm').default || require('@meteora-ag/dlmm');
const { StrategyType } = require('@meteora-ag/dlmm');
const BN = require('bn.js');
const WalletManager = require('./src/wallet');

const USDC_USDT_POOL_ADDRESS = 'ARwi1S4DaiTG5DX7S4M4ZsrXqpMD1MrTmbu9ue2tpmEq';
const USDC_MINT = new PublicKey('EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v');
const USDT_MINT = new PublicKey('Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB');

async function deployCustom() {
  const wallet = new WalletManager();
  const connection = wallet.connection;
  const userPubkey = wallet.keypair.publicKey;

  console.log('==================================================');
  console.log('📉 DEPLOYING CUSTOM NET ($0.9995 - $1.0000)');
  console.log('==================================================');

  const dlmmPool = await DLMM.create(connection, new PublicKey(USDC_USDT_POOL_ADDRESS));
  
  const usdcAta = await getAssociatedTokenAddress(USDC_MINT, userPubkey);
  const usdcAcc = await getAccount(connection, usdcAta);
  const usdcBal = Number(usdcAcc.amount) / 1e6;
  
  const usdtAta = await getAssociatedTokenAddress(USDT_MINT, userPubkey);
  const usdtAcc = await getAccount(connection, usdtAta);
  const usdtBal = Number(usdtAcc.amount) / 1e6;

  console.log(`Saldo Dompet | USDC: $${usdcBal.toFixed(4)} | USDT: $${usdtBal.toFixed(4)}`);

  const activeBin = await dlmmPool.getActiveBin();
  console.log(`Active Bin ID: ${activeBin.binId}`);
  
  // Karena user ingin batas atas $1.0000, kita set dari Bin -5 hingga Bin 0
  const minBin = activeBin.binId - 5;
  const maxBin = activeBin.binId;
  
  // Kita deposit maksimal USDC yang ada
  const depositX = new BN(Math.floor(usdcBal * 0.995 * 1e6));
  const depositY = new BN(Math.floor(usdtBal * 0.995 * 1e6));

  console.log(`\nMenyiapkan Posisi -> Bin ${minBin} to ${maxBin}`);
  
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
    console.log(`✅ Posisi Custom: ${newPosKeypair.publicKey.toBase58()}`);
  } catch (err) {
    console.log('❌ Gagal deploy:', err.message);
  }
}

deployCustom().catch(console.error);
