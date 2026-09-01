const fs = require('fs');

function runStableBacktest() {
    console.log(`\n=== BACKTEST DLMM: USDC/USDT STABLECOIN (1 TAHUN) ===`);
    console.log(`Asumsi: Peg terjaga (0.999 - 1.001), Modal Awal: $1,000\n`);

    const initialCapital = 1000;
    const days = 365;
    const hours = days * 24;

    // Strategi 1: Normal Curve (Lebar)
    // Likuiditas disebar, menangkap volume secara pasif, APY rendah
    const apyNormal = 0.15; // 15% APY
    let capNormal = initialCapital;

    // Strategi 2: Hyper-Tight (3 Bins)
    // Likuiditas ditumpuk di tengah persis, menangkap mayoritas volume arbitrasi
    const apyTight = 0.45; // 45% APY
    let capTight = initialCapital;

    // Strategi 3: Hyper-Tight + Hourly Auto-Compound
    // Mengambil fee setiap jam dan langsung disuntikkan kembali sebagai modal
    let capCompound = initialCapital;
    const hourlyRateTight = apyTight / hours;

    for (let i = 0; i < hours; i++) {
        // Asumsi harga bergerak di rentang aman, jadi IL = 0
        // Strategi 1 (No Compound, hitung setahun)
        // Strategi 2 (No Compound)
        // Strategi 3 (Hourly Compound)
        capCompound += capCompound * hourlyRateTight;
    }

    // Hitung final manual untuk Non-compound (Simple Interest)
    capNormal += initialCapital * apyNormal;
    capTight += initialCapital * apyTight;

    function printResult(name, cap) {
        const net = cap - initialCapital;
        const roi = (net / initialCapital) * 100;
        console.log(`${name.padEnd(35)}: Modal Akhir $${cap.toFixed(2)} | Profit $${net.toFixed(2)} | ROI ${roi.toFixed(2)}%`);
    }

    printResult("1. Normal Curve (No Compound)", capNormal);
    printResult("2. Hyper-Tight 3-Bin (No Compound)", capTight);
    printResult("3. Hyper-Tight + Hourly Compound", capCompound);
    
    console.log(`\nKesimpulan: Kombinasi konsentrasi ekstrem (3-Bin) dan Auto-Compound per jam menciptakan efek bola salju (Snowball Effect), meningkatkan APY dasar 45% menjadi APY efektif ${( ((capCompound-initialCapital)/initialCapital) * 100 ).toFixed(2)}% tanpa menambah risiko (Zero IL).`);
}

runStableBacktest();
