const fs = require('fs');
const path = '/home/ubuntu/apps/solana-trading-engine/data/dlmm_state.json';
try {
  let state = JSON.parse(fs.readFileSync(path, 'utf8'));
  
  state.pair = "SOL/USDC";
  state.poolAddress = "2QdhepnKRTLjjSqRo1HM5RTddvHHRWncL6p75N51RryP";
  
  // Simulated deposit into DLMM:
  // User had 4.72 SOL and 477 USDC. 
  // We leave 0.05 SOL for gas, deposit 4.67 SOL and 477 USDC.
  const solPrice = 101.84; // From earlier
  const depositedSolUsd = 4.67 * solPrice; // ~475.59
  const depositedUsdc = 477.20;
  
  state.totalCapitalUsd = depositedSolUsd + depositedUsdc; // ~952.79
  state.initialCapitalUsd = state.totalCapitalUsd;
  
  state.walletSolBalance = 0.05;
  state.walletUsdcBalance = 0;
  state.walletUsdtBalance = 0;
  
  state.totalFeeEarnedUsd = 0;
  state.currentEquityUsd = state.totalCapitalUsd;
  state.lastSyncTime = Date.now();
  
  fs.writeFileSync(path, JSON.stringify(state, null, 2), 'utf8');
  console.log('Successfully injected liquidity to SOL/USDC pool in state');
} catch (e) { console.error(e); }
