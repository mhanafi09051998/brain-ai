const WalletManager = require('./src/wallet');
const JupiterClient = require('./src/jupiter');
require('dotenv').config();

async function run() {
  const w = new WalletManager();
  const jup = new JupiterClient();
  const bal = await w.getBalances();
  
  console.log(`Initial: SOL=${bal.sol}, USDC=${bal.usdc}`);
  
  // Get SOL price
  const qPrice = await jup.getQuote({ inputToken: 'SOL', outputToken: 'USDC', amount: 0.1, slippageBps: 100 });
  if (!qPrice.success) return console.log('Failed to get price quote');
  
  const solPrice = Number(qPrice.quoteResponse.outAmount) / 1e6 / 0.1;
  console.log(`Current SOL Price: $${solPrice.toFixed(2)}`);
  
  const gasReserve = 0.05;
  const availableSol = bal.sol - gasReserve;
  if (availableSol <= 0) return console.log('Not enough SOL for balancing');
  
  const solUsdValue = availableSol * solPrice;
  const usdcValue = bal.usdc;
  
  const totalValue = solUsdValue + usdcValue;
  const targetUsdc = totalValue / 2;
  
  const diff = usdcValue - targetUsdc;
  
  if (Math.abs(diff) < 2) {
    return console.log('Already balanced!');
  }
  
  if (diff > 0) {
    // We have too much USDC, need to buy SOL
    const swapAmount = diff; // in USDC
    console.log(`Swapping $${swapAmount.toFixed(2)} USDC to SOL...`);
    const q = await jup.getQuote({ inputToken: 'USDC', outputToken: 'SOL', amount: swapAmount, slippageBps: 100 });
    const res = await jup.executeSwap({ quoteResponse: q.quoteResponse, keypair: w.keypair, connection: w.connection });
    console.log('Swap result:', res.success ? res.txid : res.error);
  } else {
    // We have too much SOL, need to sell SOL
    const swapAmountSol = Math.abs(diff) / solPrice;
    console.log(`Swapping ${swapAmountSol.toFixed(4)} SOL to USDC...`);
    const q = await jup.getQuote({ inputToken: 'SOL', outputToken: 'USDC', amount: swapAmountSol, slippageBps: 100 });
    const res = await jup.executeSwap({ quoteResponse: q.quoteResponse, keypair: w.keypair, connection: w.connection });
    console.log('Swap result:', res.success ? res.txid : res.error);
  }
}

run().catch(console.error);
