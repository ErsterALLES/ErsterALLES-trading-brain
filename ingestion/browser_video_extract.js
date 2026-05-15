const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const videoUrl = process.argv[2] || 'https://youtu.be/9SQ0EE1jjVg';
const outputDir = process.argv[3] || '/opt/data/projects/trading-brain/data/videos/browser_extract';

(async () => {
  console.log(`🎬 Browser Video Extractor`);
  console.log(`   URL: ${videoUrl}`);
  console.log(`   Output: ${outputDir}`);
  
  fs.mkdirSync(outputDir, { recursive: true });
  
  const browser = await chromium.launch({
    executablePath: '/opt/data/bin/google-chrome',
    headless: true,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-gpu',
      '--disable-blink-features=AutomationControlled',
      '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    ]
  });
  
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    locale: 'en-US'
  });
  
  const page = await context.newPage();
  
  // Go to YouTube
  console.log('   Opening YouTube...');
  await page.goto(videoUrl, { waitUntil: 'networkidle', timeout: 60000 });
  await page.waitForTimeout(3000);
  
  // Accept cookies if present
  const acceptBtn = await page.$('button:has-text("Accept all")') || 
                   await page.$('button:has-text("I agree")') ||
                   await page.$('[aria-label="Accept the use of cookies and other data for the purposes described"]');
  if (acceptBtn) {
    console.log('   Accepting cookies...');
    await acceptBtn.click().catch(() => {});
    await page.waitForTimeout(2000);
  }
  
  // Screenshot 1: Video page overview
  await page.screenshot({ path: path.join(outputDir, 'screenshot_1_overview.png') });
  console.log('   Screenshot: overview');
  
  // Get video info from page
  const videoInfo = await page.evaluate(() => {
    const title = document.querySelector('h1 yt-formatted-string')?.innerText || 
                  document.querySelector('h1')?.innerText || 'Unknown';
    const description = document.querySelector('#description-inline-expander')?.innerText || '';
    const channel = document.querySelector('ytd-channel-name a')?.innerText || '';
    return { title, description: description.slice(0, 5000), channel };
  });
  
  console.log(`   Title: ${videoInfo.title.slice(0, 100)}`);
  console.log(`   Channel: ${videoInfo.channel}`);
  
  // Extract transcript
  console.log('   Looking for transcript...');
  let transcript = '';
  
  // Try "Show transcript" button
  const moreActions = await page.$('button[aria-label="More actions"]') ||
                      await page.$('tp-yt-paper-button#expand');
  if (moreActions) {
    await moreActions.click().catch(() => {});
    await page.waitForTimeout(1000);
  }
  
  const transcriptBtn = await page.$('text=Show transcript') || 
                       await page.$('text=Open transcript') ||
                       await page.$('text=Transcript');
  
  if (transcriptBtn) {
    console.log('   Clicking transcript button...');
    await transcriptBtn.click();
    await page.waitForTimeout(3000);
    
    // Screenshot 2: Transcript panel
    await page.screenshot({ path: path.join(outputDir, 'screenshot_2_transcript.png') });
    
    // Extract transcript text
    transcript = await page.evaluate(() => {
      const segments = document.querySelectorAll('ytd-transcript-segment-renderer');
      let text = '';
      segments.forEach(s => {
        const t = s.querySelector('.segment-text') || s.querySelector('#text');
        if (t) text += t.innerText + ' ';
      });
      return text;
    });
    
    console.log(`   Transcript: ${transcript.length} chars`);
  } else {
    console.log('   No transcript button found');
  }
  
  // Take frame screenshots (simulate frame extraction)
  console.log('   Capturing frame screenshots...');
  
  // Ensure video is playing
  await page.evaluate(() => {
    const video = document.querySelector('video');
    if (video) video.currentTime = 0;
  });
  await page.waitForTimeout(2000);
  await page.screenshot({ path: path.join(outputDir, 'frame_00_start.png') });
  
  // Jump to various timestamps
  const timestamps = [30, 60, 120, 180, 240, 300];
  for (const ts of timestamps) {
    await page.evaluate((t) => {
      const video = document.querySelector('video');
      if (video) video.currentTime = t;
    }, ts);
    await page.waitForTimeout(1500);
    await page.screenshot({ path: path.join(outputDir, `frame_${String(ts).padStart(3, '0')}.png`) });
    console.log(`   Frame @ ${ts}s captured`);
  }
  
  // Save all data
  const result = {
    url: videoUrl,
    timestamp: new Date().toISOString(),
    video_info: videoInfo,
    transcript_length: transcript.length,
    transcript: transcript,
    frames: timestamps.map(ts => `frame_${String(ts).padStart(3, '0')}.png`),
    screenshots: ['screenshot_1_overview.png', 'screenshot_2_transcript.png'],
    output_dir: outputDir
  };
  
  fs.writeFileSync(
    path.join(outputDir, 'extraction_result.json'),
    JSON.stringify(result, null, 2)
  );
  
  // Also save transcript separately
  fs.writeFileSync(
    path.join(outputDir, 'transcript.txt'),
    transcript
  );
  
  console.log('\n✅ Extraction complete!');
  console.log(`   Transcript: ${transcript.length} chars`);
  console.log(`   Frames: ${timestamps.length + 1}`);
  console.log(`   Output: ${outputDir}`);
  
  await browser.close();
  
  // Print transcript preview for parent process
  console.log('\n---TRANSCRIPT_PREVIEW_START---');
  console.log(transcript.slice(0, 3000));
  console.log('---TRANSCRIPT_PREVIEW_END---');
})();
