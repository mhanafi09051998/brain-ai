const { Connection, PublicKey, Keypair, sendAndConfirmTransaction, Transaction } = require('@solana/web3.js');
const DLMM = require('@meteora-ag/dlmm');
const WalletManager = require('./src/wallet');

async function removeAndClosePosition() {
  const wallet = new WalletManager();
  const DLMMClass = DLMM.default || DLMM;
  const poolPubkey = new PublicKey('BVRbyLjjfSBcoyiYFuxbgKYnWuiFaF9CSXEa5vdSZ9Hh');
  const dlmmPool = await DLMMClass.create(wallet.connection, poolPubkey);

  const { userPositions } = await dlmmPool.getPositionsByUserAndLbPair(wallet.publicKey);
  console.log('Open positions count:', userPositions.length);

  for (const pos of userPositions) {
    console.log('Removing 100% liquidity from position:', pos.publicKey.toBase58());
    
    // Remove 100% liquidity (bps = 10000)
    const removeLiquidityTxs = await dlmmPool.removeLiquidity({
      position: pos.publicKey,
      user: wallet.publicKey,
      binIds: pos.positionData.positionBinData.map(b => b.binId),
      bps: 10000,
      shouldClaimAndClose: true
    });

    console.log('Generated remove liquidity transactions:', removeLiquidityTxs.length || 1);
    const txList = Array.isArray(removeLiquidityTxs) ? removeLiquidityTxs : [removeLiquidityTxs];

    for (const tx of txList) {
      tx.feePayer = wallet.publicKey;
      const { blockhash } = await wallet.connection.getLatestBlockhash('confirmed');
      tx.recentBlockhash = blockhash;
      tx.sign(wallet.keypair);
      
      const sig = await wallet.connection.sendRawTransaction(tx.serialize(), { skipPreflight: false });
      console.log('Sent transaction signature:', sig);
      await wallet.connection.confirmTransaction(sig, 'confirmed');
      console.log('Confirmed transaction:', sig);
    }
  }

  const finalBal = await wallet.getBalances();
  console.log('Final Balances after close -> SOL:', finalBal.sol, '| USDC:', finalBal.usdc);
}

removeAndClosePosition().catch(console.error);
