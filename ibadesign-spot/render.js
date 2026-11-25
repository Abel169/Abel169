// Usage:
//   node render.js preview <outdir> t1 t2 ...     -> PNG stills at given times
//   (PAGE=vertical.html SIZE=1080x1920 for the 9:16 version)
//   node render.js frames <outdir> <fps> <workers> -> numbered JPEG frames for the whole film
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const PAGE = process.env.PAGE || 'index.html';
const [VW, VH] = (process.env.SIZE || '1920x1080').split('x').map(Number);
const URL = 'file://' + path.join(__dirname, PAGE);
const DUR = +(process.env.DUR || 30);

async function openPage(browser) {
  const page = await browser.newPage({ viewport: { width: VW, height: VH }, deviceScaleFactor: 1 });
  await page.goto(URL);
  await page.evaluate(() => window.ready);
  await page.waitForTimeout(300);
  return page;
}

(async () => {
  const [mode, out, ...rest] = process.argv.slice(2);
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch({ args: ['--disable-gpu-vsync', '--force-color-profile=srgb'] });
  if (mode === 'preview') {
    const page = await openPage(browser);
    for (const t of rest.map(Number)) {
      await page.evaluate(([t]) => window.render(t, Math.round(t * 60)), [t]);
      await page.evaluate(() => window.settle && window.settle());
      await page.screenshot({ path: path.join(out, `t_${t.toFixed(2)}.png`) });
    }
  } else {
    const fps = +rest[0] || 60, workers = +rest[1] || 4;
    const total = Math.round(DUR * fps);
    let next = 0, done = 0;
    const t0 = Date.now();
    await Promise.all(Array.from({ length: workers }, async () => {
      const page = await openPage(browser);
      while (true) {
        const f = next++;
        if (f >= total) break;
        const t = f / fps;
        await page.evaluate(([t, f]) => window.render(t, f), [t, f]);
        await page.evaluate(() => window.settle && window.settle());
        await page.screenshot({ path: path.join(out, `f${String(f).padStart(5, '0')}.jpg`), type: 'jpeg', quality: 95 });
        if (++done % 120 === 0) console.log(`${done}/${total} frames, ${((Date.now() - t0) / 1000).toFixed(0)}s`);
      }
    }));
  }
  await browser.close();
})();
