// Exports the hand-off frame of the ACE! opening for the player-clip production:
// the exact 1080 x 1920 frame on which the HTML5 ball comes to rest (camera at rest),
// with and without the ball.  The first frame of serve.mp4 must match it.
// Usage: npm run build && node tools/export-handoff.mjs [outDir]
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const OUT = process.argv[2] || path.join(ROOT, '..', 'docs', 'ace_handoff');
fs.mkdirSync(OUT, { recursive: true });
const PORT = 4207;
const server = spawn('npx', ['vite', 'preview', '--port', String(PORT), '--strictPort'], { cwd: ROOT, stdio: 'ignore' });
for (let i = 0; i < 60; i++) { try { if ((await fetch(`http://localhost:${PORT}/`)).ok) break; } catch {} await new Promise((r) => setTimeout(r, 500)); }
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
try {
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await page.goto(`http://localhost:${PORT}/?lang=fr`);
  await page.waitForSelector('[data-testid=start]', { timeout: 90000 });
  // freeze the presentation clock as soon as the ball is at rest
  await page.evaluate(() => {
    const loop = () => {
      const c = window.__rallyIntro?.cinematic;
      if (c && c.qa.phase === 'rest') { window.__rallyTimeScale = 1e-6; window.__atRest = true; return; }
      requestAnimationFrame(loop);
    };
    requestAnimationFrame(loop);
  });
  await page.click('[data-testid=start]');
  await page.waitForFunction(() => window.__atRest, null, { timeout: 60000 });
  await page.evaluate(() => document.querySelector('[data-testid=cine-skip]')?.style.setProperty('visibility', 'hidden'));
  await page.waitForTimeout(300);
  await page.screenshot({ path: path.join(OUT, 'handoff_frame.png') });
  await page.evaluate(() => { const c = window.__rallyIntro.cinematic; c.ballC.visible = false; c.shadow.visible = false; });
  await page.waitForTimeout(200);
  await page.screenshot({ path: path.join(OUT, 'handoff_plate.png') });
  console.log('wrote', OUT);
} finally {
  await browser.close();
  server.kill();
}
