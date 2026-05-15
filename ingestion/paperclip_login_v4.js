const { chromium } = require('playwright');

const PAPERCLIP_URL = 'https://paperclip-z6c6.srv1357611.hstgr.cloud';
const EMAIL = 'gewusstwie@gmx.net';
const PASSWORD = process.env.PAPERCLIP_PASSWORD || '';

(async () => {
  if (!PASSWORD) {
    console.log('❌ No PAPERCLIP_PASSWORD env var set');
    process.exit(1);
  }
  
  console.log('🔧 Paperclip Login v4 (Email/Password)');
  console.log('   Email:', EMAIL);
  console.log('   Password:', '*'.repeat(PASSWORD.length));
  
  const browser = await chromium.launch({
    executablePath: '/opt/data/bin/google-chrome',
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
  });
  
  const context = await browser.newContext();
  const page = await context.newPage();
  
  // Go directly to auth page
  console.log('\n1. Going to Paperclip auth...');
  await page.goto(`${PAPERCLIP_URL}/auth`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);
  
  await page.screenshot({ path: '/tmp/paperclip_auth_v4.png' });
  console.log('   Screenshot: /tmp/paperclip_auth_v4.png');
  
  // Fill login form
  console.log('\n2. Filling login form...');
  await page.fill('input[type="email"]', EMAIL);
  await page.fill('input[type="password"]', PASSWORD);
  await page.waitForTimeout(500);
  
  await page.screenshot({ path: '/tmp/paperclip_filled_v4.png' });
  console.log('   Screenshot: /tmp/paperclip_filled_v4.png');
  
  // Click Sign In
  console.log('\n3. Clicking Sign In...');
  await page.click('button:has-text("Sign In")');
  await page.waitForTimeout(4000);
  
  await page.screenshot({ path: '/tmp/paperclip_after_v4.png' });
  console.log('   Screenshot: /tmp/paperclip_after_v4.png');
  
  const url = page.url();
  console.log('   Current URL:', url);
  
  if (url.includes('/ERS') && !url.includes('/auth') && !url.includes('/login')) {
    console.log('   ✅ LOGIN SUCCESSFUL!');
    
    // Navigate to Issues
    console.log('\n4. Checking Issues...');
    await page.goto(`${PAPERCLIP_URL}/ERS/issues`);
    await page.waitForTimeout(3000);
    await page.screenshot({ path: '/tmp/paperclip_issues_v4.png', fullPage: true });
    console.log('   Screenshot: /tmp/paperclip_issues_v4.png');
    
    // Check CEO
    console.log('\n5. Checking CEO...');
    await page.goto(`${PAPERCLIP_URL}/ERS/agents/ceo`);
    await page.waitForTimeout(3000);
    await page.screenshot({ path: '/tmp/paperclip_ceo_v4.png', fullPage: true });
    console.log('   Screenshot: /tmp/paperclip_ceo_v4.png');
    
  } else {
    console.log('   ❌ Login failed - still on:', url);
    const errorText = await page.$eval('[role="alert"], .error, .alert', el => el.textContent).catch(() => null);
    if (errorText) console.log('   Error:', errorText);
  }
  
  await browser.close();
})();
