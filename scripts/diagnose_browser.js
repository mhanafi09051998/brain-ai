const { chromium } = require('/home/ubuntu/.hermes/hermes-agent/node_modules/playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  page.on('console', msg => console.log('BROWSER CONSOLE:', msg.type(), msg.text()));
  page.on('pageerror', err => console.log('BROWSER PAGE ERROR:', err.message));

  await page.goto('https://learn.zolu.my.id');
  await page.waitForTimeout(3000);

  const gridHtml = await page.$eval('#metrics-grid', el => el.innerHTML);
  console.log('GRID INNER HTML LENGTH:', gridHtml.length);
  const logHtml = await page.$eval('#log-container', el => el.innerHTML);
  console.log('LOG INNER HTML:', logHtml.slice(0, 200));

  await browser.close();
})();
