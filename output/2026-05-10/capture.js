const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

async function captureHTML(htmlFile, outputFile, options = {}) {
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  try {
    const page = await browser.newPage();
    
    // Set viewport based on target
    const width = options.width || 1200;
    const height = options.height || 630;
    const retina = options.retina !== false; // Default to retina scale
    
    await page.setViewport({ 
      width: width, 
      height: height, 
      deviceScaleFactor: retina ? 2 : 1 
    });
    
    const filePath = 'file://' + path.resolve(htmlFile);
    await page.goto(filePath, { waitUntil: 'networkidle0' });
    
    // Wait for fonts and styles
    await new Promise(r => setTimeout(r, 1500));
    
    // Hide cursor by adding CSS
    await page.addStyleTag({
      content: '* { cursor: none !important; }'
    });
    
    await page.screenshot({
      path: outputFile,
      type: 'jpeg',
      quality: 95
    });
    
    console.log('✓ Generated:', outputFile);
    return outputFile;
  } catch (err) {
    console.error('✗ Failed:', err.message);
    throw err;
  } finally {
    await browser.close();
  }
}

async function main() {
  const baseDir = '/Users/dingyao/Documents/DingYao-Website/dingyaoadvisory-website/output/2026-05-10';
  const slug = 'western-cape-foreign-investment';
  
  const jobs = [
    // Hero images
    { html: path.join(baseDir, 'hero.html'), output: path.join(baseDir, `${slug}-hero.jpg`), width: 1200, height: 630 },
    
    // Inline images
    { html: path.join(baseDir, 'inline.html'), output: path.join(baseDir, `${slug}-inline.jpg`), width: 1200, height: 600 },
    
    // CTA background
    { html: path.join(baseDir, 'cta-bg.html'), output: path.join(baseDir, `${slug}-cta-bg.jpg`), width: 1200, height: 400 },
  ];
  
  const generatedFiles = [];
  
  for (const job of jobs) {
    const result = await captureHTML(job.html, job.output, { 
      width: job.width, 
      height: job.height,
      retina: true 
    });
    generatedFiles.push({
      jpg: result,
      width: job.width,
      height: job.height
    });
  }
  
  // Also write a manifest file for tracking
  const manifest = {
    date: '2026-05-10',
    slug: slug,
    files: generatedFiles.map(f => f.jpg),
    generatedAt: new Date().toISOString()
  };
  
  fs.writeFileSync(
    path.join(baseDir, 'manifest.json'),
    JSON.stringify(manifest, null, 2)
  );
  
  console.log('\n=== Generation Complete ===');
  console.log(' JPG files generated:', generatedFiles.length);
  
  // Also check file sizes
  for (const f of generatedFiles) {
    const stats = fs.statSync(f.jpg);
    console.log(`  - ${path.basename(f.jpg)}: ${(stats.size / 1024).toFixed(1)} KB`);
  }
}

main().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
