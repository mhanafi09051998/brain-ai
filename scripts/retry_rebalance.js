const WalletManager = require('./src/wallet');
const JupiterClient = require('./src/jupiter');
require('dotenv').config();

async function run() {
  const w = new WalletManager();
  const jup = new JupiterClient();
  const bal = await w.getBalances();
  
  console.log(`Initial: SOL=${bal.sol}, USDC=${bal.usdc}`);
  
  const qPrice = await jup.getQuote({ inputToken: 'SOL', outputToken: 'USDC', amount: 0.1, slippageBps: 200 });
  if (!qPrice.success) return console.log('Failed to get price quote');
  
  const solPrice = Number(qPrice.quoteResponse.outAmount) / 1e6 / 0.1;
  const gasReserve = 0.05;
  const availableSol = bal.sol - gasReserve;
  if (availableSol <= 0) return console.log('Not enough SOL');
  
  const totalValue = (availableSol * solPrice) + bal.usdc;
  const targetUsdc = totalValue / 2;
  const diff = bal.usdc - targetUsdc;
  
  if (Math.abs(diff) < 2) return console.log('Already balanced!');
  
  console.log(`Retrying Swap with Max Priority Fee...`);
  if (diff > 0) {
    const swapAmount = diff; 
    console.log(`Swapping $${swapAmount.toFixed(2)} USDC to SOL...`);
    const q = await jup.getQuote({ inputToken: 'USDC', outputToken: 'SOL', amount: swapAmount, slippageBps: 200 });
    const res = await jup.executeSwap({ 
      quoteResponse: q.quoteResponse, 
      keypair: w.keypair, 
      connection: w.connection,
      priorityFee: 500000 // 0.0005 SOL priority fee
    });
    console.log('Swap result:', res.success ? res.txid : res.error);
  } else {
    const swapAmountSol = Math.abs(diff) / solPrice;
    console.log(`Swapping ${swapAmountSol.toFixed(4)} SOL to USDC...`);
    const q = await jup.getQuote({ inputToken: 'SOL', outputToken: 'USDC', amount: swapAmountSol, slippageBps: 200 });
    const res = await jup.executeSwap({ 
      quoteResponse: q.quoteResponse, 
      keypair: w.keypair, 
      connection: w.connection,
      priorityFee: 500000
    });
    console.log('Swap result:', res.success ? res.txid : res.error);
  }
}

run().catch(console.error);
