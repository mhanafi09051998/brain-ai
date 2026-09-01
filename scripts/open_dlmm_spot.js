const bs58 = require('bs58').default || require('bs58');
const { Connection, Keypair, PublicKey, sendAndConfirmTransaction } = require('@solana/web3.js');
const DLMM = require('@meteora-ag/dlmm').default || require('@meteora-ag/dlmm');
const { StrategyType } = require('@meteora-ag/dlmm');
const BN = require('bn.js');

const SOL_USDC_POOL_ADDRESS = 'BVRbyLjjfSBcoyiYFuxbgKYnWuiFaF9CSXEa5vdSZ9Hh'; // Meteora DLMM 20bps

async function openDlmmPosition() {
  const secret = 'mHwmzEZq5oNN9M1VdSCMZDfsLEXyWDzLNPyH2o9DfjdbkvNUivUr4a2HoXzrjvcZ87CJjCpbKCxdaUNGyrSaxPB';
  const decodeFn = bs58.decode ? bs58.decode : bs58;
  const keypair = Keypair.fromSecretKey(decodeFn(secret));
  const userPubkey = keypair.publicKey;

  console.log('==================================================');
  console.log('🚀 OPENING METEORA DLMM POSITION ON SOLANA MAINNET');
  console.log('Wallet:', userPubkey.toBase58());
  console.log('==================================================');

  const connection = new Connection('https://api.mainnet-beta.solana.com', 'confirmed');
  const poolKey = new PublicKey(SOL_USDC_POOL_ADDRESS);
  const dlmmPool = await DLMM.create(connection, poolKey);

  const activeBin = await dlmmPool.getActiveBin();
  console.log('Active Bin ID:', activeBin.binId, '| Live Price:', activeBin.price);

  // Strategy Spot Curve / Spot
  const minBinId = activeBin.binId - 25;
  const maxBinId = activeBin.binId + 25;

  console.log(`Setting Liquidity Range: Bin ${minBinId} to Bin ${maxBinId} (Span: 50 Bins)`);

  const totalXAmount = new BN(Math.floor(4.0 * 1e9));      // 4.0 SOL
  const totalYAmount = new BN(Math.floor(400.0 * 1e6));    // 400 USDC

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
  console.log(`Solscan Explorer Link : https://solscan.io/tx/${txHash}`);
  console.log('==================================================');
}

openDlmmPosition().catch(err => {
  console.error('❌ Execution Error:', err.message);
});
