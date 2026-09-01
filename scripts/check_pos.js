const WalletManager = require('./src/wallet');
const DLMM = require('@meteora-ag/dlmm').default || require('@meteora-ag/dlmm');
const { PublicKey } = require('@solana/web3.js');
async function check() {
  const w = new WalletManager();
  const conn = w.connection;
  const p = await DLMM.create(conn, new PublicKey('ARwi1S4DaiTG5DX7S4M4ZsrXqpMD1MrTmbu9ue2tpmEq'));
  const res = await p.getPositionsByUserAndLbPair(w.publicKey);
  console.log('Total positions:', res.userPositions.length);
  res.userPositions.forEach((pos, i) => {
    let tX = 0, tY = 0;
    pos.positionData.positionBinData.forEach(b => {
       tX += Number(b.binXAmount); tY += Number(b.binYAmount);
    });
    console.log(`[Pos ${i}] ${pos.publicKey.toBase58()} | X: ${tX} | Y: ${tY}`);
  });
}
check().catch(console.error);
