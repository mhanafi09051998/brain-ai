const WalletManager = require('./src/wallet');
async function checkSol() {
  const w = new WalletManager();
  const bal = await w.connection.getBalance(w.keypair.publicKey);
  console.log('SOL:', bal / 1e9);
}
checkSol().catch(console.error);
