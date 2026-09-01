const { Connection, Keypair, PublicKey, sendAndConfirmTransaction } = require('@solana/web3.js');
const DLMM = require('@meteora-ag/dlmm').default || require('@meteora-ag/dlmm');
const { StrategyType } = require('@meteora-ag/dlmm');
const BN = require('bn.js');
const WalletManager = require('./src/wallet');
require('dotenv').config();

const SOL_USDC_POOL_ADDRESS = '2QdhepnKRTLjjSqRo1HM5RTddvHHRWncL6p75N51RryP'; // Meteora DLMM 

async function openDlmmPosition() {
  const w = new WalletManager();
  const keypair = w.keypair;
  const userPubkey = keypair.publicKey;

  console.log('==================================================');
  console.log('🚀 OPENING METEORA DLMM POSITION ON SOLANA MAINNET');
  console.log('Wallet:', userPubkey.toBase58());
  console.log('==================================================');

  const connection = w.connection;
  const poolKey = new PublicKey(SOL_USDC_POOL_ADDRESS);
  const dlmmPool = await DLMM.create(connection, poolKey);

  const activeBin = await dlmmPool.getActiveBin();
  console.log('Active Bin ID:', activeBin.binId, '| Live Price:', activeBin.price);

  // Strategy Spot Curve / Spot
  const minBinId = activeBin.binId - 40;
  const maxBinId = activeBin.binId + 40;

  console.log(`Setting Liquidity Range: Bin ${minBinId} to Bin ${maxBinId} (Span: 80 Bins)`);

  const totalXAmount = new BN(Math.floor(4.67 * 1e9));      // 4.67 SOL
  const totalYAmount = new BN(Math.floor(477.0 * 1e6));     // 477 USDC

  const newPositionKeypair = Keypair.generate();
  console.log('Generated Position Keypair:', newPositionKeypair.publicKey.toBase58());

  console.log('1. Constructing initializePositionAndAddLiquidityByStrategy (StrategyType.Spot)...');
  const createPositionTx = await dlmmPool.initializePositionAndAddLiquidityByStrategy({
    positionPubKey: newPositionKeypair.publicKey,
    user: userPubkey,
    totalXAmount,
    totalYAmount,
    strategy: {
      maxBinId,
      minBinId,
      strategyType: StrategyType.Spot
    }
  });

  console.log('2. Signing and broadcasting transaction to Solana Mainnet...');
  const txHash = await sendAndConfirmTransaction(
    connection,
    createPositionTx,
    [keypair, newPositionKeypair],
    { skipPreflight: false, commitment: 'confirmed' }
  );

  console.log('==================================================');
  console.log('🎉 SUCCESS! Position Opened on Solana Mainnet!');
  console.log('Transaction Signature :', txHash);
  console.log('Position Public Key   :', newPositionKeypair.publicKey.toBase58());
  console.log('==================================================');
}

openDlmmPosition().catch(err => {
  console.error('❌ Execution Error:', err.message);
});
