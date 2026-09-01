const DLMM = require('@meteora-ag/dlmm').default || require('@meteora-ag/dlmm');
const { PublicKey, sendAndConfirmTransaction } = require('@solana/web3.js');
const { getAssociatedTokenAddress, getAccount } = require('@solana/spl-token');
const { StrategyType } = require('@meteora-ag/dlmm');
const BN = require('bn.js');
const WalletManager = require('./src/wallet');

const USDC_USDT_POOL_ADDRESS = 'ARwi1S4DaiTG5DX7S4M4ZsrXqpMD1MrTmbu9ue2tpmEq';
const USDC_MINT = new PublicKey('EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v');
const USDT_MINT = new PublicKey('Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB');
const EXISTING_POS = new PublicKey('EocNHcZt3ypqasrMhvejnwojGzxcVF3MEWqzz9owLhmK');

async function addExisting() {
  const w = new WalletManager();
  const p = await DLMM.create(w.connection, new PublicKey(USDC_USDT_POOL_ADDRESS));
  
  const usdcAta = await getAssociatedTokenAddress(USDC_MINT, w.publicKey);
  let usdcAcc = await getAccount(w.connection, usdcAta);
  let usdcBal = Number(usdcAcc.amount);
  
  console.log(`USDC awal: ${usdcBal/1e6}`);
  
  // Sisakan sedikit ($1) untuk gas / dust token account
  const swapAmount = new BN(usdcBal - 1000000); 
  
  if (swapAmount.gten(1000000)) { // Swap jika lebih dari $1
    console.log(`Swapping ${swapAmount.toString()} USDC ke USDT...`);
    const binArrays = await p.getBinArrayForSwap(true, 4);
    const quote = p.swapQuote(swapAmount, true, new BN(50), binArrays);
    
    const swapTx = await p.swap({
      inToken: USDC_MINT,
      outToken: USDT_MINT,
      inAmount: swapAmount,
      minOutAmount: quote.minOutAmount,
      lbPair: p.pubkey,
      user: w.publicKey,
      binArraysPubkey: quote.binArraysPubkey
    });
    
    const sig = await sendAndConfirmTransaction(w.connection, swapTx, [w.keypair]);
    console.log(`Swap sukses! Sig: ${sig}`);
  }
  
  await new Promise(r => setTimeout(r, 5000));
  
  // Baca USDT
  const usdtAta = await getAssociatedTokenAddress(USDT_MINT, w.publicKey);
  const usdtAcc = await getAccount(w.connection, usdtAta);
  const usdtBal = Number(usdtAcc.amount);
  
  console.log(`USDT terkumpul: ${usdtBal/1e6}`);
  
  // Add ke existing position
  const activeBin = await p.getActiveBin();
  const depositX = new BN(0); // Kita cuma masukkan USDT
  const depositY = new BN(Math.floor(usdtBal * 0.99));
  
  console.log(`Memasukkan ke jaring EocN... (Bin ${activeBin.binId-5} to ${activeBin.binId})`);
  
  const addTx = await p.addLiquidityByStrategy({
    positionPubKey: EXISTING_POS,
    user: w.publicKey,
    totalXAmount: depositX,
    totalYAmount: depositY,
    strategy: { maxBinId: activeBin.binId, minBinId: activeBin.binId - 5, strategyType: StrategyType.Spot }
  });
  
  const txHash = await sendAndConfirmTransaction(w.connection, addTx, [w.keypair], { commitment: 'confirmed' });
  console.log(`✅ BERHASIL DITAMBAHKAN! Tx: ${txHash}`);
}

addExisting().catch(console.error);
