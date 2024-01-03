const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');
const url = require('url');

async function takeScreenshot(filePath, outputPath) {
    const browser = await puppeteer.launch({
        headless: "new",
        executablePath: '/usr/bin/chromium',
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1256, height: 800 });

    const fileUrl = url.pathToFileURL(path.resolve(filePath)).toString();
    await page.goto(fileUrl, { waitUntil: 'networkidle2' });
    await page.screenshot({ path: outputPath, fullPage: true });
    await browser.close();
}

function getLatestOutputFolder(baseFolder) {
    const dirs = fs.readdirSync(baseFolder, { withFileTypes: true })
        .filter(dirent => dirent.isDirectory() && dirent.name.startsWith('output_'))
        .map(dirent => ({ name: dirent.name, time: fs.statSync(path.join(baseFolder, dirent.name)).mtime }))
        .sort((a, b) => b.time - a.time);
    return dirs.length > 0 ? path.join(baseFolder, dirs[0].name) : null;
}

async function screenshotLatestOutput(baseFolder) {
    const latestFolder = getLatestOutputFolder(baseFolder);
    if (!latestFolder) {
        console.log('No output folder found.');
        return;
    }

    const htmlFiles = fs.readdirSync(latestFolder)
        .filter(file => file.endsWith('.html'));

    for (const file of htmlFiles) {
        const filePath = path.join(latestFolder, file);
        const outputPath = path.join(latestFolder, `${path.parse(file).name}.png`);

        // Skip if screenshot already exists
        if (fs.existsSync(outputPath)) {
            console.log(`Screenshot already exists for ${file}, skipping...`);
            continue;
        }

        console.log(`Taking screenshot of ${file}`);
        await takeScreenshot(filePath, outputPath);
    }
}

const baseFolder = 'publish'; // Adjust to your base folder path
screenshotLatestOutput(baseFolder)
    .then(() => console.log('All screenshots taken'))
    .catch(err => console.error('Error:', err));
