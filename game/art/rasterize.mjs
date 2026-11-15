// Rasterise art/svg/*.svg into public/assets/*.png with headless Chromium
// (Playwright, pre-installed).  Fonts (SIL OFL, from @fontsource) are embedded
// as data URLs so the text in SVG renders with the real typefaces.
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';

const require = createRequire(import.meta.url);
const { chromium } = require('playwright');

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.dirname(HERE);
const SRC = path.join(HERE, 'svg');
const OUT = path.join(ROOT, 'src', 'assets', 'img');
fs.mkdirSync(OUT, { recursive: true });

const font = (pkg, file) => {
  const p = path.join(ROOT, 'node_modules', '@fontsource', pkg, 'files', file);
  return `data:font/woff2;base64,${fs.readFileSync(p).toString('base64')}`;
};
const FONT_CSS = `
@font-face{font-family:'Cinzel';font-weight:700;src:url(${font('cinzel', 'cinzel-latin-700-normal.woff2')}) format('woff2')}
@font-face{font-family:'Poiret One';font-weight:400;src:url(${font('poiret-one', 'poiret-one-latin-400-normal.woff2')}) format('woff2')}
@font-face{font-family:'Marcellus';font-weight:400;src:url(${font('marcellus', 'marcellus-latin-400-normal.woff2')}) format('woff2')}
@font-face{font-family:'Luckiest Guy';font-weight:400;src:url(${font('luckiest-guy', 'luckiest-guy-latin-400-normal.woff2')}) format('woff2')}
@font-face{font-family:'Lilita One';font-weight:400;src:url(${font('lilita-one', 'lilita-one-latin-400-normal.woff2')}) format('woff2')}
@font-face{font-family:'Bangers';font-weight:400;src:url(${font('bangers', 'bangers-latin-400-normal.woff2')}) format('woff2')}
html,body{margin:0;background:transparent}`;

// scale per asset (symbols are authored at 256 and exported at 2x)
const SCALE = { default: 2, bg_landscape: 1, bg_portrait: 1, frame: 1.5 };

const browser = await chromium.launch();
const page = await browser.newPage();
const files = fs.readdirSync(SRC).filter((f) => f.endsWith('.svg'));
for (const file of files) {
  const name = file.replace('.svg', '');
  const svg = fs.readFileSync(path.join(SRC, file), 'utf8');
  const w = +svg.match(/width="(\d+)"/)[1];
  const h = +svg.match(/height="(\d+)"/)[1];
  const s = SCALE[name] ?? SCALE.default;
  await page.setViewportSize({ width: Math.ceil(w * s), height: Math.ceil(h * s) });
  await page.setContent(`<html><head><style>${FONT_CSS}</style></head><body>
    <div style="width:${w * s}px;height:${h * s}px">${svg.replace('<svg ', `<svg style="width:${w * s}px;height:${h * s}px;display:block" `)}</div></body></html>`);
  await page.evaluate(() => document.fonts.ready);
  const out = path.join(OUT, name + (name.startsWith('bg_') ? '.jpg' : '.png'));
  await page.screenshot({
    path: out,
    omitBackground: !name.startsWith('bg_'),
    type: name.startsWith('bg_') ? 'jpeg' : 'png',
    quality: name.startsWith('bg_') ? 86 : undefined,
    clip: { x: 0, y: 0, width: Math.ceil(w * s), height: Math.ceil(h * s) },
  });
  console.log('✓', path.relative(ROOT, out));
}
// contact sheet for review
const syms = ['W', 'S', 'H1', 'H2', 'H3', 'H4', 'H5', 'L1', 'L2', 'L3', 'L4', 'L5'];
await page.setViewportSize({ width: 1580, height: 540 });
await page.setContent(`<html><body style="margin:0;background:#2b6b45;display:flex;flex-wrap:wrap;gap:10px;padding:10px">
${syms.map((s) => `<img src="data:image/png;base64,${fs.readFileSync(path.join(OUT, `sym_${s}.png`)).toString('base64')}" style="width:250px;height:250px;background:#1f5e3a;border:1px solid #0b2a1e">`).join('')}
</body></html>`);
await page.screenshot({ path: path.join(HERE, 'contact-sheet.png') });
await browser.close();
