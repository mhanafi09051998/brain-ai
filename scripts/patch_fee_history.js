const fs = require('fs');

// 1. Patch dlmm.js — add fee history snapshot logging
const dlmmPath = '/home/ubuntu/apps/solana-trading-engine/src/dlmm.js';
let dlmm = fs.readFileSync(dlmmPath, 'utf8');

// Add fee history path after dataPath
if (!dlmm.includes('feeHistoryPath')) {
  dlmm = dlmm.replace(
    "this.dataPath = path.resolve(__dirname, '../data/dlmm_state.json');",
    `this.dataPath = path.resolve(__dirname, '../data/dlmm_state.json');
    this.feeHistoryPath = path.resolve(__dirname, '../data/fee_history.json');`
  );

  // Add fee snapshot method after saveState
  const snapshotMethod = `

  appendFeeSnapshot(feeUsd, capitalUsd) {
    try {
      let history = [];
      if (fs.existsSync(this.feeHistoryPath)) {
        history = JSON.parse(fs.readFileSync(this.feeHistoryPath, 'utf8')) || [];
      }
      const now = Date.now();
      // Only append if 5 min since last entry
      if (history.length === 0 || (now - history[history.length - 1].ts) >= 300000) {
        history.push({ ts: now, fee: feeUsd, cap: capitalUsd });
        // Keep max 30 days (8640 entries at 5 min intervals)
        if (history.length > 8640) history = history.slice(-8640);
        fs.writeFileSync(this.feeHistoryPath, JSON.stringify(history), 'utf8');
      }
    } catch (e) {}
  }`;

  dlmm = dlmm.replace(
    '  saveState() {',
    snapshotMethod + '\n\n  saveState() {'
  );

  // Call appendFeeSnapshot after saving state in syncOnChainMeteora
  dlmm = dlmm.replace(
    "this.poolState.onChainSynced = true;\n      this.saveState();",
    `this.poolState.onChainSynced = true;
      this.saveState();
      this.appendFeeSnapshot(this.poolState.totalFeeEarnedUsd, this.poolState.totalCapitalUsd);`
  );

  fs.writeFileSync(dlmmPath, dlmm);
  console.log('✅ dlmm.js patched with fee history tracking');
} else {
  console.log('⏭️ dlmm.js already patched');
}

// 2. Initialize fee_history.json with current state
const stateFile = '/home/ubuntu/apps/solana-trading-engine/data/dlmm_state.json';
const histFile = '/home/ubuntu/apps/solana-trading-engine/data/fee_history.json';
if (!fs.existsSync(histFile)) {
  const st = JSON.parse(fs.readFileSync(stateFile, 'utf8'));
  const seed = [{ ts: Date.now(), fee: st.totalFeeEarnedUsd || 0, cap: st.totalCapitalUsd || 0 }];
  fs.writeFileSync(histFile, JSON.stringify(seed), 'utf8');
  console.log('✅ fee_history.json initialized');
}

// 3. Add initialCapitalUsd to dlmm_state.json if not present
const state = JSON.parse(fs.readFileSync(stateFile, 'utf8'));
if (!state.initialCapitalUsd) {
  state.initialCapitalUsd = 932.40;
  fs.writeFileSync(stateFile, JSON.stringify(state, null, 2), 'utf8');
  console.log('✅ initialCapitalUsd set in dlmm_state.json');
}

console.log('Done!');
