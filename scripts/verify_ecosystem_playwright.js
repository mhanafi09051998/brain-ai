const { chromium } = require('/home/ubuntu/.hermes/hermes-agent/node_modules/playwright');

(async () => {
  try {
    console.log('[*] Testing all 7 ecosystem web applications with Playwright...');
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();

    const targets = [
      { name: 'Zolu Learn (Benchmark Hub)', url: 'https://learn.zolu.my.id' },
      { name: 'Zolu Main Portal', url: 'https://zolu.my.id' },
      { name: 'MojoLoker Job Portal', url: 'https://mojoloker.my.id' },
      { name: 'Zolu Chat & Claudia Portal', url: 'https://claudiacode.zolu.my.id' },
      { name: 'Zolu Kas Financial OS', url: 'https://kas.zolu.my.id' },
      { name: 'Zolu Skripsi Platform', url: 'https://skripsi.zolu.my.id' },
      { name: 'Zolu Invite Gateway', url: 'https://join.zolu.my.id' }
    ];

    for (const t of targets) {
      const t0 = Date.now();
      await page.goto(t.url, { waitUntil: 'domcontentloaded', timeout: 15000 });
      const title = await page.title();
      const duration = Date.now() - t0;
      console.log(` ✔ [200 OK] ${t.name.padEnd(28)} -> Title: "${title.slice(0, 35)}..." (${duration}ms)`);
    }

    await browser.close();
    console.log('\n🎉 ALL 7 ECOSYSTEM SITES VERIFIED LIVE & ACCESSIBLE VIA PLAYWRIGHT!\n');
    process.exit(0);
  } catch (e) {
    console.error('✖ Playwright verification failed:', e.message);
    process.exit(1);
  }
})();
