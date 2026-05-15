const { chromium } = require('playwright');

const PAPERCLIP_URL = 'https://paperclip-z6c6.srv1357611.hstgr.cloud';
const EMAIL = 'gewusstwie@gmx.net';
const PASSWORD = process.env.PAPERCLIP_PASSWORD || ''; // Supplied via env var, never hardcoded

// OR use SSO if available
const USE_SSO = true;

(async () => {
  console.log('🔧 Paperclip Fix Script v2');
  console.log('   Email:', EMAIL);
  console.log('   Using:', USE_SSO ? 'SSO/Password' : 'Password only');
  
  const browser = await chromium.launch({
    executablePath: '/opt/data/bin/google-chrome',
    headless: true, // MUST be true in container (no X server)
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
  });
  
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
  });
  const page = await context.newPage();
  
  // Step 1: Go directly to dashboard (user already logged in via persistent session)
  console.log('\n1. Going to Paperclip dashboard (session should persist)...');
  await page.goto(`${PAPERCLIP_URL}/ERS`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(3000);
  
  await page.screenshot({ path: '/tmp/paperclip_dashboard_v2.png' });
  console.log('   Screenshot: /tmp/paperclip_dashboard_v2.png');
  
  const url = page.url();
  console.log('   Current URL:', url);
  
  // Check if we're on dashboard or redirected to login
  if (url.includes('/login') || url.includes('/auth')) {
    console.log('   ⚠️ Session expired - need to re-authenticate');
    console.log('   ℹ️  Paperclip has no /login page - uses Magic Link or SSO');
    console.log('   Please authenticate manually via browser, then rerun');
    await browser.close();
    return;
  }
  
  console.log('   ✅ Already logged in!');
    
    // Navigate to Issues
    console.log('\n3. Checking Issues...');
    await page.goto(`${PAPERCLIP_URL}/ERS/issues`);
    await page.waitForTimeout(3000);
    await page.screenshot({ path: '/tmp/paperclip_issues_v2.png', fullPage: true });
    console.log('   Screenshot: /tmp/paperclip_issues_v2.png');
    
    // Close stalled issues
    console.log('\n4. Closing stalled issues...');
    // This would require specific selectors based on the UI
  }
  
  await browser.close();
})();
