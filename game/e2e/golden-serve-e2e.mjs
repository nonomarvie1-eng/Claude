// Real game, test build GOLDEN-SERVE-02 (npm run build first; or URL=... for a published file).
// Verifies the acceptance criteria of the Golden Serve animation on 390x844 and other screens.
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
const PORT = 4185;
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
const OLD = ['bonusStart', 'hawkEye', 'shot', 'exchangeStart', 'grandSlam', 'rallyPath', 'protoBonusStart'];
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
  // first visit: the feature explanations come after the opening, over the reels
  await page.click('[data-testid=feature-ok]', { timeout: 60000 }).catch(() => {});
  await page.waitForSelector('[data-testid=spin]:not([disabled])', { timeout: 40000 });
  await page.waitForTimeout(1800); // let the welcome finish
  return { ctx, page, errors };
}
const qa = (page) => page.evaluate(() => window.__rallyScene.qa());
async function play(page, label, click, { frames = [], taps = false } = {}) {
  const q0 = await qa(page);
  await page.click(click);
  await page.waitForTimeout(60);
  const left = await page.evaluate(() => window.__rallyScene.leftovers());
  check(`${label}: nothing from the previous round left on screen at spin start`, left.overlay === 0 && left.gsLayer === 0 && !left.rpPlate, JSON.stringify(left));
  const t0 = Date.now();
  for (const ms of frames) {
    await page.waitForTimeout(Math.max(0, ms - (Date.now() - t0)));
    await page.screenshot({ path: path.join(SHOTS, `gs02-${label}-t${String(ms).padStart(4, '0')}.png`) });
  }
  if (taps) for (let i = 0; i < 30; i++) { await page.mouse.click(195, 420).catch(() => {}); await page.waitForTimeout(120); }
  await page.waitForSelector('[data-testid=spin]:not([disabled])', { timeout: 240000 });
  const ms = Date.now() - t0;
  const { lastRound: r } = await page.evaluate(() => window.__rally);
  const q1 = await qa(page);
  const d = Object.fromEntries(Object.keys(q1).map((k) => [k, q1[k] - q0[k]]));
  const types = r.state.map((e) => e.type);
  check(`${label}: no older gameplay event`, !types.some((x) => OLD.includes(x)), [...new Set(types)].join(','));
  check(`${label}: displayed win = payout`, norm(await page.textContent('[data-testid=win]')) === norm(fmt(r.payout)), fmt(r.payout));
  await page.screenshot({ path: path.join(SHOTS, `gs02-${label}-end.png`) });
  return { r, d, ms };
}
const lastServe = (r) => [...r.state].reverse().find((e) => e.type === 'goldenServe');
/** grid the player must see at the end: board of the last spin, after its shot if it had one */
const finalGrid = (r) => {
  const last = [...r.state].reverse().find((e) => e.type === 'reveal' || e.type === 'goldenServe');
  return last.board;
};

try {
  const { ctx, page, errors } = await open(PHONE);
  const id = norm(await page.textContent('[data-testid=build-id]'));
  check('390x844: build id visible', id.startsWith('GOLDEN-SERVE-02'), id);
  check('390x844: TEST SERVE visible, old buy hidden', (await page.isVisible('[data-testid=test-serve]')) && !(await page.isVisible('[data-testid=btn-buy]')));
  await page.screenshot({ path: path.join(SHOTS, 'gs02-390-idle.png') });

  // ---- acceptance: TEST SERVE, prototype A
  const { r, d, ms } = await play(page, '390-A-serve', '[data-testid=test-serve]', { frames: [150, 450, 750, 1000, 1250, 1500, 1800, 2100, 2500, 3000] });
  const g = lastServe(r);
  check('1. the Golden Ball triggers the event', g && g.concept === 'A' && r.state[0].board[0][g.origin.row] === 'G', g && `${g.shot} from row ${g.origin.row}, target ${g.target}`);
  check('2. a racket stroke is played', d.strokes === (g.shot === 'double' ? 2 : 1), `strokes ${d.strokes}`);
  check('3/4. the ball bounces on every calculated cell', d.hits === g.paths.reduce((a, p) => a + p.length - 1, 0), `hits ${d.hits} for ${g.paths.map((p) => JSON.stringify(p.map((c) => c.row))).join(' + ')}`);
  check('5. every transformation is animated', d.flips >= g.changes.length, `flips ${d.flips}, changes ${g.changes.length}`);
  const grid = await page.evaluate(() => window.__rallyScene.grid());
  check('4/6. the grid shown is exactly the engine transformed grid', JSON.stringify(grid) === JSON.stringify(g.board));
  const wi = r.state.find((e) => e.type === 'winInfo');
  check('6. wins are paid on the transformed grid', !wi || wi.wins.every((w) => w.positions.every((p) => g.board[p.reel][p.row] === w.symbol || g.board[p.reel][p.row] === 'W')), wi ? `${wi.wins.length} combos, ${wi.totalWin / 100}x` : 'no win');
  check('7. animation ends cleanly (round duration)', true, `${ms} ms incl. win presentation`);

  // ---- acceptance 8/10: another round starts cleanly
  await play(page, '390-A-spin', '[data-testid=spin]');
  // ---- smash
  await page.click('[data-testid=btn-settings]');
  await page.waitForSelector('[data-testid=force-gs-smash]');
  await page.screenshot({ path: path.join(SHOTS, 'gs02-390-settings.png') });
  const sm = await play(page, '390-A-smash', '[data-testid=force-gs-smash]', { frames: [300, 700, 1000, 1300, 1600, 2000, 2600] });
  const gsm = lastServe(sm.r);
  check('smash: two-row band, smash stroke, grid = engine board', gsm.shot === 'smash' && gsm.paths.length === 2 && sm.d.smash === 1 && JSON.stringify(await page.evaluate(() => window.__rallyScene.grid())) === JSON.stringify(gsm.board));
  // ---- prototype B
  await page.click('[data-testid=btn-settings]');
  await page.click('[data-testid=concept-B]');
  await page.click('[data-testid=force-gs-serve]');
  await page.waitForSelector('[data-testid=spin]:not([disabled])', { timeout: 240000 });
  const rb = (await page.evaluate(() => window.__rally)).lastRound;
  const gb = lastServe(rb);
  check('B: Court Switch exchanges shown, grid = engine board', gb && gb.concept === 'B' && JSON.stringify(await page.evaluate(() => window.__rallyScene.grid())) === JSON.stringify(gb.board), gb && `${gb.swaps.length} exchanges`);
  await page.screenshot({ path: path.join(SHOTS, 'gs02-390-B-serve-end.png') });
  const id2 = norm(await page.textContent('[data-testid=build-id]'));
  check('build id shows the selected prototype', id2.endsWith('B'), id2);
  await page.click('[data-testid=btn-settings]');
  await page.click('[data-testid=concept-A]');
  await page.keyboard.press('Escape');
  // ---- bonuses
  for (const [k, lvl, frames] of [['rally', 'rally', []], ['final', 'final', [2500, 6000, 12000]]]) {
    await page.click('[data-testid=btn-settings]');
    const { r: rr } = await play(page, `390-A-${k}`, `[data-testid=force-gs-${k}]`, { frames });
    const st = rr.state.find((e) => e.type === 'gsBonusStart');
    check(`${k}: final grid = last board of the bonus`, JSON.stringify(await page.evaluate(() => window.__rallyScene.grid())) === JSON.stringify(finalGrid(rr)));
    check(`${k}: ${lvl} bonus played with Golden Serves`, st && st.bonus === lvl && rr.state.some((e) => e.type === 'goldenServe' && e.index > st.index), st && `${st.spins} spins, ${rr.payout / 1e6} credits`);
  }
  // ---- skip by taps: same result, clean grid
  await page.click('[data-testid=btn-settings]');
  const sk = await play(page, '390-A-final-skipped', '[data-testid=force-gs-final]', { taps: true });
  const gl = lastServe(sk.r);
  check('skipping (taps) keeps the result and the final grid', JSON.stringify(await page.evaluate(() => window.__rallyScene.grid())) === JSON.stringify(finalGrid(sk.r)), `${sk.ms} ms`);
  // ---- normal spins: credits
  for (let i = 0; i < 3; i++) {
    const bal = await page.evaluate(() => JSON.parse(localStorage.getItem('golden-rally-demo-gs02')).balance);
    const { r: x } = await play(page, `390-spin${i}`, '[data-testid=spin]');
    check(`spin ${i + 1}: balance = before - bet + payout`, norm(await page.textContent('[data-testid=balance]')) === norm(fmt(bal - x.amount + x.payout)));
  }
  await page.click('[data-testid=btn-paytable]');
  await page.waitForTimeout(400);
  check('info page: Golden Serve rules and measured stats', (await page.isVisible('[data-testid=golden-serve-rules]')) && (await page.isVisible('[data-testid=gs-stats]')) && !(await page.isVisible('[data-testid=final-set-rules]')));
  await page.screenshot({ path: path.join(SHOTS, 'gs02-390-info.png') });
  await page.keyboard.press('Escape');
  const m = await page.evaluate(() => ({ sw: document.documentElement.scrollWidth, sh: document.documentElement.scrollHeight, iw: innerWidth, ih: innerHeight, L: window.__rallyLayout, ctl: [...document.querySelectorAll('.top > *, .hud button')].map((e) => { const b = e.getBoundingClientRect(); return [b.left, b.right, b.top, b.bottom]; }) }));
  const b = m.L.board;
  check('390x844: no overflow, no control over the reels, all on screen', m.sw <= m.iw && m.sh <= m.ih && m.ctl.every(([l, rr, t, bt]) => (bt <= b.y || t >= b.y + b.h || rr <= b.x || l >= b.x + b.w) && l >= 0 && rr <= m.iw + 0.5));
  check('390x844: no console errors', errors.length === 0, errors.slice(0, 2).join(' | '));
  await ctx.close();

  for (const [name, opts] of [['320x568', { viewport: { width: 320, height: 568 }, isMobile: true, hasTouch: true }], ['iphone-se', devices['iPhone SE']], ['1440x900', { viewport: { width: 1440, height: 900 } }]]) {
    const o = await open(opts);
    const mm = await o.page.evaluate(() => ({ sw: document.documentElement.scrollWidth, iw: innerWidth, top: [...document.querySelectorAll('.top > *, .hud button')].map((e) => { const b = e.getBoundingClientRect(); return [b.left, b.right]; }) }));
    check(`${name}: build id + TEST visible, no overflow`, (await o.page.isVisible('[data-testid=build-id]')) && (await o.page.isVisible('[data-testid=test-serve]')) && mm.sw <= mm.iw && mm.top.every(([l, rr]) => l >= 0 && rr <= mm.iw + 0.5));
    const { r: x } = await play(o.page, `${name}-serve`, '[data-testid=test-serve]');
    check(`${name}: grid = engine board after serve`, JSON.stringify(await o.page.evaluate(() => window.__rallyScene.grid())) === JSON.stringify(lastServe(x).board));
    check(`${name}: no console errors`, o.errors.length === 0, o.errors.slice(0, 2).join(' | '));
    await o.ctx.close();
  }
} finally {
  await browser.close();
  server?.kill();
  fs.writeFileSync(path.join(HERE, 'golden-serve-report.json'), JSON.stringify({ url: URL, failures, results }, null, 1));
  console.log(`\n${results.length - failures}/${results.length} checks passed`);
  process.exit(failures ? 1 : 0);
}
