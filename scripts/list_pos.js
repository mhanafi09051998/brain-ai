const WalletManager = require('./src/wallet');
const DLMM = require('@meteora-ag/dlmm').default || require('@meteora-ag/dlmm');
const { PublicKey } = require('@solana/web3.js');
async function list() {
  const w = new WalletManager();
  const p = await DLMM.create(w.connection, new PublicKey('ARwi1S4DaiTG5DX7S4M4ZsrXqpMD1MrTmbu9ue2tpmEq'));
  const res = await p.getPositionsByUserAndLbPair(w.publicKey);
  res.userPositions.forEach(x => console.log(x.publicKey.toBase58()));
}
list().catch(console.error);
