const fs = require('fs');

const path = '/home/ubuntu/apps/solana-trading-engine/data/dlmm_state.json';
let state = JSON.parse(fs.readFileSync(path, 'utf8'));

// The user's total capital at the start of SOL/USDC:
// Pool: $951.15
// Idle: $0.34
// Gas (0.0513 SOL): ~$5.23
// Total: 956.72

state.initialCapitalUsd = 956.72;

fs.writeFileSync(path, JSON.stringify(state, null, 2), 'utf8');
console.log('Fixed initial capital in state file');
