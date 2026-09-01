const h = require('/home/ubuntu/apps/solana-trading-engine/data/fee_history.json');
const now = Date.now();

// Filter out entries with the old 4500+ bug
const clean = h.filter(e => e.cap < 1100 && e.cap > 900);

if (clean.length === 0) { console.log('No clean data'); process.exit(); }

const first = clean[0];
const last = clean[clean.length - 1];
const hoursElapsed = (last.ts - first.ts) / 3600000;

console.log('=== FEE ANALYSIS ===');
console.log('First clean entry:', new Date(first.ts).toISOString(), 'fee:', first.fee, 'cap:', first.cap);
console.log('Last entry:', new Date(last.ts).toISOString(), 'fee:', last.fee, 'cap:', last.cap);
console.log('Hours elapsed:', hoursElapsed.toFixed(2));
console.log('Clean entries:', clean.length);

// Find the max fee value in the clean dataset
const maxFee = Math.max(...clean.map(e => e.fee));
console.log('Peak claimable fee (USD):', maxFee);

// The fee resets to 0 after claims. Let's sum up the "peaks before reset"
// A reset is when fee drops significantly (e.g. from 0.2 to 0)
let totalAccumulated = 0;
let prevFee = 0;
for (const e of clean) {
  if (e.fee < prevFee - 0.01) {
    // A claim/reset happened, the previous peak was accumulated
    totalAccumulated += prevFee;
  }
  prevFee = e.fee;
}
// Add current unclaimed fee
totalAccumulated += last.fee;

console.log('Total accumulated fee (including claims):', totalAccumulated.toFixed(4));
console.log('Fee per hour:', (totalAccumulated / hoursElapsed).toFixed(4));
console.log('Fee per day (24h):', ((totalAccumulated / hoursElapsed) * 24).toFixed(4));
console.log('Capital:', last.cap);

const dailyRate = ((totalAccumulated / hoursElapsed) * 24) / last.cap * 100;
console.log('Daily yield %:', dailyRate.toFixed(4));
console.log('Monthly yield %:', (dailyRate * 30).toFixed(2));
console.log('Annual yield %:', (dailyRate * 365).toFixed(2));
