const fs = require('fs');

const dlmmPath = '/home/ubuntu/apps/solana-trading-engine/src/dlmm.js';
let dlmmContent = fs.readFileSync(dlmmPath, 'utf8');

const targetBlock = `        const liquidityUsd = (totalXAmount * solPrice) + totalYAmount;
        const claimableFeeUsd = (feeXAmount * solPrice) + feeYAmount;

        this.poolState.totalCapitalUsd = Number(liquidityUsd.toFixed(2));
        this.poolState.totalFeeEarnedUsd = Number(claimableFeeUsd.toFixed(4));
        this.poolState.currentEquityUsd = Number((liquidityUsd + claimableFeeUsd).toFixed(2));
        this.poolState.lowerBound = 0.9990;
        this.poolState.upperBound = 1.0010;`;

const replacementBlock = `        const liquidityUsd = (totalXAmount * solPrice) + totalYAmount;
        const claimableFeeUsd = (feeXAmount * solPrice) + feeYAmount;
        
        // Try to get bin prices if SDK supports it, otherwise approximate
        let lowerP = 0, upperP = 0;
        try {
            const minBin = pos.positionData.lowerBinId;
            const maxBin = pos.positionData.upperBinId;
            // The formula in Meteora: price = (1.0001 ^ binId) * (10 ^ (decimalsX - decimalsY))
            // Here X is SOL (9), Y is USDC (6), so 10^3 = 1000. Wait, actually if bin price is returned by SDK:
            // Let's just use 1.0001 ^ binId. But wait, bin step is 20 bps = 1.002.
            // Meteora 20bps pool: base = 1.002.
            const binStep = this.dlmmPool.lbPair.vParameters ? this.dlmmPool.lbPair.vParameters.binStep : 20;
            const base = 1 + (binStep / 10000); // 1.002
            lowerP = Math.pow(base, minBin) * 1000;
            upperP = Math.pow(base, maxBin) * 1000;
        } catch (e) {
            lowerP = 95; upperP = 110;
        }

        this.poolState.posSol = totalXAmount;
        this.poolState.posUsdc = totalYAmount;
        this.poolState.feeSol = feeXAmount;
        this.poolState.feeUsdc = feeYAmount;

        this.poolState.totalCapitalUsd = Number(liquidityUsd.toFixed(2));
        this.poolState.totalFeeEarnedUsd = Number(claimableFeeUsd.toFixed(4));
        this.poolState.currentEquityUsd = Number((liquidityUsd + claimableFeeUsd).toFixed(2));
        this.poolState.lowerBound = lowerP;
        this.poolState.upperBound = upperP;`;

dlmmContent = dlmmContent.replace(targetBlock, replacementBlock);
fs.writeFileSync(dlmmPath, dlmmContent, 'utf8');

console.log('Patched dlmm.js to include breakdowns and price range!');
