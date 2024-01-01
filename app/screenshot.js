const puppeteer = require('puppeteer');

async function takeScreenshot(url, path) {
    const browser = await puppeteer.launch({ 
      headless: "new", // or just 'true' if the new headless mode causes issues
      executablePath: '/usr/bin/chromium', // Updated path to the Chromium executable
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    const page = await browser.newPage();

    // Set viewport to iPhone 14 width. iPhone 14 has a width of 390 pixels (standard).
    await page.setViewport({ width: 600, height: 800 });

    await page.goto(url, { waitUntil: 'networkidle2' });

    // Take a full-page screenshot
    await page.screenshot({ path: path, fullPage: true });

    await browser.close();
}

takeScreenshot('file:///opt/app/app/deals.html', 'screenshot.png')
    .then(() => console.log('Screenshot taken'))
    .catch(err => console.error('Error taking screenshot:', err));
