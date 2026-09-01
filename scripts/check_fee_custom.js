const DLMM = require('@meteora-ag/dlmm').default || require('@meteora-ag/dlmm');
const { PublicKey } = require('@solana/web3.js');
const WalletManager = require('./src/wallet');

async function checkFees() {
  const w = new WalletManager();
  const dlmmPool = await DLMM.create(w.connection, new PublicKey('ARwi1S4DaiTG5DX7S4M4ZsrXqpMD1MrTmbu9ue2tpmEq'));
  const { userPositions } = await dlmmPool.getPositionsByUserAndLbPair(w.publicKey);
  
  if (userPositions.length === 0) {
    return console.log('Tidak ada posisi ditemukan.');
  }

  // Cari posisi EocN (rentang -5 to 0)
  const pos = userPositions.find(p => p.publicKey.toBase58() === 'EocNHcZt3ypqasrMhvejnwojGzxcVF3MEWqzz9owLhmK') || userPositions[0];
  
  let feeX = 0, feeY = 0;
  pos.positionData.positionBinData.forEach(b => {
    feeX += Number(b.positionFeeXAmount || 0);
    feeY += Number(b.positionFeeYAmount || 0);
  });

  console.log(`USDC_FEE: ${feeX / 1e6}`);
  console.log(`USDT_FEE: ${feeY / 1e6}`);
}
checkFees().catch(console.error);
