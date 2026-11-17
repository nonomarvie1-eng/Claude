// Rally Path LAB browser checks + screenshots (prototype).  Run `npm run build` first.
// node e2e/lab-e2e.mjs -> e2e/lab-report.json + e2e/screenshots/lab-*
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';

const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.dirname(HERE);
const SHOTS = path.join(HERE, 'screenshots');
fs.mkdirSync(SHOTS, { recursive: true });
const PORT = 4181;
const URL = `http://localhost:${PORT}/?lang=fr`;
const PROTO = JSON.parse(fs.readFileSync(path.join(ROOT, '..', 'shared', 'rally-path-proto.json'), 'utf8'));
const server = spawn('npx', ['vite', 'preview', '--port', String(PORT), '--strictPort'], { cwd: ROOT, stdio: 'ignore' });
const results = [];
let failures = 0;
const check = (name, ok, detail = '') => {
  results.push({ name, ok: !!ok, detail });
  if (!ok) failures++;
  console.log(`${ok ? '✓' : '✗'} ${name}${detail ? ' — ' + detail : ''}`);
};
for (let i = 0; i < 60; i++) {
  try { if ((await fetch(`http://localhost:${PORT}/`)).ok) break; } catch {}
  await new Promise((r) => setTimeout(r, 500));
}
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const vps = [[320, 568], [375, 812], [390, 844], [430, 932], [768, 1024], [1440, 900]];
const norm = (s) => s.replace(/\s/g, ' ').replace(/[  ]/g, ' ').trim();

async function open(w, h) {
  const ctx = await browser.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: 1, hasTouch: w < 800, isMobile: w < 800 });
  const page = await ctx.newPage();
  const errors = [];
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  page.on('pageerror', (e) => errors.push(e.message));
  await page.goto(URL);
  await page.waitForSelector('[data-testid=start]', { timeout: 40000 });
  await page.click('[data-testid=start]');
  // first visit: the feature explanations come after the opening, over the reels
  await page.click('[data-testid=feature-ok]', { timeout: 60000 }).catch(() => {});
  await page.waitForSelector('[data-testid=spin]:not([disabled])', { timeout: 40000 });
  return { ctx, page, errors };
}
async function runScenario(page, key, shotName, frames = []) {
  await page.click('[data-testid=btn-settings]');
  await page.waitForSelector(`[data-testid=lab-sc-${key}]`);
  await page.click(`[data-testid=lab-sc-${key}]`);
  const t0 = Date.now();
  for (const ms of frames) {
    await page.waitForTimeout(Math.max(0, ms - (Date.now() - t0)));
    await page.screenshot({ path: path.join(SHOTS, `${shotName}-t${ms}.png`) });
  }
  await page.waitForSelector('[data-testid=spin]:not([disabled])', { timeout: 180000 });
  const lab = await page.evaluate(() => window.__rallyLab);
  await page.screenshot({ path: path.join(SHOTS, `${shotName}.png`) });
  return { lab, ms: Date.now() - t0 };
}

try {
  for (const [w, h] of vps) {
    const name = `lab-${w}x${h}`;
    const { ctx, page, errors } = await open(w, h);
    const bal0 = norm(await page.textContent('[data-testid=balance]'));
    const keys = w === 390 || w === 1440 ? Object.keys(PROTO.scenarios) : ['three', 'full'];
    for (const key of keys) {
      const frames = key === 'full' && (w === 390 || w === 1440) ? [900, 1500, 2100, 2700, 3300, 4200] : key === 'five' && w === 390 ? [900, 1300, 1700] : [];
      const { lab, ms } = await runScenario(page, key, `${name}-${key}`, frames);
      const sc = PROTO.scenarios[key];
      const fin = lab.events[lab.events.length - 1];
      check(`${name} ${key}: scenario replays the recorded result`, lab.scenario === key && Math.abs(fin.amount / 100 - sc.totalX) < 1e-9, `${fin.amount / 100}x / ${sc.totalX}x`);
      const rps = lab.events.filter((e) => e.type === 'rallyPath');
      if (sc.mode === 'base') check(`${name} ${key}: rally length as expected`, rps.length === 1, rps.map((e) => e.length).join(','));
      check(`${name} ${key}: balance unchanged (lab not credited)`, norm(await page.textContent('[data-testid=balance]')) === bal0);
      if (sc.mode === 'base') check(`${name} ${key}: duration`, true, `${ms} ms`);
    }
    const ov = await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth && document.documentElement.scrollHeight <= innerHeight);
    check(`${name}: no scroll/overflow`, ov);
    check(`${name}: no console errors`, errors.length === 0, errors.slice(0, 2).join(' | '));
    await ctx.close();
  }
  // skip: tapping during the animation never changes the result
  {
    const { ctx, page } = await open(390, 844);
    await page.click('[data-testid=btn-settings]');
    await page.click('[data-testid=lab-sc-final_ss]');
    const t0 = Date.now();
    for (let i = 0; i < 40; i++) { await page.mouse.click(195, 420); await page.waitForTimeout(150); }
    await page.waitForSelector('[data-testid=spin]:not([disabled])', { timeout: 180000 });
    const lab = await page.evaluate(() => window.__rallyLab);
    const fin = lab.events[lab.events.length - 1];
    check('skip by taps: same result as the recorded scenario', Math.abs(fin.amount / 100 - PROTO.scenarios.final_ss.totalX) < 1e-9, `${Date.now() - t0} ms`);
    await page.screenshot({ path: path.join(SHOTS, 'lab-390x844-final_ss-skipped.png') });
    // lab toggle: Spin plays prototype rounds, normal game resumes after
    await page.click('[data-testid=btn-settings]');
    await page.check('[data-testid=lab-toggle]');
    await page.keyboard.press('Escape');
    const bal0 = norm(await page.textContent('[data-testid=balance]'));
    for (let i = 0; i < 3; i++) {
      await page.click('[data-testid=spin]');
      await page.waitForSelector('[data-testid=spin][disabled]', { timeout: 5000 }).catch(() => {});
      await page.waitForSelector('[data-testid=spin]:not([disabled])', { timeout: 120000 });
    }
    check('lab toggle: 3 prototype spins, balance unchanged', norm(await page.textContent('[data-testid=balance]')) === bal0);
    await page.screenshot({ path: path.join(SHOTS, 'lab-390x844-toggle.png') });
    await ctx.close();
  }
} finally {
  await browser.close();
  server.kill();
  fs.writeFileSync(path.join(HERE, 'lab-report.json'), JSON.stringify({ failures, results }, null, 1));
  console.log(`\n${results.length - failures}/${results.length} checks passed`);
  process.exit(failures ? 1 : 0);
}
