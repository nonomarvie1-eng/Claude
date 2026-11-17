// ACE! opening cinematic on the real app (npm run build first, or URL=... for a published file).
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';

const require = createRequire(import.meta.url);
const { chromium, devices } = require('playwright');
const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.dirname(HERE);
const SHOTS = path.join(HERE, 'screenshots');
fs.mkdirSync(SHOTS, { recursive: true });
const PORT = 4203;
const URL = process.env.URL || `http://localhost:${PORT}/?lang=fr`;
const TEST_CLIP = process.env.TEST_CLIP; // synthetic QA clip (never shipped) to test the external clip integration point
const server = process.env.URL ? null : spawn('npx', ['vite', 'preview', '--port', String(PORT), '--strictPort'], { cwd: ROOT, stdio: 'ignore' });
const results = [];
let failures = 0;
const check = (name, ok, detail = '') => {
  results.push({ name, ok: !!ok, detail });
  if (!ok) failures++;
  console.log(`${ok ? '✓' : '✗'} ${name}${detail ? ' — ' + detail : ''}`);
};
if (server) for (let i = 0; i < 60; i++) {
  try { if ((await fetch(`http://localhost:${PORT}/`)).ok) break; } catch {}
  await new Promise((r) => setTimeout(r, 500));
}
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--autoplay-policy=no-user-gesture-required'] });
const PHONE = { viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, userAgent: devices['iPhone 13'].userAgent };

async function open(opts, init) {
  const ctx = await browser.newContext(opts);
  if (init) await ctx.addInitScript(init.fn, init.arg);
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push(e.message));
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  return { ctx, page, errors };
}
async function playFirstVisit(page, { shots = [], skipAt = null, label = 'x' } = {}) {
  await page.goto(URL);
  await page.waitForSelector('[data-testid=start]', { timeout: 60000 });
  await page.evaluate(() => {
    window.__hud = [];
    const loop = () => {
      const el = document.querySelector('.hud');
      if (el && document.querySelector('[data-testid=intro-progress]')) window.__hud.push(+getComputedStyle(el).opacity);
      if (!window.__rallyIntro?.cinematicResult && !window.__rallyIntro?.qa.transitionMs) requestAnimationFrame(loop);
    };
    requestAnimationFrame(loop);
  });
  const t0 = Date.now();
  await page.click('[data-testid=start]');
  for (const ms of shots) {
    await page.waitForTimeout(Math.max(0, ms - (Date.now() - t0)));
    await page.screenshot({ path: path.join(SHOTS, `ace-${label}-t${ms}.png`) });
  }
  if (skipAt !== null) {
    await page.waitForTimeout(Math.max(0, skipAt - (Date.now() - t0)));
    await page.click('[data-testid=cine-skip]').catch(() => {});
  }
  await page.waitForSelector('[data-testid=spin]:not([disabled])', { timeout: 120000 });
  return page.evaluate(() => ({ r: window.__rallyIntro?.cinematicResult ?? null, hud: window.__hud, canvases: document.querySelectorAll('canvas').length, wall: 0 }));
}

try {
  // ---- iPhone size, first visit: HTML5 version (no external clip)
  {
    const { ctx, page, errors } = await open(PHONE);
    const o = await playFirstVisit(page, { shots: [300, 900, 1500, 2100, 2700, 3300, 3900], label: '390' });
    const r = o.r;
    check('390: the ACE! opening plays after PLAY (first visit)', !!r);
    check('390: ONE ball — the falling ball starts exactly at the logo ball (same x, same size)', r && Math.abs(r.continuity.fallStartX - r.continuity.logoBallX) < 0.5 && Math.abs(r.continuity.dStart - r.continuity.dLogo) < 0.01, r && JSON.stringify(r.continuity));
    check('390: the ball leaves its socket upwards before falling (lift only)', r && r.continuity.fallStartY < r.continuity.logoBallY);
    check('390: two bounces on the court with sound cues', r && r.bounces === 2, r && `${r.bounces}`);
    check('390: no player clip: no stand-in character, camera push into the ball', r && r.usedClip === false);
    check('390: real reels revealed under the ball (occlusion), game playable', r && r.occludedAt > 0 && (await page.isEnabled('[data-testid=spin]')), r && `occluded at ${Math.round(r.occludedAt)} ms of ${Math.round(r.totalMs)} ms`);
    check('390: HUD hidden during the whole opening', o.hud.length > 0 && Math.max(...o.hud) < 0.5, `${o.hud.length} frames`);
    check('390: loading/opening canvas removed (one canvas left)', o.canvases === 1);
    await page.waitForTimeout(500);
    await page.screenshot({ path: path.join(SHOTS, 'ace-390-game.png') });
    await page.click('[data-testid=spin]');
    await page.waitForSelector('[data-testid=spin]:not([disabled])', { timeout: 60000 });
    check('390: a spin works right after the opening', true);
    // returning visit: no opening, straight to the grid
    await page.reload();
    await page.waitForSelector('[data-testid=spin]:not([disabled])', { timeout: 60000 });
    check('390: returning visit goes straight to the grid (no opening)', (await page.evaluate(() => window.__rallyIntro?.cinematicResult ?? null)) === null);
    check('390: no console errors', errors.length === 0, errors.slice(0, 2).join(' | '));
    await ctx.close();
  }
  // ---- skip
  {
    const { ctx, page } = await open(PHONE);
    const o = await playFirstVisit(page, { skipAt: 600, label: 'skip' });
    check('skip: the opening can be skipped (shorter, game reached)', o.r && o.r.occludedAt > 0 && o.r.totalMs < 2500, o.r && `${Math.round(o.r.totalMs)} ms`);
    await ctx.close();
  }
  // ---- reduced motion: no opening
  {
    const { ctx, page } = await open({ ...PHONE, reducedMotion: 'reduce' });
    const o = await playFirstVisit(page, { label: 'rm' });
    check('reduced motion: no opening, short crossfade', o.r === null);
    await ctx.close();
  }
  // ---- external player clip integration point (synthetic QA clip, never shipped)
  if (TEST_CLIP) {
    const clip = { src: 'qa.webm', width: 1080, height: 1920, handoffAt: 0, ball: { x: 0.5, y: 0.81, d: 0.11 }, contactAt: 1.0, occludedAt: 2.0 };
    const init = { fn: (c) => { window.__aceClipOverride = { clip: c, url: '/__qa/clip.webm' }; }, arg: clip };
    const { ctx, page, errors } = await open(PHONE, init);
    await page.route('**/__qa/clip.webm', (r) => r.fulfill({ path: TEST_CLIP, contentType: 'video/webm' }));
    const o = await playFirstVisit(page, { shots: [2600, 3400], label: 'clip' });
    check('clip: the external serve clip is played between the bounce and the occlusion', o.r && o.r.usedClip === true, o.r && `occluded at ${Math.round(o.r.occludedAt)} ms`);
    check('clip: reels revealed after the clip, no console errors', o.r && o.r.occludedAt > 0 && errors.length === 0, errors.slice(0, 2).join(' | '));
    await ctx.close();
    // broken clip -> HTML5 version, never a blank screen
    const b = await open(PHONE, { fn: (c) => { window.__aceClipOverride = { clip: c, url: '/__qa/missing.webm' }; }, arg: clip });
    const ob = await playFirstVisit(b.page, { label: 'clip-missing' });
    check('clip missing/broken: falls back to the HTML5 version and reaches the game', ob.r && ob.r.usedClip === false && ob.r.occludedAt > 0);
    await b.ctx.close();
  }
  // ---- other screens
  for (const [name, opts] of [['1440x900', { viewport: { width: 1440, height: 900 } }], ['pixel7-landscape', devices['Pixel 7 landscape']], ['320x568', { viewport: { width: 320, height: 568 }, isMobile: true, hasTouch: true }]]) {
    const { ctx, page, errors } = await open(opts);
    const o = await playFirstVisit(page, { shots: [1000], label: name });
    const mm = await page.evaluate(() => ({ sw: document.documentElement.scrollWidth, iw: innerWidth }));
    check(`${name}: opening plays and reaches the game, no overflow, no errors`, o.r && o.r.occludedAt > 0 && mm.sw <= mm.iw && errors.length === 0, errors.slice(0, 2).join(' | '));
    await ctx.close();
  }
} catch (e) {
  check('test run completed', false, String(e).slice(0, 300));
} finally {
  await browser.close();
  server?.kill();
  fs.writeFileSync(path.join(HERE, 'cinematic-report.json'), JSON.stringify({ url: URL, failures, results }, null, 1));
  console.log(`\n${results.length - failures}/${results.length} checks passed`);
  process.exit(failures ? 1 : 0);
}
