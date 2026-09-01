const fs = require('fs');

async function fetchBinanceData(symbol = 'SOLUSDT', interval = '1h', limit = 1000) {
    console.log(`Mengambil data historis ${symbol} (${interval}) dari Binance...`);
    const url = `https://data-api.binance.vision/api/v3/klines?symbol=${symbol}&interval=${interval}&limit=${limit}`;
    const res = await fetch(url);
    const data = await res.json();
    
    return data.map(d => ({
        time: new Date(d[0]).toISOString(),
        open: parseFloat(d[1]),
        high: parseFloat(d[2]),
        low: parseFloat(d[3]),
        close: parseFloat(d[4])
    }));
}

// IL Formula murni (kerugian karena curve, di luar kerugian harga aset)
function calculateIL(p_0, p_current, p_min, p_max) {
    if (p_current < p_min) p_current = p_min;
    if (p_current > p_max) p_current = p_max;
    const sqrt_p0 = Math.sqrt(p_0);
    const sqrt_pc = Math.sqrt(p_current);
    
    const hold_value = 0.5 + 0.5 * (p_current / p_0);
    const lp_value = (sqrt_pc - Math.sqrt(p_min)) / (sqrt_p0 - Math.sqrt(p_min)) * 0.5 + 
                     (1 / sqrt_pc - 1 / Math.sqrt(p_max)) / (1 / sqrt_p0 - 1 / Math.sqrt(p_max)) * 0.5 * (p_current / p_0);

    return (lp_value / hold_value) - 1;
}

async function runBacktest() {
    const data = await fetchBinanceData('SOLUSDT', '1h', 720); // 30 hari
    
    let initialCapital = 1000;
    
    // Alokasi: 50% di DLMM, 50% di Perps (sebagai jaminan margin Short)
    let lpCapital = 500;
    let marginCapital = 500;
    
    const rangePercent = 0.10; // Range +/- 10%
    const assumedDailyAPY = 1.0; // Asumsi APY 100% karena modal aktif hanya 50%
    const hourlyFeeYield = (assumedDailyAPY / 365) / 24; 
    
    let currentPosition = null;
    let totalRebalances = 0;
    let accumulatedFees = 0;

    console.log(`\n=== BACKTEST: DELTA NEUTRAL LP (HEDGED) ===`);
    console.log(`Pair: SOL/USDT`);
    console.log(`Range DLMM: +/- ${rangePercent * 100}%`);
    console.log(`Total Modal: $${initialCapital} (50% LP, 50% Margin Short)`);
    console.log(`Simulasi: 30 Hari Terakhir\n`);

    for (let i = 0; i < data.length; i++) {
        const price = data[i].close;

        if (!currentPosition) {
            currentPosition = {
                entryPrice: price,
                pMin: price * (1 - rangePercent),
                pMax: price * (1 + rangePercent),
                lpCapitalStart: lpCapital
            };
        }

        const isOutOfRange = price <= currentPosition.pMin || price >= currentPosition.pMax;

        if (isOutOfRange) {
            // REBALANCE
            const ilPct = calculateIL(currentPosition.entryPrice, price, currentPosition.pMin, currentPosition.pMax);
            
            // Dalam Hedged LP, harga SOL yang turun/naik dikompensasi 100% oleh posisi Short.
            // Sehingga modal LP hanya tergerus oleh Impermanent Loss murni, bukan oleh Principal Loss.
            // Kita potong modal LP berdasarkan % IL. Slippage asumsi 0.1%
            lpCapital = currentPosition.lpCapitalStart * (1 + ilPct) * 0.999;
            
            // Auto-compound fee ke LP
            lpCapital += accumulatedFees;
            accumulatedFees = 0;
            currentPosition = null;
            totalRebalances++;
        } else {
            // Hasilkan fee dari kapital yang ada di LP
            accumulatedFees += currentPosition.lpCapitalStart * hourlyFeeYield;
        }
    }

    // Akhir simulasi, evaluasi sisa IL yang belum di-rebalance
    if (currentPosition) {
        const lastPrice = data[data.length - 1].close;
        const ilPct = calculateIL(currentPosition.entryPrice, lastPrice, currentPosition.pMin, currentPosition.pMax);
        lpCapital = (currentPosition.lpCapitalStart * (1 + ilPct));
    }

    // Total ekuitas = Sisa modal LP + Modal Margin (tidak tersentuh karena 1x hedge) + Total Fee
    const finalCapital = lpCapital + marginCapital + accumulatedFees;
    const netProfit = finalCapital - initialCapital;
    const roi = (netProfit / initialCapital) * 100;

    console.log(`=== HASIL BACKTEST (30 HARI) ===`);
    console.log(`Modal Akhir     : $${finalCapital.toFixed(2)}`);
    console.log(`Net Profit      : $${netProfit.toFixed(2)} (${roi.toFixed(2)}%)`);
    console.log(`Total Rebalance : ${totalRebalances} kali`);
    console.log(`Est. APY Tahunan: ${(roi * 12).toFixed(2)}%\n`);
}

runBacktest().catch(console.error);
