const DLMM = require('@meteora-ag/dlmm').default || require('@meteora-ag/dlmm');
const { PublicKey } = require('@solana/web3.js');
const WalletManager = require('./src/wallet');

async function verify() {
  const w = new WalletManager();
  const dlmmPool = await DLMM.create(w.connection, new PublicKey('ARwi1S4DaiTG5DX7S4M4ZsrXqpMD1MrTmbu9ue2tpmEq'));
  const { userPositions } = await dlmmPool.getPositionsByUserAndLbPair(w.publicKey);
  
  console.log(`\n=== VERIFIKASI AKHIR ON-CHAIN ===`);
  console.log(`Total Posisi Aktif: ${userPositions.length}`);
  
  userPositions.forEach((pos, i) => {
    let tX = 0, tY = 0;
    pos.positionData.positionBinData.forEach(b => {
      // In DLMM, positionBinAmount is the user's amount of LP tokens for that bin
      // We will just print the bounds and fee
      tX += Number(b.positionFeeXAmount || 0);
      tY += Number(b.positionFeeYAmount || 0);
    });
    const minBin = pos.positionData.lowerBinId;
    const maxBin = pos.positionData.upperBinId;
    
    console.log(`\n[Posisi ${i+1}] ${pos.publicKey.toBase58()}`);
    console.log(`-> Rentang: Bin ${minBin} hingga Bin ${maxBin}`);
    console.log(`-> Keterangan: Ini adalah ${maxBin - minBin === 4 ? 'CORE 80/20' : (maxBin - minBin === 12 ? 'WHALE NET' : 'CUSTOM NET')} (${(maxBin-minBin)+1} Bins)`);
    console.log(`-> Status: AKTIF di Meteora`);
  });
  console.log(`=================================\n`);
}
verify().catch(console.error);
