const { chromium } = require('playwright');
const path = require('path');

async function takeScreenshot() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  // Set viewport to a nice desktop size
  await page.setViewportSize({ width: 1280, height: 800 });
  
  console.log('Navigating to https://sol.zolu.my.id ...');
  await page.goto('https://sol.zolu.my.id', { waitUntil: 'networkidle', timeout: 30000 });
  
  // Wait for a few seconds to let the logs populate
  await page.waitForTimeout(5000);
  
  const screenshotPath = path.join(__dirname, 'dashboard_screenshot.png');
  await page.screenshot({ path: screenshotPath });
  console.log(`Screenshot saved to ${screenshotPath}`);
  
  await browser.close();
}

takeScreenshot().catch(console.error);
