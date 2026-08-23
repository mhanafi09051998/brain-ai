const { chromium } = require('/home/ubuntu/.hermes/hermes-agent/node_modules/playwright');

(async () => {
  try {
    console.log('[*] Launching Playwright Chromium Headless...');
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();
    await page.goto('https://learn.zolu.my.id', { waitUntil: 'domcontentloaded' });
    const title = await page.title();
    console.log('✔ Playwright Test: SUCCESS!');
    console.log('  • Page Title:', title);
    await browser.close();
    process.exit(0);
  } catch (e) {
    console.error('✖ Playwright Test Failed:', e.message);
    process.exit(1);
  }
})();
