const DLMM = require('@meteora-ag/dlmm').default || require('@meteora-ag/dlmm');
const { PublicKey, sendAndConfirmTransaction } = require('@solana/web3.js');
const BN = require('bn.js');
const WalletManager = require('./src/wallet');

async function testSwap() {
  const w = new WalletManager();
  const p = await DLMM.create(w.connection, new PublicKey('ARwi1S4DaiTG5DX7S4M4ZsrXqpMD1MrTmbu9ue2tpmEq'));
  
  // swap USDC to USDT
  // Token X is USDC, Token Y is USDT
  // We want to give X, get Y. So swapForY = true.
  const swapForY = true;
  const inAmount = new BN(1000000); // 1 USDC
  
  console.log('Fetching bin arrays for swap...');
  const binArrays = await p.getBinArrayForSwap(swapForY, 4);
  console.log('Got bin arrays:', binArrays.length);
  
  const quote = p.swapQuote(inAmount, swapForY, new BN(50), binArrays);
  console.log('Quote out amount:', quote.outAmount.toString());
  
  const USDC_MINT = new PublicKey('EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v');
  const USDT_MINT = new PublicKey('Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB');
  
  const swapTx = await p.swap({
    inToken: USDC_MINT,
    outToken: USDT_MINT,
    inAmount,
    minOutAmount: quote.minOutAmount,
    lbPair: p.pubkey,
    user: w.publicKey,
    binArraysPubkey: quote.binArraysPubkey
  });
  
  console.log('Executing test swap of 1 USDC...');
  const sig = await sendAndConfirmTransaction(w.connection, swapTx, [w.keypair]);
  console.log('Swap Success! Sig:', sig);
}
testSwap().catch(console.error);
