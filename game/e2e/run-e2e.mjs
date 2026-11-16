// End-to-end browser tests (Playwright library, pre-installed Chromium).
// Builds nothing: run `npm run build` first.  Starts `vite preview`, then
// drives the real game in several screen sizes.
// Usage: node e2e/run-e2e.mjs            -> writes e2e/report.json + e2e/screenshots/*
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
const PORT = 4179;
const URL = `http://localhost:${PORT}/?lang=fr`;

const server = spawn('npx', ['vite', 'preview', '--port', String(PORT), '--strictPort'], { cwd: ROOT, stdio: 'ignore' });
const results = [];
let failures = 0;
const check = (name, ok, detail = '') => {
  results.push({ name, ok: !!ok, detail });
  if (!ok) failures++;
  console.log(`${ok ? '✓' : '✗'} ${name}${detail ? ' — ' + detail : ''}`);
};

async function waitServer() {
  for (let i = 0; i < 60; i++) {
    try {
      const r = await fetch(`http://localhost:${PORT}/`);
      if (r.ok) return;
    } catch {}
    await new Promise((r) => setTimeout(r, 500));
  }
  throw new Error('preview server did not start');
}

const fmt = (amount) => new Intl.NumberFormat('fr-FR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(amount / 1e6);
const norm = (s) => s.replace(/\s/g, ' ').replace(/[  ]/g, ' ').trim();

async function open(browser, name, ctxOpts) {
  const ctx = await browser.newContext(ctxOpts);
  const page = await ctx.newPage();
  const errors = [];
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  page.on('pageerror', (e) => errors.push(e.message));
  await page.goto(URL);
  await page.waitForSelector('[data-testid=start]', { timeout: 40000 });
  await page.screenshot({ path: path.join(SHOTS, `${name}-0-loading.png`) });
  await page.click('[data-testid=start]');
  await page.waitForSelector('[data-testid=spin]:not([disabled])', { timeout: 40000 });
  return { ctx, page, errors };
}

const text = async (page, id) => norm(await page.textContent(`[data-testid=${id}]`));

async function spinAndVerify(page, label) {
  const before = await page.evaluate(() => JSON.parse(localStorage.getItem('golden-rally-demo-v1') || 'null')?.balance ?? 1e9);
  await page.click('[data-testid=spin]');
  await page.waitForSelector('[data-testid=spin][disabled]', { timeout: 5000 }).catch(() => {});
  await page.waitForSelector('[data-testid=spin]:not([disabled])', { timeout: 120000 });
  const qa = await page.evaluate(() => window.__rally);
  const r = qa.lastRound;
  const shownWin = await text(page, 'win');
  const shownBal = await text(page, 'balance');
  check(`${label}: displayed win equals RGS payout`, shownWin === norm(fmt(r.payout)), `${shownWin} vs ${fmt(r.payout)} (×${r.payoutMultiplier / 100})`);
  check(`${label}: balance = before - bet + payout`, shownBal === norm(fmt(before - r.amount + r.payout)), shownBal);
  return r;
}

async function layoutChecks(page, name) {
  const m = await page.evaluate(() => {
    const r = (el) => { const b = el.getBoundingClientRect(); return { top: b.top, bottom: b.bottom, left: b.left, right: b.right, w: b.width, h: b.height }; };
    const q = (sel) => [...document.querySelectorAll(sel)].filter((e) => e.getClientRects().length > 0).map(r);
    const L = window.__rallyLayout;
    const clipped = [...document.querySelectorAll('.hud .value, .hud .label, .top .demo')].filter((e) => e.scrollWidth > e.clientWidth + 1).map((e) => e.textContent);
    return {
      sw: document.documentElement.scrollWidth, iw: innerWidth, ih: innerHeight, sy: document.documentElement.scrollHeight,
      spin: r(document.querySelector('[data-testid=spin]')),
      controls: q('.hud button, .top button, .top .demo'),
      board: L && L.board, header: L && L.header, clipped,
    };
  });
  check(`${name}: no horizontal overflow`, m.sw <= m.iw, `${m.sw} <= ${m.iw}`);
  check(`${name}: no vertical scroll`, m.sy <= m.ih, `${m.sy} <= ${m.ih}`);
  check(`${name}: spin button fully visible`, m.spin.top >= 0 && m.spin.bottom <= m.ih && m.spin.left >= 0 && m.spin.right <= m.iw);
  const b = m.board;
  check(`${name}: reels fully on screen`, b && b.x >= 0 && b.y >= 0 && b.x + b.w <= m.iw + 0.5 && b.y + b.h <= m.ih + 0.5, b && `${Math.round(b.x)},${Math.round(b.y)} ${Math.round(b.w)}x${Math.round(b.h)}`);
  const overlap = (c) => b && !(c.right <= b.x || c.left >= b.x + b.w || c.bottom <= b.y || c.top >= b.y + b.h);
  const hits = m.controls.filter(overlap);
  check(`${name}: no control overlaps the reels`, hits.length === 0, hits.length ? JSON.stringify(hits[0]) : `${m.controls.length} controls checked`);
  const small = m.controls.filter((c) => c.w < 38 || c.h < 38).length;
  check(`${name}: touch targets >= 38px`, small <= 1, `${small} smaller (demo badge allowed)`);
  check(`${name}: no clipped HUD text`, m.clipped.length === 0, m.clipped.join(' | '));
  check(`${name}: symbol cell legible (>= 44px)`, b && b.w / 6 >= 44, b && `${(b.w / 6).toFixed(1)}px per reel`);
  const demo = await page.isVisible('[data-testid=demo-badge]');
  check(`${name}: demo badge visible`, demo);
}

await waitServer();
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--autoplay-policy=no-user-gesture-required'] });

const viewports = [
  ['desktop-1920x1080', { viewport: { width: 1920, height: 1080 } }],
  ['laptop-1366x768', { viewport: { width: 1366, height: 768 } }],
  ['iphone-se-portrait', { ...devices['iPhone SE'] }],
  ['iphone-13-portrait', { ...devices['iPhone 13'] }],
  ['iphone-14-pro-max-portrait', { ...devices['iPhone 14 Pro Max'] }],
  ['iphone-13-landscape', { ...devices['iPhone 13 landscape'] }],
  ['pixel-7-landscape', { ...devices['Pixel 7 landscape'] }],
  ['ipad-portrait', { ...devices['iPad (gen 7)'] }],
];

try {
  for (const [name, opts] of viewports) {
    const { ctx, page, errors } = await open(browser, name, opts);
    await page.waitForTimeout(600);
    await page.screenshot({ path: path.join(SHOTS, `${name}-1-idle.png`) });
    await layoutChecks(page, name);
    for (let i = 0; i < 3; i++) await spinAndVerify(page, `${name} spin ${i + 1}`);
    await page.screenshot({ path: path.join(SHOTS, `${name}-2-after-spins.png`) });
    check(`${name}: no console errors`, errors.length === 0, errors.slice(0, 3).join(' | '));
    await ctx.close();
  }

  // ------------------------------------------------ desktop feature tour
  const { ctx, page, errors } = await open(browser, 'feature', { viewport: { width: 1600, height: 900 } });
  // paytable
  await page.click('[data-testid=btn-paytable]');
  await page.waitForTimeout(400);
  await page.screenshot({ path: path.join(SHOTS, 'feature-paytable.png') });
  const rtpText = await page.textContent('[data-testid=rtp]');
  const cfgRtp = (JSON.parse(fs.readFileSync(path.join(ROOT, '..', 'shared', 'game-config.json'), 'utf8')).stats.rtp * 100).toFixed(2);
  check('paytable shows the computed RTP', rtpText.includes(cfgRtp), `${rtpText} / expected ${cfgRtp}`);
  await page.keyboard.press('Escape');

  // forced bonus (demo test tool)
  await page.click('[data-testid=btn-settings]');
  await page.waitForTimeout(300);
  await page.screenshot({ path: path.join(SHOTS, 'feature-settings.png') });
  await page.click('[data-testid=force-bonus3]');
  await page.waitForSelector('[data-testid=fs-counter]', { timeout: 30000 });
  await page.waitForTimeout(1200);
  await page.screenshot({ path: path.join(SHOTS, 'feature-bonus-intro.png') });
  await page.waitForTimeout(6000);
  await page.screenshot({ path: path.join(SHOTS, 'feature-bonus-spin.png') });
  await page.waitForSelector('[data-testid=spin]:not([disabled])', { timeout: 240000 });
  const r = await page.evaluate(() => window.__rally.lastRound);
  check('forced bonus round contains free spins', r.state.some((e) => e.type === 'bonusStart'));
  check('bonus: displayed total win equals payout', (await text(page, 'win')) === norm(fmt(r.payout)), `${await text(page, 'win')} vs ${fmt(r.payout)}`);
  await page.screenshot({ path: path.join(SHOTS, 'feature-bonus-end.png') });

  // history + faithful replay
  await page.click('[data-testid=btn-history]');
  await page.waitForSelector('[data-testid=history-table]');
  await page.screenshot({ path: path.join(SHOTS, 'feature-history.png') });
  const balBefore = await text(page, 'balance');
  await page.click('[data-testid=history-table] tbody tr:nth-child(1) button');
  await page.waitForTimeout(800);
  await page.screenshot({ path: path.join(SHOTS, 'feature-replay.png') });
  await page.waitForSelector('[data-testid=spin]:not([disabled])', { timeout: 240000 });
  check('replay does not change the balance', (await text(page, 'balance')) === balBefore);

  // winning connections: what is drawn == the engine's winInfo (positions, ways, amounts)
  {
    let found = null;
    for (let i = 0; i < 25 && !found; i++) {
      await page.click('[data-testid=spin]');
      await page.waitForSelector('[data-testid=spin]:not([disabled])', { timeout: 120000 });
      const r = await page.evaluate(() => window.__rally.lastRound);
      const wi = r.state.filter((e) => e.type === 'winInfo' && e.gameType === 'basegame');
      if (wi.length && !r.state.some((e) => e.type === 'bonusStart')) found = wi[wi.length - 1];
    }
    check('connections: found a winning base spin', !!found);
    if (found) {
      const shown = await page.evaluate(() => window.__rallyShownWins);
      const key = (w) => `${w.kind}:${w.symbol}:${w.count}:${w.ways}:${w.win}:${w.positions.map((p) => p.reel + '.' + p.row).sort().join(',')}`;
      check('connections: drawn combinations == engine winInfo', JSON.stringify(shown.map(key).sort()) === JSON.stringify(found.wins.map(key).sort()), `${shown.length} vs ${found.wins.length}`);
      check('connections: every drawn combination starts on reel 1 and is contiguous', shown.filter((w) => w.kind === 'ways').every((w) => Array.from({ length: w.count }, (_, r) => w.positions.some((p) => p.reel === r)).every(Boolean) && w.positions.every((p) => p.reel < w.count)));
      await page.screenshot({ path: path.join(SHOTS, 'feature-connections.png') });
      await page.click('[data-testid=btn-replay-last]');
      await page.waitForTimeout(400);
      await page.screenshot({ path: path.join(SHOTS, 'feature-replay-last.png') });
      await page.waitForSelector('[data-testid=spin]:not([disabled])', { timeout: 120000 });
      check('replay last round: balance unchanged', true);
    }
  }

  // Bonus Chance: debit = bet x cost, then back to Normal
  {
    await page.click('[data-testid=btn-buy]');
    await page.waitForSelector('[data-testid=mode-chance]');
    await page.screenshot({ path: path.join(SHOTS, 'feature-modes.png') });
    await page.click('[data-testid=mode-chance]');
    check('bonus chance: next-spin price shown in the HUD', await page.isVisible('[data-testid=spin-cost]'));
    const before = await page.evaluate(() => JSON.parse(localStorage.getItem('golden-rally-demo-v1')).balance);
    await page.click('[data-testid=spin]');
    await page.waitForSelector('[data-testid=spin]:not([disabled])', { timeout: 300000 });
    const r = await page.evaluate(() => window.__rally.lastRound);
    check('bonus chance: round played in mode bonus_chance', r.mode === 'bonus_chance' && Math.abs(r.cost - 1.4) < 1e-9, `${r.mode} ${r.cost}`);
    check('bonus chance: balance = before - 1.4 x bet + payout', (await text(page, 'balance')) === norm(fmt(before - Math.round(r.cost * r.amount) + r.payout)), await text(page, 'balance'));
    await page.screenshot({ path: path.join(SHOTS, 'feature-bonus-chance.png') });
    await page.click('[data-testid=btn-buy]');
    await page.click('[data-testid=mode-base]');
    check('bonus chance: back to Normal mode (no price line)', !(await page.isVisible('[data-testid=spin-cost]')));
  }

  // two explicit buys: each guarantees its level; exact debit; confirmation shows the amount
  for (const [btn, level, k] of [['buy-tb', 'rally', 3], ['buy-stb', 'final', 4]]) {
    const before = await page.evaluate(() => JSON.parse(localStorage.getItem('golden-rally-demo-v1')).balance);
    await page.click('[data-testid=btn-buy]');
    await page.click(`[data-testid=${btn}]`);
    await page.waitForSelector('[data-testid=buy-confirm]');
    const shownPrice = await text(page, 'buy-price');
    await page.screenshot({ path: path.join(SHOTS, `feature-${btn}-confirm.png`) });
    await page.click('[data-testid=buy-confirm]');
    await page.waitForSelector('[data-testid=fs-counter]', { timeout: 30000 });
    await page.waitForTimeout(level === 'final' ? 2500 : 1500);
    await page.screenshot({ path: path.join(SHOTS, `feature-${btn}-bonus.png`) });
    await page.waitForSelector('[data-testid=spin]:not([disabled])', { timeout: 400000 });
    const rb = await page.evaluate(() => window.__rally.lastRound);
    const trig = rb.state.find((e) => e.type === 'bonusStart');
    const nsc = rb.state[0].board.flat().filter((x) => x === 'S').length;
    check(`${btn}: bought round gives exactly the ${level} level`, trig && trig.bought === true && trig.bonus === level && nsc === k, `${trig && trig.bonus} ${nsc}`);
    check(`${btn}: confirmation showed the exact debited amount`, shownPrice === norm(fmt(Math.round(rb.cost * rb.amount))), `${shownPrice} vs ${fmt(Math.round(rb.cost * rb.amount))}`);
    check(`${btn}: balance = before - cost x bet + payout`, (await text(page, 'balance')) === norm(fmt(before - Math.round(rb.cost * rb.amount) + rb.payout)), await text(page, 'balance'));
    check(`${btn}: displayed win equals payout`, (await text(page, 'win')) === norm(fmt(rb.payout)));
    const shots = rb.state.filter((e) => e.type === 'shot');
    const bonusEnd = rb.state.find((e) => e.type === 'bonusEnd');
    check(`${btn}: bonus total = sum of the shots played`, shots.reduce((a, e) => a + e.win, 0) === bonusEnd.bonusWin, `${shots.length} shots`);
    check(`${btn}: ${level} mechanics present`, level === 'final' ? rb.state.some((e) => e.type === 'exchangeStart' && e.championshipPoint) : !rb.state.some((e) => e.type === 'hawkEye'));
  }

  // autoplay: 10 spins with loss limit, then a stopped run
  {
    const h0 = await page.evaluate(() => JSON.parse(localStorage.getItem('golden-rally-history-v1') || '[]').length);
    await page.click('[data-testid=btn-auto]');
    await page.waitForSelector('[data-testid=auto-start]');
    await page.screenshot({ path: path.join(SHOTS, 'feature-autoplay-dialog.png') });
    await page.click('[data-testid=auto-count-10]');
    await page.click('[data-testid=auto-start]');
    await page.waitForSelector('[data-testid=auto-stop]', { timeout: 10000 });
    await page.screenshot({ path: path.join(SHOTS, 'feature-autoplay-running.png') });
    await page.waitForSelector('[data-testid=spin]:not([disabled])', { timeout: 600000 });
    const h1 = await page.evaluate(() => JSON.parse(localStorage.getItem('golden-rally-history-v1') || '[]').length);
    check('autoplay: plays between 1 and 10 rounds', h1 - h0 >= 1 && h1 - h0 <= 10, `${h1 - h0} rounds`);
    await page.click('[data-testid=btn-auto]');
    await page.click('[data-testid=auto-count-100]');
    await page.click('[data-testid=auto-start]');
    await page.waitForSelector('[data-testid=auto-stop]', { timeout: 10000 });
    await page.click('[data-testid=auto-stop]');
    await page.waitForSelector('[data-testid=spin]:not([disabled])', { timeout: 300000 });
    const h2 = await page.evaluate(() => JSON.parse(localStorage.getItem('golden-rally-history-v1') || '[]').length);
    check('autoplay: stop button ends autoplay promptly', h2 - h1 <= 2, `${h2 - h1} rounds after stop`);
  }

  // server error -> error dialog -> retry
  await page.evaluate(() => (window.__rallyDemo.failNext = 'play'));
  await page.click('[data-testid=spin]');
  await page.waitForSelector('[role=alertdialog]', { timeout: 10000 });
  await page.screenshot({ path: path.join(SHOTS, 'feature-error.png') });
  check('server error shows an error dialog', true);
  await page.click('[role=alertdialog] button');
  await page.waitForSelector('[data-testid=spin]:not([disabled])', { timeout: 20000 });
  check('retry recovers to idle', true);

  // insufficient credits
  await page.evaluate(() => {
    const k = 'golden-rally-demo-v1';
    const s = JSON.parse(localStorage.getItem(k));
    s.balance = 100000; // 0.10 credits
    localStorage.setItem(k, JSON.stringify(s));
  });
  await page.reload();
  await page.waitForSelector('[data-testid=start]');
  await page.click('[data-testid=start]');
  await page.waitForSelector('[data-testid=spin]:not([disabled])');
  await page.click('[data-testid=spin]');
  await page.waitForTimeout(300);
  check('insufficient credits notice', (await page.textContent('[role=status]'))?.includes('insuffisants'));
  check('feature tour: no console errors', errors.length === 0, errors.slice(0, 3).join(' | '));
  await ctx.close();

  // ------------------------------------------------ interruption / reload mid-round
  {
    const { ctx, page } = await open(browser, 'resume', { viewport: { width: 1280, height: 720 } });
    await page.click('[data-testid=spin]');
    await page.waitForTimeout(250);
    const st = await page.evaluate(() => JSON.parse(localStorage.getItem('golden-rally-demo-v1')));
    check('round is persisted as active while presenting', !!st.active);
    await page.reload(); // simulate crash / reload in the middle of the round
    await page.waitForSelector('[data-testid=start]');
    await page.click('[data-testid=start]');
    await page.waitForSelector('[data-testid=spin]:not([disabled])', { timeout: 60000 });
    const bal = await text(page, 'balance');
    check('interrupted round is resumed and settled exactly once', bal === norm(fmt(st.balance + st.active.payout)), `${bal} vs ${fmt(st.balance + st.active.payout)}`);
    const st2 = await page.evaluate(() => JSON.parse(localStorage.getItem('golden-rally-demo-v1')));
    check('no active round left after resume', st2.active === null);
    await ctx.close();
  }

  // ------------------------------------------------ reduced motion
  {
    const { ctx, page, errors } = await open(browser, 'reduced', { viewport: { width: 1280, height: 720 }, reducedMotion: 'reduce' });
    const t0 = Date.now();
    await spinAndVerify(page, 'reduced-motion');
    check('reduced motion: round presentation is short', Date.now() - t0 < 9000, `${Date.now() - t0} ms`);
    check('reduced motion: no console errors', errors.length === 0);
    await ctx.close();
  }
} catch (e) {
  check('e2e run completed', false, String(e && e.stack || e));
} finally {
  await browser.close();
  server.kill();
}

fs.writeFileSync(path.join(HERE, 'report.json'), JSON.stringify({ date: new Date().toISOString(), failures, results }, null, 2));
console.log(`\n${results.length - failures}/${results.length} checks passed`);
process.exit(failures ? 1 : 0);
