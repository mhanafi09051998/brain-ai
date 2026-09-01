const DLMM = require('@meteora-ag/dlmm').default || require('@meteora-ag/dlmm');
const { Connection, PublicKey } = require('@solana/web3.js');
async function run() {
  const conn = new Connection('https://api.mainnet-beta.solana.com');
  const p = await DLMM.create(conn, new PublicKey('ARwi1S4DaiTG5DX7S4M4ZsrXqpMD1MrTmbu9ue2tpmEq'));
  console.log('Mint X:', p.lbPair.tokenXMint.toBase58());
  console.log('Mint Y:', p.lbPair.tokenYMint.toBase58());
}
run().catch(console.error);
