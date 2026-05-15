const { chromium } = require('playwright');

const PAPERCLIP_URL = 'https://paperclip-z6c6.srv1357611.hstgr.cloud';

(async () => {
  console.log('🔧 Paperclip Direct Access (Session-based)');
  
  const browser = await chromium.launch({
    executablePath: '/opt/data/bin/google-chrome',
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
  });
  
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
  });
  const page = await context.newPage();
  
  // Step 1: Go directly to dashboard (session should persist from previous login)
  console.log('\n1. Going to Paperclip ERS dashboard...');
  await page.goto(`${PAPERCLIP_URL}/ERS`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(3000);
  
  await page.screenshot({ path: '/tmp/paperclip_dashboard_v3.png' });
  console.log('   Screenshot: /tmp/paperclip_dashboard_v3.png');
  
  const url = page.url();
  console.log('   Current URL:', url);
  
  // Check if session expired
  if (url.includes('/login') || url.includes('/auth') || url.includes('/signin')) {
    console.log('   ⚠️  Session expired - Paperclip requires re-authentication');
    console.log('   ℹ️   Paperclip uses Magic Link (no password login available)');
    console.log('   Action needed: Visit Paperclip in your browser and click the Magic Link');
    await browser.close();
    return;
  }
  
  console.log('   ✅ Session active!');
  
  // Step 2: Navigate to Issues
  console.log('\n2. Navigating to Issues...');
  await page.goto(`${PAPERCLIP_URL}/ERS/issues`);
  await page.waitForTimeout(3000);
  await page.screenshot({ path: '/tmp/paperclip_issues_v3.png', fullPage: true });
  console.log('   Screenshot: /tmp/paperclip_issues_v3.png');
  
  // Step 3: Check CEO status
  console.log('\n3. Checking CEO Agent...');
  await page.goto(`${PAPERCLIP_URL}/ERS/agents/ceo`);
  await page.waitForTimeout(3000);
  await page.screenshot({ path: '/tmp/paperclip_ceo_v3.png', fullPage: true });
  console.log('   Screenshot: /tmp/paperclip_ceo_v3.png');
  
  // Step 4: Check Skills
  console.log('\n4. Checking Skills...');
  await page.goto(`${PAPERCLIP_URL}/ERS/skills`);
  await page.waitForTimeout(3000);
  await page.screenshot({ path: '/tmp/paperclip_skills_v3.png', fullPage: true });
  console.log('   Screenshot: /tmp/paperclip_skills_v3.png');
  
  console.log('\n✅ Done! Check screenshots for status.');
  await browser.close();
})();
