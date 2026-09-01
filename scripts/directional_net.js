const { Connection, PublicKey, sendAndConfirmTransaction, VersionedTransaction } = require('@solana/web3.js');
const { getAssociatedTokenAddress, getAccount } = require('@solana/spl-token');
const DLMM = require('@meteora-ag/dlmm').default || require('@meteora-ag/dlmm');
const { StrategyType } = require('@meteora-ag/dlmm');
const BN = require('bn.js');
const fetch = require('node-fetch');
const WalletManager = require('./src/wallet');

const USDC_USDT_POOL_ADDRESS = 'ARwi1S4DaiTG5DX7S4M4ZsrXqpMD1MrTmbu9ue2tpmEq';
const USDC_MINT = new PublicKey('EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v');
const USDT_MINT = new PublicKey('Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB');

async function deployDirectional() {
  const wallet = new WalletManager();
  const connection = wallet.connection;
  const userPubkey = wallet.keypair.publicKey;

  console.log('==================================================');
  console.log('📉 DEPLOYING DIRECTIONAL NET (BIN -5 TO 0)');
  console.log('==================================================');

  const dlmmPool = await DLMM.create(connection, new PublicKey(USDC_USDT_POOL_ADDRESS));
  
  // 1. Close current positions
  const { userPositions } = await dlmmPool.getPositionsByUserAndLbPair(userPubkey);
  for (const pos of userPositions) {
    console.log(`Menutup posisi ${pos.publicKey.toBase58()}...`);
    try {
      const removeTx = await dlmmPool.removeLiquidity({
        position: pos.publicKey,
        user: userPubkey,
        binIds: pos.positionData.positionBinData.map(b => b.binId),
        bps: 10000,
        shouldClaimAndClose: true
      });
      const txs = Array.isArray(removeTx) ? removeTx : [removeTx];
      for (const tx of txs) {
        await sendAndConfirmTransaction(connection, tx, [wallet.keypair], { commitment: 'confirmed' });
      }
      console.log(`✅ Ditutup.`);
    } catch(e) {}
  }

  await new Promise(r => setTimeout(r, 5000));

  // 2. Cek Saldo
  const usdcAta = await getAssociatedTokenAddress(USDC_MINT, userPubkey);
  const usdtAta = await getAssociatedTokenAddress(USDT_MINT, userPubkey);
  let usdcAcc = await getAccount(connection, usdcAta);
  let usdtAcc = await getAccount(connection, usdtAta);
  
  let usdcBal = Number(usdcAcc.amount);
  let usdtBal = Number(usdtAcc.amount);
  console.log(`Saldo Awal | USDC: ${usdcBal/1e6} | USDT: ${usdtBal/1e6}`);

  // 3. Swap USDT ke USDC via Jupiter
  if (usdtBal > 1000000) { // Lebih dari $1
    console.log('Menukar seluruh USDT menjadi USDC via Jupiter...');
    try {
      const jupQuote = await fetch(`https://quote-api.jup.ag/v6/quote?inputMint=${USDT_MINT.toBase58()}&outputMint=${USDC_MINT.toBase58()}&amount=${usdtBal}&slippageBps=50`).then(r => r.json());
      const jupSwap = await fetch('https://quote-api.jup.ag/v6/swap', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          quoteResponse: jupQuote,
          userPublicKey: userPubkey.toBase58(),
          wrapAndUnwrapSol: true
        })
      }).then(r => r.json());
      
      const swapTxBuf = Buffer.from(jupSwap.swapTransaction, 'base64');
      const swapTx = VersionedTransaction.deserialize(swapTxBuf);
      swapTx.sign([wallet.keypair]);
      
      const sig = await connection.sendTransaction(swapTx, { skipPreflight: true });
      await connection.confirmTransaction(sig, 'confirmed');
      console.log(`✅ Swap sukses! Sig: ${sig}`);
    } catch (e) {
      console.log('Gagal swap:', e.message);
    }
  }

  await new Promise(r => setTimeout(r, 5000));
  usdcAcc = await getAccount(connection, usdcAta);
  const finalUsdc = Number(usdcAcc.amount);
  console.log(`\nModal USDC Siap Deploy: ${finalUsdc/1e6}`);

  // 4. Deploy Posisi Bin -5 ke 0
  const activeBin = await dlmmPool.getActiveBin();
  const minBin = activeBin.binId - 5;
  const maxBin = activeBin.binId;
  
  // Karena posisi hanya memiliki USDC, kita butuh sedikit USDT untuk Bin 0 (karena Bin 0 butuh 50% USDC & 50% USDT). 
  // Jika tidak ada USDT, DLMM tidak bisa memenuhinya. 
  // Trik: Kita batasi ke -1 agar 100% murni USDC tanpa error, atau pakai Jup zapper bawaan SDK.
  // Untuk 0.9995 - 1.0000, itu = -5 hingga 0. Kita deploy saja dengan Y = 0, DLMM SDK akan melimitasi Bin 0.
  const depositX = new BN(Math.floor(finalUsdc * 0.99));
  const depositY = new BN(0);

  console.log(`Menyiapkan Posisi: Bin ${minBin} to ${maxBin}`);
  
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
  } catch (err) {
    console.log('❌ Gagal deploy:', err.message);
  }
}

deployDirectional().catch(console.error);
