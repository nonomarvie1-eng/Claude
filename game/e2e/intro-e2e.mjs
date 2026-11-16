// THE FIRST SERVE — loading / entry checks on the real app (npm run build first, or URL=... for a published file).
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
const PORT = 4197;
const URL = process.env.URL || `http://localhost:${PORT}/?lang=fr`;
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
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
// counts AudioContext creations: no sound before a real gesture
const AUDIO_SPY = () => {
  window.__audioCtx = 0;
  const A = window.AudioContext;
  window.AudioContext = class extends A { constructor(...a) { super(...a); window.__audioCtx++; } };
};
async function probe(page) {
  // progress values seen by the accessible progressbar (real decoded fraction)
  return page.evaluate(() => {
    window.__prog = [];
    const tick = () => {
      const el = document.querySelector('[data-testid=intro-progress]');
      if (el) window.__prog.push({ v: +el.getAttribute('aria-valuenow'), t: performance.now() });
      const ready = document.querySelector('[data-testid=start]') || document.querySelector('[data-testid=spin]');
      if (ready && !window.__readyAt) window.__readyAt = performance.now();
      requestAnimationFrame(tick);
    };
    tick();
  });
}

async function firstVisit(name, opts, throttle) {
  const ctx = await browser.newContext(opts);
  await ctx.addInitScript(AUDIO_SPY);
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push(e.message));
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  if (throttle) {
    const cdp = await ctx.newCDPSession(page);
    await cdp.send('Network.enable');
    await cdp.send('Network.emulateNetworkConditions', { offline: false, latency: 120, downloadThroughput: (+(process.env.KBPS || 2500) * 1000) / 8, uploadThroughput: 1e5 });
  }
  await page.goto(URL, { waitUntil: 'commit' });
  await page.waitForSelector('#preboot, [data-testid=intro-progress]', { timeout: 20000 });
  check(`${name}: stadium pre-boot layer shown before the game script`, await page.isVisible('#preboot .pb-bg').catch(() => false) || (await page.$('[data-testid=intro-progress]')) !== null);
  await page.waitForSelector('[data-testid=intro-progress]', { timeout: 60000 });
  await probe(page);
  await page.screenshot({ path: path.join(SHOTS, `fs-${name}-loading.png`) });
  await page.waitForSelector('[data-testid=start]', { timeout: 90000 });
  const prog = await page.evaluate(() => window.__prog.map((x) => x.v));
  const mono = prog.every((v, i) => i === 0 || v >= prog[i - 1]);
  check(`${name}: real progress, monotonic, ends at 100`, mono && prog[prog.length - 1] === 100, `${prog.length} samples, ${[...new Set(prog)].slice(0, 12).join(',')}…`);
  const q = await page.evaluate(() => ({ ...window.__rallyIntro.qa }));
  check(`${name}: the four light banks switched on with the progress`, q.lightsOn === 4);
  check(`${name}: preboot removed once the scene is up`, (await page.$('#preboot')) === null);
  check(`${name}: no sound before a gesture`, (await page.evaluate(() => window.__audioCtx)) === 0);
  await page.waitForTimeout(400);
  await page.screenshot({ path: path.join(SHOTS, `fs-${name}-card.png`) });
  check(`${name}: first visit shows the feature card with continue and skip`, (await page.isVisible('[data-testid=start]')) && (await page.isVisible('[data-testid=intro-skip]')));
  const b = await page.evaluate(() => document.querySelector('[data-testid=start]').getBoundingClientRect().toJSON());
  const vp = page.viewportSize();
  const cardBottom = await page.evaluate(() => window.__rallyIntro.cardBottom());
  check(`${name}: the feature card never covers the buttons`, cardBottom !== null && cardBottom <= b.top - 4, `card bottom ${Math.round(cardBottom)} / button top ${Math.round(b.top)}`);
  check(`${name}: continue button fully on screen, >= 44 px`, b.top >= 0 && b.bottom <= vp.height && b.height >= 44, JSON.stringify({ top: Math.round(b.top), h: Math.round(b.height) }));
  return { ctx, page, errors };
}

try {
  // ---- iPhone-size, slowed network: loading sequence, card, transition, return visit
  const { ctx, page, errors } = await firstVisit('390', { viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, userAgent: devices['iPhone 13'].userAgent }, true);
  await page.click('[data-testid=start]');
  await page.waitForTimeout(250);
  await page.screenshot({ path: path.join(SHOTS, 'fs-390-transition.png') });
  const hudOp = await page.evaluate(() => getComputedStyle(document.querySelector('.hud')).opacity);
  check('390: HUD hidden during the transition', +hudOp < 0.5, `opacity ${hudOp}`);
  await page.waitForSelector('[data-testid=spin]:not([disabled])', { timeout: 30000 });
  const tq = await page.evaluate(() => ({ ...window.__rallyIntro.qa }));
  // animation time (what a fluid device shows); the wall time of this software-rendered browser is reported too
  check('390: transition animation 0.5–0.8 s', tq.transitionAnimMs >= 500 && tq.transitionAnimMs <= 800, `${Math.round(tq.transitionAnimMs)} ms animation · ${Math.round(tq.transitionMs)} ms wall @ ${tq.fps} fps (software rendering)`);
  check('390: sound started by the PLAY gesture', (await page.evaluate(() => window.__audioCtx)) === 1);
  check('390: intro canvas removed, reels visible', (await page.$('[data-testid=intro-progress]')) === null && (await page.evaluate(() => window.__rallyLayout.board.w)) > 300);
  await page.waitForTimeout(500);
  await page.screenshot({ path: path.join(SHOTS, 'fs-390-game.png') });
  await page.click('[data-testid=spin]');
  await page.waitForSelector('[data-testid=spin]:not([disabled])', { timeout: 60000 });
  check('390: a spin works after the entry', true);
  // return visit (same storage): straight to the reels, no card, no sound until a gesture
  await page.reload();
  await page.waitForSelector('[data-testid=spin]:not([disabled])', { timeout: 60000 });
  const sawCard = await page.evaluate(() => !!document.querySelector('[data-testid=intro-skip]'));
  check('390: returning visit goes straight to the grid (no card)', !sawCard);
  check('390: returning visit: no sound before a gesture', (await page.evaluate(() => window.__audioCtx)) === 0);
  await page.click('[data-testid=spin]');
  await page.waitForTimeout(300);
  check('390: first gesture unlocks the sound', (await page.evaluate(() => window.__audioCtx)) === 1);
  check('390: no console errors', errors.length === 0, errors.slice(0, 2).join(' | '));
  await ctx.close();

  // ---- skip link + reduced motion + landscape phone + desktop
  for (const [name, opts] of [['pixel7-landscape', devices['Pixel 7 landscape']], ['1440x900', { viewport: { width: 1440, height: 900 } }], ['320x568', { viewport: { width: 320, height: 568 }, isMobile: true, hasTouch: true }]]) {
    const o = await firstVisit(name, opts, false);
    if (name === '320x568') {
      await o.page.evaluate(() => { const p = JSON.parse(localStorage.getItem('golden-rally-prefs-v1') || '{}'); p.reducedMotion = true; localStorage.setItem('golden-rally-prefs-v1', JSON.stringify(p)); });
    }
    await o.page.click('[data-testid=intro-skip]');
    await o.page.waitForSelector('[data-testid=spin]:not([disabled])', { timeout: 30000 });
    const tq2 = await o.page.evaluate(() => window.__rallyIntro.qa.transitionMs);
    check(`${name}: skip link enters the game`, tq2 > 0, `${Math.round(tq2)} ms`);
    await o.page.waitForTimeout(400);
    await o.page.screenshot({ path: path.join(SHOTS, `fs-${name}-game.png`) });
    const mm = await o.page.evaluate(() => ({ sw: document.documentElement.scrollWidth, iw: innerWidth }));
    check(`${name}: no overflow, no console errors`, mm.sw <= mm.iw && o.errors.length === 0, o.errors.slice(0, 2).join(' | '));
    await o.ctx.close();
  }
  // reduced motion (preference set before loading): short crossfade
  {
    const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, reducedMotion: 'reduce' });
    const page = await ctx.newPage();
    await page.goto(URL);
    await page.waitForSelector('[data-testid=start]', { timeout: 60000 });
    await page.click('[data-testid=start]');
    await page.waitForSelector('[data-testid=spin]:not([disabled])', { timeout: 30000 });
    const tq3 = await page.evaluate(() => window.__rallyIntro.qa.transitionAnimMs);
    check('reduced motion: short crossfade only (≤ 0.3 s of animation)', tq3 > 0 && tq3 <= 300, `${Math.round(tq3)} ms`);
    await ctx.close();
  }
  // tap during the transition skips it (never changes anything else)
  {
    const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
    const page = await ctx.newPage();
    await page.goto(URL);
    await page.waitForSelector('[data-testid=start]', { timeout: 60000 });
    await page.evaluate(() => { window.__rallyTimeScale = 0.25; });
    await page.click('[data-testid=start]');
    await page.waitForTimeout(150);
    for (let i = 0; i < 4; i++) await page.mouse.click(195, 500).catch(() => {});
    await page.waitForSelector('[data-testid=spin]:not([disabled])', { timeout: 30000 });
    const tq4 = await page.evaluate(() => window.__rallyIntro.qa.transitionAnimMs);
    check('tap skips the transition (shorter than the slowed-down one)', tq4 < (0.7 / 0.25) * 1000 * 0.8, `${Math.round(tq4)} ms of animation at 0.25x speed`);
    await ctx.close();
  }
  // loading error: an image cannot be fetched -> clear message + retry
  if (!process.env.URL) {
    const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } });
    const page = await ctx.newPage();
    await page.route(/sym_H2.*\.(webp|png)$/, (r) => r.abort());
    await page.goto(URL);
    await page.waitForSelector('[data-testid=intro-error]', { timeout: 60000 });
    check('load error: message + retry button, no game entered', (await page.isVisible('[data-testid=intro-error] button')) && !(await page.isVisible('[data-testid=spin]')));
    await page.screenshot({ path: path.join(SHOTS, 'fs-390-error.png') });
    await ctx.close();
  }
} catch (e) {
  check('test run completed', false, String(e).slice(0, 300));
} finally {
  await browser.close();
  server?.kill();
  fs.writeFileSync(path.join(HERE, 'intro-report.json'), JSON.stringify({ url: URL, failures, results }, null, 1));
  console.log(`\n${results.length - failures}/${results.length} checks passed`);
  process.exit(failures ? 1 : 0);
}
