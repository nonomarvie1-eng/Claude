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
    const b = document.querySelector('[data-testid=spin]').getBoundingClientRect();
    return { sw: document.documentElement.scrollWidth, iw: innerWidth, ih: innerHeight, spin: { top: b.top, bottom: b.bottom, left: b.left, right: b.right } };
  });
  check(`${name}: no horizontal overflow`, m.sw <= m.iw, `${m.sw} <= ${m.iw}`);
  check(`${name}: spin button fully visible`, m.spin.top >= 0 && m.spin.bottom <= m.ih && m.spin.left >= 0 && m.spin.right <= m.iw);
  const demo = await page.isVisible('[data-testid=demo-badge]');
  check(`${name}: demo badge visible`, demo);
}

await waitServer();
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--autoplay-policy=no-user-gesture-required'] });

const viewports = [
  ['desktop-1920x1080', { viewport: { width: 1920, height: 1080 } }],
  ['laptop-1366x768', { viewport: { width: 1366, height: 768 } }],
  ['iphone-13-portrait', { ...devices['iPhone 13'] }],
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
  check('paytable shows the computed RTP', /96[,.]4[89]/.test(rtpText), rtpText);
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
  check('forced bonus round contains free spins', r.state.some((e) => e.type === 'freeSpinTrigger'));
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

  // bonus buy: debit = bet x 75, bought Tie-Break shown, payout credited
  {
    const before = await page.evaluate(() => JSON.parse(localStorage.getItem('golden-rally-demo-v1')).balance);
    await page.click('[data-testid=btn-buy]');
    await page.waitForSelector('[data-testid=buy-confirm]');
    await page.screenshot({ path: path.join(SHOTS, 'feature-buy-dialog.png') });
    await page.click('[data-testid=buy-confirm]');
    await page.waitForSelector('[data-testid=fs-counter]', { timeout: 30000 });
    await page.waitForTimeout(1500);
    await page.screenshot({ path: path.join(SHOTS, 'feature-buy-bonus.png') });
    await page.waitForSelector('[data-testid=spin]:not([disabled])', { timeout: 300000 });
    const rb = await page.evaluate(() => window.__rally.lastRound);
    const trig = rb.state.find((e) => e.type === 'freeSpinTrigger');
    check('bonus buy: round is a bought Tie-Break of 10 spins', trig && trig.bought === true && trig.totalFs === 10);
    check('bonus buy: cost multiplier 75', rb.cost === 75);
    check('bonus buy: balance = before - 75 x bet + payout', (await text(page, 'balance')) === norm(fmt(before - 75 * rb.amount + rb.payout)), await text(page, 'balance'));
    check('bonus buy: displayed win equals payout', (await text(page, 'win')) === norm(fmt(rb.payout)));
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
