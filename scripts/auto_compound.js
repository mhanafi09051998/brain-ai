const { PublicKey, sendAndConfirmTransaction } = require('@solana/web3.js');
const { getAssociatedTokenAddress, getAccount } = require('@solana/spl-token');
const DLMM = require('@meteora-ag/dlmm').default || require('@meteora-ag/dlmm');
const { StrategyType } = require('@meteora-ag/dlmm');
const BN = require('bn.js');
const WalletManager = require('./src/wallet');
const JupiterClient = require('./src/jupiter');
const fs = require('fs');
const path = require('path');

const SOL_USDC_POOL_ADDRESS = 'BVRbyLjjfSBcoyiYFuxbgKYnWuiFaF9CSXEa5vdSZ9Hh';
const USDC_MINT = new PublicKey('EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v');
const WSOL_MINT = new PublicKey('So11111111111111111111111111111111111111112');

async function autoCompound() {
  const wallet = new WalletManager();
  const connection = wallet.connection;
  const userPubkey = wallet.keypair.publicKey;

  console.log(`\n[${new Date().toISOString()}] 🚀 6-HOUR AUTO-COMPOUND STARTING...`);
  const dlmmPool = await DLMM.create(connection, new PublicKey(SOL_USDC_POOL_ADDRESS));
  
  const { userPositions } = await dlmmPool.getPositionsByUserAndLbPair(userPubkey);
  if (!userPositions || userPositions.length === 0) return console.log('Tidak ada posisi aktif.');

  // Update State Database (Accumulate Fees before claiming)
  const statePath = path.resolve(__dirname, 'data/dlmm_state.json');
  try {
    const state = JSON.parse(fs.readFileSync(statePath, 'utf8'));
    const unClaimed = state.totalFeeEarnedUsd || 0;
    if (unClaimed > 0.01) {
      state.totalFeeClaimed = (state.totalFeeClaimed || 3.31) + unClaimed;
      state.totalFeeEarnedUsd = 0; // reset local
      fs.writeFileSync(statePath, JSON.stringify(state, null, 2), 'utf8');
      console.log(`✅ Update Database Lokal: Akumulasi Total Fee Claimed = $${state.totalFeeClaimed.toFixed(2)}`);
    }
  } catch (e) {
    console.log('⚠️ Gagal update dlmm_state.json', e.message);
  }

  // 1. Claim Fees
  let feeClaimed = false;
  for (const pos of userPositions) {
    try {
      const claimTx = await dlmmPool.claimSwapFee({ position: pos, owner: userPubkey });
      const txs = Array.isArray(claimTx) ? claimTx : [claimTx];
      for (let tx of txs) {
        await sendAndConfirmTransaction(connection, tx, [wallet.keypair], { commitment: 'confirmed' });
      }
      console.log(`✅ Fee diklaim dari posisi ${pos.publicKey.toBase58()}`);
      feeClaimed = true;
    } catch (err) {
      // It's normal if there's no fee to claim or very small
    }
  }
  
  await new Promise(r => setTimeout(r, 4000));

  // 2. Check Balance
  const jup = new JupiterClient();
  const b = await wallet.getBalances();
  console.log(`Saldo Wallet: SOL ${b.sol.toFixed(4)} | USDC $${b.usdc.toFixed(2)}`);

  const qPrice = await jup.getQuote({ inputToken: 'SOL', outputToken: 'USDC', amount: 0.1, slippageBps: 100 });
  if (!qPrice.success) return console.log('Gagal get price dari Jupiter');
  const solPrice = Number(qPrice.quoteResponse.outAmount) / 1e6 / 0.1;

  const gasReserve = 0.05; // 0.05 SOL untuk biaya gas operasional
  const availableSol = Math.max(0, b.sol - gasReserve);
  const solUsdValue = availableSol * solPrice;
  const usdcValue = b.usdc;

  // 3. Auto-Rebalance (Threshold diturunkan ke $1 agar responsif di siklus 6 jam)
  const diffUsd = usdcValue - solUsdValue;
  if (Math.abs(diffUsd) > 1.0) {
    console.log(`Rasio tidak seimbang. Melakukan Jupiter Rebalance...`);
    const swapTargetUsd = Math.abs(diffUsd) / 2;
    if (diffUsd > 0) {
      console.log(`Swapping $${swapTargetUsd.toFixed(2)} USDC ke SOL...`);
      const q = await jup.getQuote({ inputToken: 'USDC', outputToken: 'SOL', amount: swapTargetUsd, slippageBps: 100 });
      await jup.executeSwap({ quoteResponse: q.quoteResponse, keypair: wallet.keypair, connection });
    } else {
      const swapSolAmount = swapTargetUsd / solPrice;
      console.log(`Swapping ${swapSolAmount.toFixed(4)} SOL ke USDC...`);
      const q = await jup.getQuote({ inputToken: 'SOL', outputToken: 'USDC', amount: swapSolAmount, slippageBps: 100 });
      await jup.executeSwap({ quoteResponse: q.quoteResponse, keypair: wallet.keypair, connection });
    }
    await new Promise(r => setTimeout(r, 5000));
  }

  // 4. Reinvest ke Posisi Meteora
  const b2 = await wallet.getBalances();
  const availSolFinal = Math.max(0, b2.sol - gasReserve);
  
  // Threshold diturunkan agar fee sekecil $0.5 pun bisa di-compound
  if (availSolFinal < 0.001 && b2.usdc < 0.1) {
    return console.log('Saldo terlalu kecil untuk compound, menunggu siklus berikutnya.');
  }

  const corePosition = userPositions[0]; 
  const depositX = new BN(Math.floor(availSolFinal * 1e9)); 
  const depositY = new BN(Math.floor(b2.usdc * 1e6)); 

  console.log(`Menyuntikkan ${availSolFinal.toFixed(4)} SOL & $${b2.usdc.toFixed(2)} USDC ke LP Meteora...`);
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
      console.log('✅ SNOWBALL COMPOUND BERHASIL DIAKTIFKAN!');
    }
  } catch (err) {
    console.log('❌ Gagal Reinvestasi:', err.message);
  }
}
autoCompound().catch(console.error);
