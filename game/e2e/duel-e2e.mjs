// Real game, test build DUEL-01 (npm run build first; or URL=... for the published file).
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
const PORT = 4189;
const URL = process.env.URL || `http://localhost:${PORT}/?lang=fr`;
const DUEL = JSON.parse(fs.readFileSync(path.join(ROOT, '..', 'shared', 'championship-duel.json'), 'utf8'));
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
const OLD = ['bonusStart', 'hawkEye', 'shot', 'exchangeStart', 'rallyPath', 'protoBonusStart', 'goldenServe', 'gsBonusStart'];
const CAPTION = { DOUBLE_FAULT: 'DOUBLE FAUTE', ACE: 'ACE', WINNER: 'COUP GAGNANT', LOST: 'POINT PERDU', RALLY_WON: 'POINT GAGNÉ', GOLDEN: null };
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
  await page.waitForTimeout(1800);
  return { ctx, page, errors };
}
const court = (page) => page.evaluate(() => window.__rallyScene.court());
const idle = (page) => page.waitForSelector('[data-testid=spin]:not([disabled])', { timeout: 240000 });
async function lab(page, click, label, { taps = false, shot = [] } = {}) {
  const bal0 = norm(await page.textContent('[data-testid=balance]'));
  const n0 = (await court(page)).durations.length;
  if (click.startsWith('duel-')) { await page.click('[data-testid=btn-settings]'); await page.waitForSelector(`[data-testid=${click}]`); }
  const t0 = Date.now();
  await page.click(`[data-testid=${click}]`);
  await page.waitForSelector('[data-testid=spin][disabled]', { timeout: 5000 }).catch(() => {});
  for (const ms of shot) { await page.waitForTimeout(Math.max(0, ms - (Date.now() - t0))); await page.screenshot({ path: path.join(SHOTS, `duel01-${label}-t${ms}.png`) }); }
  if (taps) for (let i = 0; i < 25; i++) { await page.mouse.click(195, 430).catch(() => {}); await page.waitForTimeout(80); }
  await idle(page);
  const c = await court(page);
  const lab = await page.evaluate(() => window.__duelLab);
  const pts = lab.events.filter((e) => e.type === 'duelPoint');
  check(`${label}: balance unchanged (test point not credited)`, norm(await page.textContent('[data-testid=balance]')) === bal0);
  check(`${label}: court closed, reels back`, !c.visible && (await page.evaluate(() => window.__rallyScene.leftovers())).overlay === 0);
  return { pts, durs: c.durations.slice(n0), ms: Date.now() - t0, c };
}

try {
  const { ctx, page, errors } = await open(PHONE);
  const id = norm(await page.textContent('[data-testid=build-id]'));
  check('390x844: build id DUEL-01 visible', id === 'DUEL-01', id);
  check('390x844: TEST POINT visible, old buy hidden', (await page.isVisible('[data-testid=test-point]')) && !(await page.isVisible('[data-testid=btn-buy]')));
  await page.screenshot({ path: path.join(SHOTS, 'duel01-390-idle.png') });
  // ---- reproducible demo: fault, ace, winner
  const d = await lab(page, 'test-point', '390-demo3', { shot: [1500, 3000, 5000, 7500] });
  check('demo: double fault, ace, winner (engine outcomes)', d.pts.map((p) => p.outcome).join(',') === 'DOUBLE_FAULT,ACE,WINNER', d.pts.map((p) => `${p.outcome} ${p.prize / 100}x`).join(' · '));
  check('demo: the two serves of the double fault are drawn', d.pts[0].firstServe === 'FAULT' && d.pts[0].secondServe === 'DOUBLE_FAULT');
  check('demo: point prizes follow the documented scenarios', d.pts[1].prize / 100 === DUEL.pointScenarios.ace.prizeX && d.pts[2].prize / 100 === DUEL.pointScenarios.winner.prizeX && d.pts[0].prize === 0);
  check('demo: one court animation per point', d.durs.length === 3);
  // timing measured without screenshots (they freeze rendering): second run of the same demo
  const d2 = await lab(page, 'test-point', '390-demo3-timing');
  const act = Object.fromEntries(d2.durs.map((x) => [x.outcome, x.actionMs]));
  // targets of the brief (action, before the result announcement): double fault < 1.5 s, ace 0.8-1.2 s, rally 1-2 s
  check('action time: double fault < 1.5 s, ace <= 1.2 s, winner rally <= 2 s', act.DOUBLE_FAULT < 1500 && act.ACE <= 1200 && act.WINNER <= 2000, d2.durs.map((x) => `${x.outcome}: action ${x.actionMs} ms + result ${x.animMs - x.actionMs} ms (wall ${x.ms} ms @ ${Math.round((x.frames * 1000) / x.ms)} fps)`).join(' · '));
  // ---- each point scenario
  for (const [k, sc] of Object.entries(DUEL.pointScenarios)) {
    const r = await lab(page, `duel-pt-${k}`, `390-${k}`);
    const p = r.pts[0];
    const cap = CAPTION[p.outcome] ?? (sc.level === 'final' ? 'GOLDEN SMASH' : 'GOLDEN WINNER');
    check(`${k}: outcome ${p.outcome}, prize ${p.prize / 100}x, caption shown`, p.outcome === sc.outcome && p.prize / 100 === sc.prizeX && r.c.lastCaption === cap, `${r.c.lastCaption} · ${r.durs[0]?.ms} ms`);
    await page.screenshot({ path: path.join(SHOTS, `duel01-390-${k}-end.png`) });
  }
  // ---- skip by taps: same result, faster
  const sk = await lab(page, 'test-point', '390-demo3-skipped', { taps: true });
  check('skip (taps): same outcomes, faster', sk.pts.map((p) => p.outcome).join(',') === 'DOUBLE_FAULT,ACE,WINNER' && sk.ms < d.ms, `${sk.ms} ms vs ${d.ms} ms`);
  // ---- complete forced rounds (credited, fictitious credits)
  for (const k of ['tiebreak', 'final']) {
    const bal = await page.evaluate(() => JSON.parse(localStorage.getItem('golden-rally-demo-duel01')).balance);
    await page.click('[data-testid=btn-settings]');
    await page.waitForSelector(`[data-testid=force-duel-${k}]`);
    if (k === 'tiebreak') await page.screenshot({ path: path.join(SHOTS, 'duel01-390-settings.png') });
    await page.click(`[data-testid=force-duel-${k}]`);
    await page.waitForTimeout(4000);
    await page.screenshot({ path: path.join(SHOTS, `duel01-390-round-${k}.png`) });
    await idle(page);
    const { lastRound: r } = await page.evaluate(() => window.__rally);
    const st = r.state.find((e) => e.type === 'duelStart');
    check(`${k} round: duel level and point count`, st.level === k && r.state.filter((e) => e.type === 'duelPoint').length === DUEL.rules.LEVELS[k].POINTS);
    check(`${k} round: no older gameplay event`, !r.state.some((e) => OLD.includes(e.type)));
    check(`${k} round: win shown = payout; balance = before - bet + payout`, norm(await page.textContent('[data-testid=win]')) === norm(fmt(r.payout)) && norm(await page.textContent('[data-testid=balance]')) === norm(fmt(bal - r.amount + r.payout)), `${r.payout / 1e6}`);
    const lf = await page.evaluate(() => window.__rallyScene.leftovers());
    check(`${k} round: court closed after the bonus`, !lf.court && lf.overlay === 0, JSON.stringify(lf));
  }
  // ---- normal spins
  for (let i = 0; i < 3; i++) {
    const bal = await page.evaluate(() => JSON.parse(localStorage.getItem('golden-rally-demo-duel01')).balance);
    await page.click('[data-testid=spin]');
    await page.waitForTimeout(60);
    const lf = await page.evaluate(() => window.__rallyScene.leftovers());
    check(`spin ${i + 1}: nothing left from the previous round`, !lf.court && lf.overlay === 0 && lf.gsLayer === 0 && !lf.rpPlate, JSON.stringify(lf));
    await idle(page);
    const { lastRound: r } = await page.evaluate(() => window.__rally);
    check(`spin ${i + 1}: balance = before - bet + payout`, norm(await page.textContent('[data-testid=balance]')) === norm(fmt(bal - r.amount + r.payout)));
  }
  await page.click('[data-testid=btn-paytable]');
  await page.waitForTimeout(400);
  check('info page: Championship Duel rules + event table + exact stats', (await page.isVisible('[data-testid=duel-rules]')) && (await page.isVisible('[data-testid=duel-table]')) && (await page.isVisible('[data-testid=duel-stats]')));
  await page.screenshot({ path: path.join(SHOTS, 'duel01-390-info.png'), fullPage: false });
  await page.keyboard.press('Escape');
  const m = await page.evaluate(() => ({ sw: document.documentElement.scrollWidth, sh: document.documentElement.scrollHeight, iw: innerWidth, ih: innerHeight }));
  check('390x844: no overflow', m.sw <= m.iw && m.sh <= m.ih);
  check('390x844: no console errors', errors.length === 0, errors.slice(0, 2).join(' | '));
  await ctx.close();

  for (const [name, opts] of [['320x568', { viewport: { width: 320, height: 568 }, isMobile: true, hasTouch: true }], ['iphone-se', devices['iPhone SE']], ['1440x900', { viewport: { width: 1440, height: 900 } }]]) {
    const o = await open(opts);
    const r = await lab(o.page, 'test-point', `${name}-demo3`, { shot: [5200] });
    check(`${name}: demo plays fault, ace, winner`, r.pts.map((p) => p.outcome).join(',') === 'DOUBLE_FAULT,ACE,WINNER');
    const mm = await o.page.evaluate(() => ({ sw: document.documentElement.scrollWidth, iw: innerWidth }));
    check(`${name}: no overflow, no console errors`, mm.sw <= mm.iw && o.errors.length === 0, o.errors.slice(0, 2).join(' | '));
    await o.ctx.close();
  }
} finally {
  await browser.close();
  server?.kill();
  fs.writeFileSync(path.join(HERE, 'duel-report.json'), JSON.stringify({ url: URL, failures, results }, null, 1));
  console.log(`\n${results.length - failures}/${results.length} checks passed`);
  process.exit(failures ? 1 : 0);
}
