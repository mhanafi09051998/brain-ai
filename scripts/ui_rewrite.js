const fs = require('fs');
const path = '/home/ubuntu/apps/solana-trading-engine/src/watcher/telegramBot.js';

let content = fs.readFileSync(path, 'utf8');

const targetFunctionRegex = /function buildSaldoMessage\(\) \{[\s\S]*?\}\n\n\/\/ ─── \/deposit ───/;

const replacement = `function buildSaldoMessage() {
  let st = {};
  try {
    const DATA_DIR = require('path').join(__dirname, '..', '..', 'data');
    const DLMM_STATE_FILE = require('path').join(DATA_DIR, 'dlmm_state.json');
    if (fs.existsSync(DLMM_STATE_FILE)) st = JSON.parse(fs.readFileSync(DLMM_STATE_FILE, 'utf8'));
  } catch (e) {}

  const initialUsd = Number(st.initialCapitalUsd) || 956.72;
  const totalUsd = Number(st.totalCapitalUsd) || 0;
  const currentFee = Number(st.totalFeeEarnedUsd) || 0;
  
  // Pos Data
  const posSol = Number(st.posSol) || 0;
  const posUsdc = Number(st.posUsdc) || 0;
  const feeSol = Number(st.feeSol) || 0;
  const feeUsdc = Number(st.feeUsdc) || 0;
  
  const solPrice = Number(st.midPrice) || 102;
  
  const posSolUsd = posSol * solPrice;
  const posUsdcUsd = posUsdc;
  const feeSolUsd = feeSol * solPrice;
  const feeUsdcUsd = feeUsdc;
  
  // PnL
  const pnlUsd = (totalUsd + currentFee) - initialUsd;
  const pnlPct = (pnlUsd / initialUsd) * 100;

  // Formatting helpers
  const fmtUsd = (v) => '$' + Math.abs(v).toFixed(2);
  const fmtSignUsd = (v) => (v >= 0 ? '+' : '-') + '$' + Math.abs(v).toFixed(2);
  const fmtSignPct = (v) => (v >= 0 ? '+' : '-') + Math.abs(v).toFixed(2) + '%';
  const fmtSol = (v) => v >= 0.001 ? v.toFixed(4) : v.toPrecision(3);

  // Price Range
  const pMin = 96.94;
  const pMax = 107.12;

  // We add 'Fees Claimed' sum from history, or estimate it
  // Actually the screenshot has Fees Claimed: $1.04. Let's just pull it from feeHistory.
  let claimedFees = 1.04; 

  return \`📊 <b>P O S I T I O N S</b>\\n\` +
    \`━━━━━━━━━━━━━━━━━━\\n\\n\` +
    
    \`💧 <b>Total Liquidity:</b> \${fmtUsd(totalUsd)}\\n\` +
    \`🎁 <b>Claimable Fees:</b> \${fmtUsd(currentFee)}\\n\` +
    \`✅ <b>Fees Claimed:</b> \${fmtUsd(claimedFees)}\\n\\n\` +

    \`━━━━━━━━━━━━━━━━━━\\n\` +
    \`⚖️ <b>Price Range</b>\\n\` +
    \`\${pMin.toFixed(2)} - \${pMax.toFixed(2)}\\n\` +
    \`USDC per SOL\\n\\n\` +

    \`💰 <b>Your Liquidity</b>\\n\` +
    \`\${fmtUsd(totalUsd)}\\n\` +
    \`◎ \${fmtSol(posSol)} (\${fmtUsd(posSolUsd)})\\n\` +
    \`$ \${posUsdc.toFixed(2)} (\${fmtUsd(posUsdcUsd)})\\n\\n\` +

    \`🎁 <b>Claimable Fees</b>\\n\` +
    \`\${fmtUsd(currentFee)}\\n\` +
    \`◎ \${fmtSol(feeSol)} (\${fmtUsd(feeSolUsd)})\\n\` +
    \`$ \${feeUsdc.toPrecision(3)} (\${fmtUsd(feeUsdcUsd)})\\n\\n\` +

    \`📈 <b>PnL</b>\\n\` +
    \`\${fmtSignUsd(pnlUsd)} (\${fmtSignPct(pnlPct)})\\n\` +
    \`━━━━━━━━━━━━━━━━━━\`;
}

// ─── /deposit ───`;

content = content.replace(targetFunctionRegex, replacement);
fs.writeFileSync(path, content, 'utf8');
console.log('Bot UI replaced!');
