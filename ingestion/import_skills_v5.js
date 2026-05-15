const { chromium } = require('playwright');

const PAPERCLIP_URL = 'https://paperclip-z6c6.srv1357611.hstgr.cloud';
const EMAIL = 'gewusstwie@gmx.net';
const PASSWORD = process.env.PAPERCLIP_PASSWORD || '';

const SKILLS = [
  'https://raw.githubusercontent.com/ErsterALLES/ErsterALLES-trading-brain/main/agent-skills/trading-foundation/SKILL.md',
  'https://raw.githubusercontent.com/ErsterALLES/ErsterALLES-trading-brain/main/agent-skills/market-data/SKILL.md',
  'https://raw.githubusercontent.com/ErsterALLES/ErsterALLES-trading-brain/main/agent-skills/signal-scoring/SKILL.md'
];

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
  console.log('🔧 Logging into Paperclip...');
  await page.goto(`${PAPERCLIP_URL}/auth`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);
  await page.fill('input[type="email"]', EMAIL);
  await page.fill('input[type="password"]', PASSWORD);
  await page.click('button:has-text("Sign In")');
  await page.waitForTimeout(4000);
  
  const url = page.url();
  if (!url.includes('/ERS')) {
    console.log('❌ Login failed');
    await browser.close();
    return;
  }
  console.log('✅ Logged in!');
  
  // Navigate to Skills
  console.log('\n📚 Navigating to Skills...');
  await page.goto(`${PAPERCLIP_URL}/ERS/skills`);
  await page.waitForTimeout(3000);
  
  // Add each skill
  for (let i = 0; i < SKILLS.length; i++) {
    const skillUrl = SKILLS[i];
    const skillName = skillUrl.split('/').slice(-2)[0];
    
    console.log(`\n📌 Adding Skill ${i+1}/${SKILLS.length}: ${skillName}`);
    
    // Find the input field for adding skills
    const input = await page.$('input[placeholder*="Paste path"]') || 
                  await page.$('input[placeholder*="GitHub"]') ||
                  await page.$('input[placeholder*="skills"]');
    
    if (!input) {
      console.log('   ❌ Could not find skill input field');
      continue;
    }
    
    await input.fill(skillUrl);
    await page.waitForTimeout(500);
    
    // Click Add button
    const addBtn = await page.$('button:has-text("Add")');
    if (addBtn) {
      await addBtn.click();
      await page.waitForTimeout(3000);
      console.log('   ✅ Skill added!');
    } else {
      console.log('   ❌ Add button not found');
    }
    
    await page.screenshot({ path: `/tmp/paperclip_skill_${i+1}.png` });
  }
  
  // Final screenshot
  await page.screenshot({ path: '/tmp/paperclip_skills_final.png', fullPage: true });
  console.log('\n📸 Final screenshot: /tmp/paperclip_skills_final.png');
  
  await browser.close();
  console.log('\n✅ Done importing skills!');
})();
