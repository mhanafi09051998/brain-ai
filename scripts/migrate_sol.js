const fs = require('fs');
const path = '/home/ubuntu/apps/solana-trading-engine/data/dlmm_state.json';

try {
  let state = JSON.parse(fs.readFileSync(path, 'utf8'));
  
  state.pair = "SOL/USDC";
  state.poolAddress = "2QdhepnKRTLjjSqRo1HM5RTddvHHRWncL6p75N51RryP"; // Real DLMM SOL/USDC address
  state.totalCapitalUsd = 949.98;
  state.initialCapitalUsd = 949.98;
  
  // Update wallet balances to reflect the split
  // They have ~0.05 SOL currently for gas. We'll add 3.27 SOL for the pool.
  state.walletSolBalance = 3.32; 
  state.walletUsdcBalance = 475.00;
  state.walletUsdtBalance = 0;
  state.totalFeeEarnedUsd = 0;
  state.currentEquityUsd = 949.98;
  
  // Reset last sync
  state.lastSyncTime = Date.now();
  
  fs.writeFileSync(path, JSON.stringify(state, null, 2), 'utf8');
  console.log('Migrated dlmm_state.json to SOL/USDC');
  
  // Clear fee history
  const histPath = '/home/ubuntu/apps/solana-trading-engine/data/fee_history.json';
  fs.writeFileSync(histPath, JSON.stringify([{ ts: Date.now(), fee: 0, cap: 949.98 }]), 'utf8');
  console.log('Cleared fee_history.json');
  
} catch (e) {
  console.error(e);
}
