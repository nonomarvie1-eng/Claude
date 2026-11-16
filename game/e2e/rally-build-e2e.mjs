// Real game, test build RALLY-PATH-01 (npm run build first).  Checks what the
// player actually gets: build id, Spin -> Rally Path engine, TEST 6 COUPS button,
// no v6 Final Set event, credits accounting, mobile layout.  Screenshots: e2e/screenshots/rp01-*
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
const PORT = 4183;
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
const OLD = ['bonusStart', 'hawkEye', 'shot', 'exchangeStart', 'grandSlam', 'markExpire', 'exchangeEnd', 'bonusEnd'];
const fmt = (a) => new Intl.NumberFormat('fr-FR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(a / 1e6);
const norm = (s) => s.replace(/\s/g, ' ').replace(/[  ]/g, ' ').trim();
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });

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
  return { ctx, page, errors };
}
async function playAndCheck(page, label, click, frames = []) {
  const before = norm(await page.textContent('[data-testid=balance]'));
  await page.click(click);
  const t0 = Date.now();
  for (const ms of frames) {
    await page.waitForTimeout(Math.max(0, ms - (Date.now() - t0)));
    await page.screenshot({ path: path.join(SHOTS, `rp01-${label}-t${ms}.png`) });
  }
  await page.waitForSelector('[data-testid=spin]:not([disabled])', { timeout: 240000 });
  const { lastRound: r } = await page.evaluate(() => window.__rally);
  const types = r.state.map((e) => e.type);
  check(`${label}: no v6 Final Set event (Hawk-Eye, shots, exchanges)`, !types.some((x) => OLD.includes(x)), [...new Set(types)].join(','));
  check(`${label}: displayed win = payout`, norm(await page.textContent('[data-testid=win]')) === norm(fmt(r.payout)), fmt(r.payout));
  return { r, ms: Date.now() - t0, before };
}

try {
  // ---- iPhone 13 class: 390 x 844
  const { ctx, page, errors } = await open({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, isMobile: true, hasTouch: true, userAgent: devices['iPhone 13'].userAgent });
  const vp = page.viewportSize();
  check('viewport 390x844', vp.width === 390 && vp.height === 844, `${vp.width}x${vp.height}`);
  const id = norm(await page.textContent('[data-testid=build-id]'));
  check('build id RALLY-PATH-01 visible', id === 'RALLY-PATH-01' && (await page.isVisible('[data-testid=build-id]')), id);
  check('old buy / modes button hidden', !(await page.isVisible('[data-testid=btn-buy]')));
  check('TEST 6 COUPS button visible', await page.isVisible('[data-testid=test-six]'));
  await page.screenshot({ path: path.join(SHOTS, 'rp01-390-idle.png') });
  const { r, ms } = await playAndCheck(page, '390-test6', '[data-testid=test-six]', [700, 1200, 1500, 1800, 2100, 2400, 2800, 3600]);
  const rp = r.state.find((e) => e.type === 'rallyPath');
  check('TEST 6 COUPS: Golden Ball crosses the 6 reels', rp && rp.length === 6 && rp.path.map((p) => p.reel).join('') === '012345', rp && JSON.stringify(rp.path));
  check('TEST 6 COUPS: every return is a racket on the same or adjacent row', rp && rp.path.every((p, i) => i === 0 ? r.state[0].board[0][p.row] === 'G' : r.state[0].board[p.reel][p.row] === 'H4' && Math.abs(p.row - rp.path[i - 1].row) <= 1));
  check('TEST 6 COUPS: Championship Shot', rp && rp.championshipShot === true, `${rp.reward / 100}x`);
  check('TEST 6 COUPS: round duration', true, `${ms} ms`);
  await page.screenshot({ path: path.join(SHOTS, 'rp01-390-test6-end.png') });
  // bonus scenarios through the Settings test buttons
  for (const [k, lvl] of [['game_rally', 'rally'], ['game_final', 'final']]) {
    await page.click('[data-testid=btn-settings]');
    await page.waitForSelector(`[data-testid=force-${k}]`);
    if (k === 'game_rally') await page.screenshot({ path: path.join(SHOTS, 'rp01-390-settings.png') });
    const { r: rb } = await playAndCheck(page, `390-${k}`, `[data-testid=force-${k}]`, k === 'game_final' ? [3500, 6000, 9000] : [3500]);
    const st = rb.state.find((e) => e.type === 'protoBonusStart');
    check(`${k}: new bonus ${lvl} played`, st && st.bonus === lvl, st && `${st.spins} spins`);
    if (k === 'game_final') check('game_final: Second Serve shown in the book', rb.state.some((e) => e.type === 'secondServe'));
  }
  // random real spins: balance accounting
  for (let i = 0; i < 4; i++) {
    const bal = await page.evaluate(() => JSON.parse(localStorage.getItem('golden-rally-demo-rp01')).balance);
    const { r: rr } = await playAndCheck(page, `390-spin${i + 1}`, '[data-testid=spin]');
    check(`spin ${i + 1}: balance = before - bet + payout`, norm(await page.textContent('[data-testid=balance]')) === norm(fmt(bal - rr.amount + rr.payout)));
  }
  // info page shows Rally Path rules, not the Final Set
  await page.click('[data-testid=btn-paytable]');
  await page.waitForTimeout(400);
  check('info page: Rally Path rules present, Final Set rules absent', (await page.isVisible('[data-testid=rally-path-rules]')) && !(await page.isVisible('[data-testid=final-set-rules]')));
  await page.screenshot({ path: path.join(SHOTS, 'rp01-390-info.png') });
  await page.keyboard.press('Escape');
  const m = await page.evaluate(() => ({ hud: [...document.querySelectorAll('.hud button')].map((e) => { const b = e.getBoundingClientRect(); return [b.left, b.right, b.top, b.bottom]; }), sw: document.documentElement.scrollWidth, sh: document.documentElement.scrollHeight, iw: innerWidth, ih: innerHeight, L: window.__rallyLayout, top: [...document.querySelectorAll('.top > *')].map((e) => { const b = e.getBoundingClientRect(); return [b.left, b.right, b.top, b.bottom]; }) }));
  check('390: no horizontal/vertical overflow', m.sw <= m.iw && m.sh <= m.ih);
  const b = m.L.board;
  check('390: top bar items do not overlap the reels', m.top.every(([l, rr, t, bt]) => bt <= b.y || t >= b.y + b.h || rr <= b.x || l >= b.x + b.w));
  check('390: HUD buttons do not overlap the reels', m.hud.every(([l, rr, t, bt]) => bt <= b.y || t >= b.y + b.h || rr <= b.x || l >= b.x + b.w));
  check('390: top bar items stay on screen', m.top.every(([l, rr]) => l >= 0 && rr <= m.iw + 0.5), JSON.stringify(m.top.map((x) => x.map(Math.round))));
  check('390: no console errors', errors.length === 0, errors.slice(0, 2).join(' | '));
  await ctx.close();
  // ---- other screens: layout + TEST button
  for (const [name, opts] of [['320x568', { viewport: { width: 320, height: 568 }, isMobile: true, hasTouch: true }], ['iphone-se', devices['iPhone SE']], ['1440x900', { viewport: { width: 1440, height: 900 } }]]) {
    const o = await open(opts);
    const mm = await o.page.evaluate(() => ({ sw: document.documentElement.scrollWidth, iw: innerWidth, top: [...document.querySelectorAll('.top > *')].map((e) => { const b = e.getBoundingClientRect(); return [b.left, b.right]; }) }));
    check(`${name}: build id + TEST button visible, no overflow`, (await o.page.isVisible('[data-testid=build-id]')) && (await o.page.isVisible('[data-testid=test-six]')) && mm.sw <= mm.iw && mm.top.every(([l, rr]) => l >= 0 && rr <= mm.iw + 0.5));
    await playAndCheck(o.page, `${name}-test6`, '[data-testid=test-six]');
    await o.page.screenshot({ path: path.join(SHOTS, `rp01-${name}-test6-end.png`) });
    await o.ctx.close();
  }
} finally {
  await browser.close();
  server?.kill();
  fs.writeFileSync(path.join(HERE, 'rally-build-report.json'), JSON.stringify({ url: URL, failures, results }, null, 1));
  console.log(`\n${results.length - failures}/${results.length} checks passed`);
  process.exit(failures ? 1 : 0);
}
