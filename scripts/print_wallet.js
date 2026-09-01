const WalletManager = require('./src/wallet');
const w = new WalletManager();
console.log('Wallet:', w.publicKey.toBase58());
