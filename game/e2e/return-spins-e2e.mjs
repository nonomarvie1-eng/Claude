// Real game, test build RETURN-01 (npm run build first; or URL=... for the published file).
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
const PORT = 4193;
const URL = process.env.URL || `http://localhost:${PORT}/?lang=fr`;
const RS = JSON.parse(fs.readFileSync(path.join(ROOT, '..', 'shared', 'return-spins.json'), 'utf8'));
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
const OLD = ['bonusStart', 'hawkEye', 'shot', 'exchangeStart', 'rallyPath', 'protoBonusStart', 'goldenServe', 'gsBonusStart', 'duelStart', 'duelPoint'];
const fmt = (a) => new Intl.NumberFormat('fr-FR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(a / 1e6);
const norm = (s) => s.replace(/\s/g, ' ').replace(/[  ]/g, ' ').trim();
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const PHONE = { viewport: { width: 390, height: 844 }, deviceScaleFactor: 1, isMobile: true, hasTouch: true, userAgent: devices['iPhone 13'].userAgent };

async function open(opts) {
  const ctx = await browser.newContext(opts);
  const page = await ctx.newPage();
  const errors = [];
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  page.on('pageerror', (e) => errors.push(e.message));
  await page.goto(URL);
  await page.waitForSelector('[data-testid=start]', { timeout: 40000 });
  await page.click('[data-testid=start]');
  await page.waitForSelector('[data-testid=spin]:not([disabled])', { timeout: 40000 });
  await page.waitForTimeout(2000);
  return { ctx, page, errors };
}
const rsqa = (page) => page.evaluate(() => window.__rallyScene.rs());
async function play(page, label, scenario, { taps = false, shot = [] } = {}) {
  const bal = await page.evaluate(() => JSON.parse(localStorage.getItem('golden-rally-demo-rs01') || 'null')?.balance ?? 1e9);
  const q0 = await rsqa(page);
  if (scenario) { await page.click('[data-testid=btn-settings]'); await page.waitForSelector(`[data-testid=force-rs-${scenario}]`); }
  const t0 = Date.now();
  await page.click(scenario ? `[data-testid=force-rs-${scenario}]` : '[data-testid=spin]');
  await page.waitForSelector('[data-testid=spin][disabled]', { timeout: 5000 }).catch(() => {});
  const lf = await page.evaluate(() => window.__rallyScene.leftovers());
  check(`${label}: clean start (no plate, overlay, ball or zone left)`, lf.overlay === 0 && lf.gsLayer === 0 && !lf.rpPlate, JSON.stringify(lf));
  for (const ms of shot) { await page.waitForTimeout(Math.max(0, ms - (Date.now() - t0))); await page.screenshot({ path: path.join(SHOTS, `rs01-${label}-t${ms}.png`) }); }
  if (taps) for (let i = 0; i < 30; i++) { await page.mouse.click(195, 300).catch(() => {}); await page.waitForTimeout(100); }
  await page.waitForSelector('[data-testid=spin]:not([disabled])', { timeout: 240000 });
  const ms = Date.now() - t0;
  const { lastRound: r } = await page.evaluate(() => window.__rally);
  const q1 = await rsqa(page);
  const ev = r.state;
  const serves = ev.filter((e) => e.type === 'serve');
  const respins = ev.filter((e) => e.type === 'respin');
  const stages = ev.filter((e) => e.type === 'stageWin');
  check(`${label}: no older gameplay event`, !ev.some((e) => OLD.includes(e.type)));
  check(`${label}: every serve animated, every respin animated`, q1.serves - q0.serves === serves.length && q1.respins - q0.respins === respins.length, `${serves.length} serve(s), ${respins.length} respin(s)`);
  const moved = q1.movedReels.slice(q0.movedReels.length);
  check(`${label}: exactly the struck reels moved, the others stayed still`, JSON.stringify(moved) === JSON.stringify(respins.map((x) => x.reels)) && q1.stablePositions, JSON.stringify(moved));
  const paid = stages.reduce((a, e) => a + e.stageWin, 0) + ev.filter((e) => e.type === 'scatterPay').reduce((a, e) => a + e.amount, 0);
  check(`${label}: stop wins add up to the payout; win shown = payout; balance = before - bet + payout`, Math.min(paid, 500000) === r.payoutMultiplier && norm(await page.textContent('[data-testid=win]')) === norm(fmt(r.payout)) && norm(await page.textContent('[data-testid=balance]')) === norm(fmt(bal - r.amount + r.payout)), stages.map((s) => s.stageWin / 100).join(' + ') + ` = ${r.payoutMultiplier / 100}x`);
  return { r, serves, respins, stages, ms };
}

try {
  const { ctx, page, errors } = await open(PHONE);
  const id = norm(await page.textContent('[data-testid=build-id]'));
  check('390x844: build id FIRST-SERVE-02 visible', id === 'FIRST-SERVE-02', id);
  check('390x844: no buy / modes button, no test button in the player HUD', !(await page.isVisible('[data-testid=btn-buy]')) && !(await page.isVisible('[data-testid=test-point]')) && !(await page.isVisible('[data-testid=test-serve]')));
  await page.screenshot({ path: path.join(SHOTS, 'rs01-390-idle.png') });
  const s1 = await play(page, '1-plain', 'plain');
  check('1. ordinary spin: no Golden Serve, one stop', s1.serves.length === 0 && s1.stages.length === 1);
  const s2 = await play(page, '2-center', 'center', { shot: [2600, 3600, 4400] });
  check('2. Golden Serve strikes the centre zone: reels 3-4 respin', s2.serves.length === 1 && s2.serves[0].zone === 'center' && JSON.stringify(s2.respins[0].reels) === '[2,3]');
  const s3 = await play(page, '3-returns', 'returns', { shot: [5000, 8000] });
  check('3. serve + 2 Return Spins, each to a zone not struck just before', s3.serves.filter((s) => s.kind === 'return').length === 2 && s3.serves.every((s, i) => i === 0 || !s.reels.some((r) => s3.serves[i - 1].reels.includes(r))), s3.serves.map((s) => `${s.kind}:${s.zone}`).join(' → '));
  const s4 = await play(page, '4-nowin', 'nowin');
  check('4. event without any win', s4.serves.length >= 1 && s4.r.payoutMultiplier === 0);
  const s5 = await play(page, '5-win', 'win', { shot: [4500] });
  check('5. visible win on each stop, correctly cumulated', s5.stages.length === 2 && s5.stages[0].stageWin > 0 && s5.stages[1].stageWin > 0 && s5.stages[1].runningTotal === s5.stages[0].stageWin + s5.stages[1].stageWin, s5.stages.map((s) => `stop ${s.stage + 1}: +${s.stageWin / 100}x (total ${s.runningTotal / 100}x)`).join(' · '));
  const s6 = await play(page, '6-smash', 'smash', { shot: [3000, 4000] });
  const sm = s6.serves.find((s) => s.smash);
  check('6. Golden Smash strikes four reels', sm && sm.reels.length === 4 && s6.respins.some((x) => x.reels.length === 4), sm && `${sm.zone} → reels ${sm.reels.map((r) => r + 1).join(',')}`);
  for (const k of ['rally', 'final']) {
    const b = await play(page, `bonus-${k}`, k, { shot: k === 'final' ? [6000] : [] });
    const st = b.r.state.find((e) => e.type === 'rsBonusStart');
    check(`${k}: bonus played on the reels, with serves`, st && st.bonus === k && b.serves.length > 0, `${st?.spins} spins, ${b.serves.length} serves, ${b.r.payout / 1e6}`);
  }
  const sk = await play(page, 'skip-returns', 'returns', { taps: true });
  check('skip (taps): same result, faster', sk.r.payoutMultiplier === s3.r.payoutMultiplier && sk.ms < s3.ms, `${sk.ms} ms vs ${s3.ms} ms`);
  for (let i = 0; i < 4; i++) {
    const x = await play(page, `normal-${i + 1}`, null);
    check(`normal spin ${i + 1}: never forced`, !x.r.forced);
  }
  await page.click('[data-testid=btn-paytable]');
  await page.waitForTimeout(400);
  check('info page: Return Spins rules + measured stats', (await page.isVisible('[data-testid=rs-rules]')) && (await page.isVisible('[data-testid=rs-stats]')));
  await page.screenshot({ path: path.join(SHOTS, 'rs01-390-info.png') });
  await page.keyboard.press('Escape');
  const m = await page.evaluate(() => ({ sw: document.documentElement.scrollWidth, sh: document.documentElement.scrollHeight, iw: innerWidth, ih: innerHeight }));
  check('390x844: no overflow', m.sw <= m.iw && m.sh <= m.ih);
  check('390x844: no console errors', errors.length === 0, errors.slice(0, 2).join(' | '));
  await ctx.close();
  for (const [name, opts] of [['320x568', { viewport: { width: 320, height: 568 }, isMobile: true, hasTouch: true }], ['iphone-se', devices['iPhone SE']], ['1440x900', { viewport: { width: 1440, height: 900 } }]]) {
    const o = await open(opts);
    const x = await play(o.page, `${name}-smash`, 'smash', { shot: [3500] });
    check(`${name}: smash plays, 4 reels`, x.respins.some((r) => r.reels.length === 4));
    const mm = await o.page.evaluate(() => ({ sw: document.documentElement.scrollWidth, iw: innerWidth }));
    check(`${name}: no overflow, no console errors`, mm.sw <= mm.iw && o.errors.length === 0, o.errors.slice(0, 2).join(' | '));
    await o.ctx.close();
  }
} finally {
  await browser.close();
  server?.kill();
  fs.writeFileSync(path.join(HERE, 'return-spins-report.json'), JSON.stringify({ url: URL, failures, results }, null, 1));
  console.log(`\n${results.length - failures}/${results.length} checks passed`);
  process.exit(failures ? 1 : 0);
}
