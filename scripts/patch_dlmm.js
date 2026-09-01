const fs = require('fs');

const path = '/home/ubuntu/apps/solana-trading-engine/src/dlmm.js';
let content = fs.readFileSync(path, 'utf8');

// The replacement logic:
// Replace 1e6 logic for X with 1e9, and multiply X by price.
// But wait, the easiest is to just use a regular expression or simple string replace.

const targetBlock = `        if (pos.positionData?.positionBinData) {
          for (const bin of pos.positionData.positionBinData) {
            totalXAmount += Number(bin.positionXAmount || 0) / 1e6;
            totalYAmount += Number(bin.positionYAmount || 0) / 1e6;
            feeXAmount += Number(bin.positionFeeXAmount || 0) / 1e6;
            feeYAmount += Number(bin.positionFeeYAmount || 0) / 1e6;
          }
        }

        const liquidityUsd = totalXAmount + totalYAmount;
        const claimableFeeUsd = feeXAmount + feeYAmount;`;

const replacementBlock = `        const activeBin = await this.dlmmPool.getActiveBin();
        const solPrice = Number(activeBin.price);

        if (pos.positionData?.positionBinData) {
          for (const bin of pos.positionData.positionBinData) {
            totalXAmount += Number(bin.positionXAmount || 0) / 1e9;
            totalYAmount += Number(bin.positionYAmount || 0) / 1e6;
            feeXAmount += Number(bin.positionFeeXAmount || 0) / 1e9;
            feeYAmount += Number(bin.positionFeeYAmount || 0) / 1e6;
          }
        }

        const liquidityUsd = (totalXAmount * solPrice) + totalYAmount;
        const claimableFeeUsd = (feeXAmount * solPrice) + feeYAmount;`;

content = content.replace(targetBlock, replacementBlock);

fs.writeFileSync(path, content, 'utf8');
console.log("Patched dlmm.js successfully!");
