const { Connection, PublicKey } = require('@solana/web3.js');
const DLMM = require('@meteora-ag/dlmm').default || require('@meteora-ag/dlmm');
DLMM.create(new Connection('https://api.mainnet-beta.solana.com'), new PublicKey('ARwi1S4DaiTG5DX7S4M4ZsrXqpMD1MrTmbu9ue2tpmEq'))
  .then(p => p.getActiveBin())
  .then(b => console.log('ActiveBin:', b.binId, '| Price:', b.price))
  .catch(console.error);
