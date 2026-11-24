// node rerender.js <outdir> <fromFrame> <toFrame>  (60 fps) — re-renders a frame range in place
const { chromium } = require('playwright'); const path = require('path');
(async () => {
  const [out, a, b] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  await page.goto('file://' + path.join(__dirname, 'index.html'));
  await page.evaluate(() => window.ready); await page.waitForTimeout(300);
  for (let f = +a; f <= +b; f++) {
    await page.evaluate(([t, f]) => window.render(t, f), [f / 60, f]);
    await page.evaluate(() => window.settle && window.settle());
    await page.screenshot({ path: path.join(out, `f${String(f).padStart(5, '0')}.jpg`), type: 'jpeg', quality: 95 });
  }
  await browser.close();
})();
