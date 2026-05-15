const { chromium } = require('playwright');

const PAPERCLIP_URL = 'https://paperclip-z6c6.srv1357611.hstgr.cloud';
const EMAIL = 'gewusstwie@gmx.net';
const PASSWORD = process.env.PAPERCLIP_PASSWORD || '';

(async () => {
  if (!PASSWORD) {
    console.log('❌ No PAPERCLIP_PASSWORD env var set');
    process.exit(1);
  }
  
  const browser = await chromium.launch({
    executablePath: '/opt/data/bin/google-chrome',
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
  });
  
  const context = await browser.newContext();
  const page = await context.newPage();
  
  // Login
  await page.goto(`${PAPERCLIP_URL}/auth`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);
  await page.fill('input[type="email"]', EMAIL);
  await page.fill('input[type="password"]', PASSWORD);
  await page.click('button:has-text("Sign In")');
  await page.waitForTimeout(4000);
  
  // Check if login successful
  const url = page.url();
  if (!url.includes('/ERS')) {
    console.log('❌ Login failed');
    await browser.close();
    return;
  }
  
  console.log('✅ Logged in!');
  
  // Navigate to Skills
  console.log('\nChecking Skills...');
  await page.goto(`${PAPERCLIP_URL}/ERS/skills`);
  await page.waitForTimeout(3000);
  await page.screenshot({ path: '/tmp/paperclip_skills_v4.png', fullPage: true });
  console.log('Screenshot: /tmp/paperclip_skills_v4.png');
  
  await browser.close();
})();
