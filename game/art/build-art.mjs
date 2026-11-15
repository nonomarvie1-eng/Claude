// GOLDEN RALLY — procedural art generator (tennis club, original designs;
// no real players, tournaments, trophies or brands are depicted).
// Every visual asset of the game is generated from code in this file
// (no third-party images, no AI image service).  Output: art/svg/*.svg,
// rasterised to public/assets/*.png by art/rasterize.mjs.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(HERE, 'svg');
fs.mkdirSync(OUT, { recursive: true });

const TAU = Math.PI * 2;
const f = (n) => +n.toFixed(2);
const pol = (cx, cy, r, a) => [f(cx + r * Math.cos(a)), f(cy + r * Math.sin(a))];

// ------------------------------------------------------------------ palette
const P = {
  navy0: '#040816',
  navy1: '#0a1430',
  navy2: '#13224d',
  navy3: '#1d3370',
  gold: '#d9a93f',
  goldHi: '#fff1b8',
  copper: '#c8763f',
  ink: '#08102a',
};

const DEFS = `
<defs>
  <linearGradient id="gold" x1="0" y1="0" x2="0.35" y2="1">
    <stop offset="0" stop-color="#fff6c9"/><stop offset="0.18" stop-color="#f4d27a"/>
    <stop offset="0.45" stop-color="#b8842a"/><stop offset="0.62" stop-color="#f1cf72"/>
    <stop offset="0.82" stop-color="#9a6a1c"/><stop offset="1" stop-color="#5c3a0c"/>
  </linearGradient>
  <linearGradient id="goldH" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#7a5212"/><stop offset="0.25" stop-color="#f6d98a"/>
    <stop offset="0.5" stop-color="#b8842a"/><stop offset="0.75" stop-color="#fff0b0"/>
    <stop offset="1" stop-color="#6b4510"/>
  </linearGradient>
  <radialGradient id="goldR" cx="0.38" cy="0.32" r="0.75">
    <stop offset="0" stop-color="#fff7cf"/><stop offset="0.35" stop-color="#ecc463"/>
    <stop offset="0.75" stop-color="#9c6b1d"/><stop offset="1" stop-color="#4f320a"/>
  </radialGradient>
  <linearGradient id="copper" x1="0" y1="0" x2="0.4" y2="1">
    <stop offset="0" stop-color="#ffd9bd"/><stop offset="0.25" stop-color="#e3925a"/>
    <stop offset="0.55" stop-color="#8f4020"/><stop offset="0.75" stop-color="#e8a172"/>
    <stop offset="1" stop-color="#4e1d0a"/>
  </linearGradient>
  <linearGradient id="silver" x1="0" y1="0" x2="0.4" y2="1">
    <stop offset="0" stop-color="#ffffff"/><stop offset="0.3" stop-color="#cfd8e4"/>
    <stop offset="0.55" stop-color="#6f7c8f"/><stop offset="0.78" stop-color="#e9eef5"/>
    <stop offset="1" stop-color="#3a4352"/>
  </linearGradient>
  <linearGradient id="blued" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#8fb6ff"/><stop offset="0.4" stop-color="#2853b8"/>
    <stop offset="1" stop-color="#0b1c55"/>
  </linearGradient>
  <radialGradient id="enamel" cx="0.4" cy="0.35" r="0.8">
    <stop offset="0" stop-color="#fffaf0"/><stop offset="0.7" stop-color="#efe4cc"/>
    <stop offset="1" stop-color="#c9b48a"/>
  </radialGradient>
  <radialGradient id="navyDisc" cx="0.45" cy="0.35" r="0.8">
    <stop offset="0" stop-color="#22397c"/><stop offset="0.6" stop-color="#0f1c45"/>
    <stop offset="1" stop-color="#060b20"/>
  </radialGradient>
  <radialGradient id="ruby" cx="0.38" cy="0.3" r="0.8">
    <stop offset="0" stop-color="#ffc2cc"/><stop offset="0.3" stop-color="#ff3d64"/>
    <stop offset="0.7" stop-color="#a0062c"/><stop offset="1" stop-color="#3d0010"/>
  </radialGradient>
  <radialGradient id="sapphire" cx="0.38" cy="0.3" r="0.8">
    <stop offset="0" stop-color="#d6e6ff"/><stop offset="0.3" stop-color="#4d8cff"/>
    <stop offset="0.7" stop-color="#123a9e"/><stop offset="1" stop-color="#040f3a"/>
  </radialGradient>
  <radialGradient id="glass" cx="0.35" cy="0.3" r="0.9">
    <stop offset="0" stop-color="#e8f3ff" stop-opacity="0.55"/><stop offset="0.6" stop-color="#7fa8e0" stop-opacity="0.18"/>
    <stop offset="1" stop-color="#1b3570" stop-opacity="0.35"/>
  </radialGradient>
  <radialGradient id="halo" cx="0.5" cy="0.5" r="0.5">
    <stop offset="0" stop-color="#ffe9a8" stop-opacity="0.85"/><stop offset="0.45" stop-color="#f0b84a" stop-opacity="0.35"/>
    <stop offset="1" stop-color="#f0b84a" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="haloBlue" cx="0.5" cy="0.5" r="0.5">
    <stop offset="0" stop-color="#bcd4ff" stop-opacity="0.8"/><stop offset="0.5" stop-color="#5a86ff" stop-opacity="0.3"/>
    <stop offset="1" stop-color="#5a86ff" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="greenDisc" cx="0.45" cy="0.35" r="0.8">
    <stop offset="0" stop-color="#2f8a5c"/><stop offset="0.6" stop-color="#14492f"/>
    <stop offset="1" stop-color="#06180f"/>
  </radialGradient>
  <radialGradient id="ballG" cx="0.38" cy="0.32" r="0.8">
    <stop offset="0" stop-color="#f9ffc2"/><stop offset="0.45" stop-color="#dcef4c"/>
    <stop offset="0.85" stop-color="#9fb526"/><stop offset="1" stop-color="#5f6e12"/>
  </radialGradient>
  <linearGradient id="clay" x1="0" y1="0" x2="0.4" y2="1">
    <stop offset="0" stop-color="#f0a274"/><stop offset="0.45" stop-color="#c8643a"/>
    <stop offset="1" stop-color="#6e2a12"/>
  </linearGradient>
  <linearGradient id="ivory" x1="0" y1="0" x2="0.5" y2="1">
    <stop offset="0" stop-color="#ffffff"/><stop offset="0.5" stop-color="#f1e8d2"/>
    <stop offset="1" stop-color="#c2b48e"/>
  </linearGradient>
  <linearGradient id="glassG" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#d8f2e4" stop-opacity="0.35"/><stop offset="0.5" stop-color="#7fc7a0" stop-opacity="0.12"/>
    <stop offset="1" stop-color="#1b5a3e" stop-opacity="0.4"/>
  </linearGradient>
  <radialGradient id="haloGreen" cx="0.5" cy="0.5" r="0.5">
    <stop offset="0" stop-color="#f6ffc0" stop-opacity="0.75"/><stop offset="0.5" stop-color="#9fd16a" stop-opacity="0.25"/>
    <stop offset="1" stop-color="#9fd16a" stop-opacity="0"/>
  </radialGradient>
  <filter id="shadow" x="-30%" y="-30%" width="160%" height="160%">
    <feDropShadow dx="0" dy="5" stdDeviation="5" flood-color="#000" flood-opacity="0.6"/>
  </filter>
  <filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="6"/></filter>
  <filter id="blur2"><feGaussianBlur stdDeviation="2"/></filter>
</defs>`;

const svg = (w, h, body, extraStyle = '') =>
  `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">
<style>
  .cinzel{font-family:'Cinzel',serif;font-weight:700}
  .marcellus{font-family:'Marcellus',serif}
  .poiret{font-family:'Poiret One',sans-serif}
  ${extraStyle}
</style>${DEFS}${body}</svg>`;

// ------------------------------------------------------------------ helpers
function gearPath(cx, cy, rOut, rRoot, teeth, { tip = 0.45, holeR = 0 } = {}) {
  const pts = [];
  const step = TAU / teeth;
  for (let i = 0; i < teeth; i++) {
    const a = i * step;
    const w = (step * tip) / 2;
    pts.push(pol(cx, cy, rRoot, a - step / 2 + 0.02));
    pts.push(pol(cx, cy, rRoot, a - w - 0.05));
    pts.push(pol(cx, cy, rOut, a - w * 0.75));
    pts.push(pol(cx, cy, rOut, a + w * 0.75));
    pts.push(pol(cx, cy, rRoot, a + w + 0.05));
  }
  let d = 'M' + pts.map((p) => p.join(',')).join('L') + 'Z';
  if (holeR) d += circlePath(cx, cy, holeR);
  return d;
}
const circlePath = (cx, cy, r) => `M${f(cx - r)},${cy}a${r},${r} 0 1,0 ${2 * r},0a${r},${r} 0 1,0 ${-2 * r},0Z`;

function spokes(cx, cy, rIn, rOut, n, width, rot = 0) {
  let s = '';
  for (let i = 0; i < n; i++) {
    const a = rot + (i * TAU) / n;
    const [x1, y1] = pol(cx, cy, rIn, a);
    const [x2, y2] = pol(cx, cy, rOut, a);
    s += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke-width="${width}" stroke-linecap="round"/>`;
  }
  return s;
}

function ticks(cx, cy, r1, r2, n, width, color, skipEvery = 0) {
  let s = '';
  for (let i = 0; i < n; i++) {
    if (skipEvery && i % skipEvery === 0) continue;
    const a = (i * TAU) / n - Math.PI / 2;
    const [x1, y1] = pol(cx, cy, r1, a);
    const [x2, y2] = pol(cx, cy, r2, a);
    s += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${color}" stroke-width="${width}" stroke-linecap="round"/>`;
  }
  return s;
}

function spiral(cx, cy, r0, r1, turns, steps = 220) {
  let d = '';
  for (let i = 0; i <= steps; i++) {
    const t = i / steps;
    const a = t * turns * TAU;
    const r = r0 + (r1 - r0) * t;
    const [x, y] = pol(cx, cy, r, a);
    d += (i ? 'L' : 'M') + x + ',' + y;
  }
  return d;
}

function jewel(cx, cy, r) {
  return `<circle cx="${cx}" cy="${cy}" r="${r + 2.2}" fill="url(#gold)"/>
  <circle cx="${cx}" cy="${cy}" r="${r}" fill="url(#ruby)"/>
  <circle cx="${f(cx - r * 0.35)}" cy="${f(cy - r * 0.35)}" r="${f(r * 0.28)}" fill="#fff" opacity="0.8"/>`;
}

// art-deco medallion used behind high symbols
function medallion(cx, cy, r, accent = 'url(#gold)') {
  let rays = '';
  for (let i = 0; i < 24; i++) {
    const a = (i * TAU) / 24;
    const [x1, y1] = pol(cx, cy, r * 0.55, a);
    const [x2, y2] = pol(cx, cy, r * 0.93, a);
    rays += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#d9a93f" stroke-opacity="${i % 2 ? 0.12 : 0.22}" stroke-width="${i % 2 ? 1.2 : 2.4}"/>`;
  }
  return `<g filter="url(#shadow)">
    <circle cx="${cx}" cy="${cy}" r="${r}" fill="${accent}"/>
    <circle cx="${cx}" cy="${cy}" r="${r - 5}" fill="#2a1c06"/>
    <circle cx="${cx}" cy="${cy}" r="${r - 7}" fill="url(#navyDisc)"/>
  </g>
  ${rays}
  <circle cx="${cx}" cy="${cy}" r="${r - 14}" fill="none" stroke="#d9a93f" stroke-opacity="0.45" stroke-width="1.5" stroke-dasharray="2 5"/>`;
}

// ------------------------------------------------------------------ symbols (256x256)
const S = 256;
const C = 128;

// tennis ball with its classic seam, drawn generically
function ball(cx, cy, r, fill = 'url(#ballG)', seam = '#f8f6ea', sw = 0) {
  const k = r * 0.62;
  return `<circle cx="${cx}" cy="${cy}" r="${r}" fill="${fill}"/>
  <path d="M${f(cx - r * 0.95)},${f(cy - r * 0.3)} C${f(cx - k * 0.3)},${f(cy - r * 0.2)} ${f(cx - k * 0.3)},${f(cy + r * 0.85)} ${f(cx - r * 0.45)},${f(cy + r * 0.9)}" fill="none" stroke="${seam}" stroke-width="${sw || f(r * 0.1)}" stroke-linecap="round"/>
  <path d="M${f(cx + r * 0.45)},${f(cy - r * 0.9)} C${f(cx + k * 0.3)},${f(cy - r * 0.85)} ${f(cx + k * 0.3)},${f(cy + r * 0.2)} ${f(cx + r * 0.95)},${f(cy + r * 0.3)}" fill="none" stroke="${seam}" stroke-width="${sw || f(r * 0.1)}" stroke-linecap="round"/>
  <ellipse cx="${f(cx - r * 0.35)}" cy="${f(cy - r * 0.42)}" rx="${f(r * 0.32)}" ry="${f(r * 0.18)}" fill="#fff" opacity="0.45" transform="rotate(-30 ${f(cx - r * 0.35)} ${f(cy - r * 0.42)})"/>`;
}

function laurel(cx, cy, r, color = 'url(#gold)') {
  let s = '';
  for (const side of [-1, 1]) {
    for (let i = 0; i < 9; i++) {
      const a = Math.PI / 2 + side * (0.35 + i * 0.27);
      const [x, y] = pol(cx, cy, r, a);
      const rot = (a * 180) / Math.PI + (side > 0 ? -60 : 60);
      s += `<ellipse cx="${x}" cy="${y}" rx="${f(r * 0.17)}" ry="${f(r * 0.07)}" fill="${color}" transform="rotate(${f(rot)} ${x} ${y})"/>`;
    }
  }
  return s;
}

function banner(cx, y, text, size = 23) {
  return `<g filter="url(#shadow)">
    <path d="M${cx - 88},${y} L${cx - 72},${y - 14} H${cx + 72} L${cx + 88},${y} L${cx + 72},${y + 14} H${cx - 72} Z" fill="url(#gold)"/>
    <path d="M${cx - 80},${y} L${cx - 68},${y - 10} H${cx + 68} L${cx + 80},${y} L${cx + 68},${y + 10} H${cx - 68} Z" fill="#0b2a1e"/>
  </g>
  <text x="${cx}" y="${y + 8}" text-anchor="middle" class="cinzel" font-size="${size}" letter-spacing="6" fill="url(#gold)">${text}</text>`;
}

function symWild() {
  const cx = C;
  // racket head
  let strings = '';
  for (let i = -5; i <= 5; i++) strings += `<line x1="${cx + i * 9}" y1="12" x2="${cx + i * 9}" y2="150" stroke="#f5eedc" stroke-width="1.6" opacity="0.9"/>`;
  for (let j = 0; j < 14; j++) strings += `<line x1="${cx - 60}" y1="${24 + j * 9}" x2="${cx + 60}" y2="${24 + j * 9}" stroke="#f5eedc" stroke-width="1.6" opacity="0.9"/>`;
  return svg(S, S, `
  <circle cx="${cx}" cy="100" r="110" fill="url(#halo)"/>
  <clipPath id="head"><ellipse cx="${cx}" cy="80" rx="46" ry="58"/></clipPath>
  <g filter="url(#shadow)" transform="rotate(-18 ${cx} 120)">
    <ellipse cx="${cx}" cy="80" rx="56" ry="68" fill="url(#gold)"/>
    <ellipse cx="${cx}" cy="80" rx="47" ry="59" fill="#0b2a1e"/>
    <g clip-path="url(#head)">${strings}</g>
    <path d="M${cx - 30},140 Q${cx},150 ${cx - 7},170 L${cx + 7},170 Q${cx},150 ${cx + 30},140 L${cx + 20},136 Q${cx},146 ${cx},160 Q${cx},146 ${cx - 20},136 Z" fill="url(#gold)"/>
    <rect x="${cx - 9}" y="168" width="18" height="56" rx="4" fill="url(#ivory)"/>
    ${[0, 1, 2, 3, 4, 5].map((i) => `<line x1="${cx - 9}" y1="${172 + i * 9}" x2="${cx + 9}" y2="${178 + i * 9}" stroke="#a89a78" stroke-width="2"/>`).join('')}
    <rect x="${cx - 11}" y="220" width="22" height="8" rx="3" fill="url(#gold)"/>
  </g>
  ${banner(cx, 214, 'WILD')}
  <path d="M${cx - 50},40 A60,70 0 0,1 ${cx - 10},14" fill="none" stroke="#fff" stroke-opacity="0.6" stroke-width="3" stroke-linecap="round"/>
  `);
}

function symScatter() {
  const cx = C;
  let rays = '';
  for (let i = 0; i < 16; i++) {
    const a = (i * TAU) / 16;
    const [x1, y1] = pol(cx, 100, 70, a - 0.07);
    const [x2, y2] = pol(cx, 100, i % 2 ? 104 : 120, a);
    const [x3, y3] = pol(cx, 100, 70, a + 0.07);
    rays += `<path d="M${x1},${y1} L${x2},${y2} L${x3},${y3} Z" fill="url(#gold)" opacity="0.55"/>`;
  }
  return svg(S, S, `
  <circle cx="${cx}" cy="104" r="124" fill="url(#haloGreen)"/>
  ${rays}
  <g filter="url(#shadow)">
    <path d="M${cx - 50},44 C${cx - 82},44 ${cx - 84},96 ${cx - 40},110" fill="none" stroke="url(#gold)" stroke-width="9" stroke-linecap="round"/>
    <path d="M${cx + 50},44 C${cx + 82},44 ${cx + 84},96 ${cx + 40},110" fill="none" stroke="url(#gold)" stroke-width="9" stroke-linecap="round"/>
    <path d="M${cx - 56},34 H${cx + 56} C${cx + 56},96 ${cx + 34},126 ${cx},132 C${cx - 34},126 ${cx - 56},96 ${cx - 56},34 Z" fill="url(#gold)"/>
    <ellipse cx="${cx}" cy="34" rx="56" ry="9" fill="url(#goldR)"/>
    <ellipse cx="${cx}" cy="34" rx="48" ry="5" fill="#5c3a0c" opacity="0.6"/>
    <rect x="${cx - 7}" y="130" width="14" height="22" fill="url(#goldH)"/>
    <ellipse cx="${cx}" cy="154" rx="26" ry="7" fill="url(#gold)"/>
    <path d="M${cx - 36},162 H${cx + 36} L${cx + 42},186 H${cx - 42} Z" fill="#0b2a1e" stroke="url(#gold)" stroke-width="3"/>
  </g>
  ${ball(cx, 82, 17, 'url(#ballG)')}
  <path d="M${cx - 40},46 C${cx - 40},80 ${cx - 30},104 ${cx - 14},116" fill="none" stroke="#fff" stroke-opacity="0.55" stroke-width="4" stroke-linecap="round"/>
  ${banner(cx, 214, 'BONUS', 21)}
  `);
}

function symGoldBall() {
  const cx = C, cy = 124;
  return svg(S, S, `
  <circle cx="${cx}" cy="${cy}" r="112" fill="url(#halo)" opacity="0.7"/>
  ${laurel(cx, cy, 96)}
  <g filter="url(#shadow)">${ball(cx, cy, 66, 'url(#goldR)', '#fff5d0')}</g>
  ${jewel(cx, cy + 104, 6)}
  `);
}

function medallionG(cx, cy, r) {
  let rays = '';
  for (let i = 0; i < 24; i++) {
    const a = (i * TAU) / 24;
    const [x1, y1] = pol(cx, cy, r * 0.55, a);
    const [x2, y2] = pol(cx, cy, r * 0.93, a);
    rays += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#e6d6a8" stroke-opacity="${i % 2 ? 0.08 : 0.16}" stroke-width="${i % 2 ? 1.2 : 2.4}"/>`;
  }
  return `<g filter="url(#shadow)">
    <circle cx="${cx}" cy="${cy}" r="${r}" fill="url(#gold)"/>
    <circle cx="${cx}" cy="${cy}" r="${r - 5}" fill="#1a1204"/>
    <circle cx="${cx}" cy="${cy}" r="${r - 7}" fill="url(#greenDisc)"/>
  </g>${rays}
  <circle cx="${cx}" cy="${cy}" r="${r - 14}" fill="none" stroke="#f5eedc" stroke-opacity="0.35" stroke-width="1.5"/>`;
}

function symUmpireChair() {
  const cx = C;
  return svg(S, S, `
  ${medallionG(cx, C, 114)}
  <g filter="url(#shadow)" stroke-linecap="round">
    <path d="M${cx - 40},228 L${cx - 22},104 M${cx + 40},228 L${cx + 22},104" stroke="url(#ivory)" stroke-width="9"/>
    ${[0, 1, 2, 3].map((i) => `<line x1="${cx - 36 + i * 2.6}" y1="${206 - i * 26}" x2="${cx + 36 - i * 2.6}" y2="${206 - i * 26}" stroke="#efe6cf" stroke-width="7"/>`).join('')}
    <rect x="${cx - 36}" y="92" width="72" height="12" rx="3" fill="url(#gold)"/>
    <path d="M${cx - 30},92 V54 H${cx + 30} V92" fill="none" stroke="url(#ivory)" stroke-width="8"/>
    <rect x="${cx - 30}" y="54" width="60" height="22" fill="#1f6b47" stroke="url(#gold)" stroke-width="2"/>
    <path d="M${cx - 36},88 H${cx - 52} V70 M${cx + 36},88 H${cx + 52} V70" fill="none" stroke="url(#ivory)" stroke-width="6"/>
    <path d="M${cx - 62},40 Q${cx},4 ${cx + 62},40 Z" fill="url(#clay)"/>
    <path d="M${cx - 62},40 Q${cx - 31},30 ${cx},40 Q${cx + 31},30 ${cx + 62},40" fill="none" stroke="#f5eedc" stroke-width="3"/>
    <line x1="${cx}" y1="20" x2="${cx}" y2="56" stroke="url(#gold)" stroke-width="4"/>
  </g>
  `);
}

function symBallTube() {
  const cx = C;
  return svg(S, S, `
  ${medallionG(cx, C, 114)}
  <g filter="url(#shadow)">
    <rect x="${cx - 42}" y="44" width="84" height="176" rx="12" fill="url(#glassG)" stroke="#f5eedc" stroke-opacity="0.7" stroke-width="2.5"/>
    ${ball(cx, 92, 34)}${ball(cx, 152, 34)}
    <rect x="${cx - 42}" y="178" width="84" height="40" rx="6" fill="url(#ivory)"/>
    <text x="${cx}" y="206" text-anchor="middle" class="cinzel" font-size="18" letter-spacing="3" fill="#0b2a1e">CLUB</text>
    <rect x="${cx - 48}" y="28" width="96" height="22" rx="8" fill="url(#gold)"/>
    <rect x="${cx - 48}" y="214" width="96" height="16" rx="6" fill="url(#gold)"/>
    <rect x="${cx - 32}" y="52" width="10" height="120" rx="5" fill="#fff" opacity="0.28"/>
  </g>
  `);
}

function symCap() {
  const cx = C;
  return svg(S, S, `
  ${medallionG(cx, C, 114)}
  <g filter="url(#shadow)">
    <path d="M${cx - 74},150 C${cx - 74},70 ${cx - 30},54 ${cx + 6},54 C${cx + 50},54 ${cx + 76},86 ${cx + 76},150 Z" fill="url(#ivory)"/>
    <path d="M${cx - 74},150 H${cx + 76} L${cx + 76},160 H${cx - 74} Z" fill="#1f6b47"/>
    <path d="M${cx + 6},54 C${cx - 10},80 ${cx - 14},120 ${cx - 12},150" fill="none" stroke="#c9bc98" stroke-width="2"/>
    <path d="M${cx + 6},54 C${cx + 28},80 ${cx + 34},120 ${cx + 34},150" fill="none" stroke="#c9bc98" stroke-width="2"/>
    <path d="M${cx + 70},150 C${cx + 104},150 ${cx + 118},166 ${cx + 112},176 C${cx + 80},176 ${cx + 40},168 ${cx + 20},160 Z" fill="#1f6b47" stroke="url(#gold)" stroke-width="2"/>
    <circle cx="${cx + 6}" cy="56" r="7" fill="url(#gold)"/>
    <circle cx="${cx - 34}" cy="110" r="20" fill="#0b2a1e" stroke="url(#gold)" stroke-width="3"/>
    <path d="M${cx - 44},120 L${cx - 24},100 M${cx - 24},120 L${cx - 44},100" stroke="url(#gold)" stroke-width="3.5" stroke-linecap="round"/>
    <circle cx="${cx - 34}" cy="104" r="4" fill="url(#ballG)"/>
  </g>
  <path d="M${cx - 60},116 C${cx - 56},86 ${cx - 36},70 ${cx - 14},64" fill="none" stroke="#fff" stroke-opacity="0.7" stroke-width="4" stroke-linecap="round"/>
  `);
}

// low symbols: tennis score medallions
function scoreBadge(label, fill, textFill, size) {
  const cx = C, cy = C, R = 96;
  const oct = (r) => Array.from({ length: 8 }, (_, i) => pol(cx, cy, r, (i * TAU) / 8 + TAU / 16).join(',')).join(' ');
  return svg(S, S, `
  <g filter="url(#shadow)">
    <polygon points="${oct(R)}" fill="url(#gold)"/>
    <polygon points="${oct(R - 7)}" fill="#1a1204"/>
    <polygon points="${oct(R - 9)}" fill="${fill}"/>
  </g>
  <polygon points="${oct(R - 18)}" fill="none" stroke="url(#gold)" stroke-width="2" opacity="0.8"/>
  <path d="M${cx - 60},${cy - 44} A80,80 0 0,1 ${cx + 10},${cy - 78}" fill="none" stroke="#fff" stroke-opacity="0.3" stroke-width="6" stroke-linecap="round"/>
  <text x="${cx}" y="${cy + size * 0.36}" text-anchor="middle" class="cinzel" font-size="${size}" fill="${textFill}" stroke="#1a1204" stroke-width="2" letter-spacing="2">${label}</text>
  `);
}

function mulberry(a) {
  return () => {
    a |= 0; a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// ------------------------------------------------------------------ decor
function decoBall(r, alpha = 1) {
  const size = Math.ceil(r * 2 + 8);
  const c = size / 2;
  return svg(size, size, `<g opacity="${alpha}">${ball(c, c, r, 'url(#ballG)')}</g>`);
}

function decoRacket() {
  const w = 300, h = 640, cx = 150;
  let strings = '';
  for (let i = -8; i <= 8; i++) strings += `<line x1="${cx + i * 13}" y1="20" x2="${cx + i * 13}" y2="400" stroke="#f5eedc" stroke-width="2.4"/>`;
  for (let j = 0; j < 30; j++) strings += `<line x1="${cx - 130}" y1="${30 + j * 13}" x2="${cx + 130}" y2="${30 + j * 13}" stroke="#f5eedc" stroke-width="2.4"/>`;
  return svg(w, h, `
    <clipPath id="rh"><ellipse cx="${cx}" cy="200" rx="112" ry="160"/></clipPath>
    <ellipse cx="${cx}" cy="200" rx="128" ry="178" fill="none" stroke="url(#gold)" stroke-width="22"/>
    <g clip-path="url(#rh)">${strings}</g>
    <path d="M${cx - 60},360 Q${cx},400 ${cx - 14},450 L${cx + 14},450 Q${cx},400 ${cx + 60},360" fill="none" stroke="url(#gold)" stroke-width="16"/>
    <rect x="${cx - 18}" y="446" width="36" height="180" rx="8" fill="url(#ivory)"/>`);
}

function background(w, h) {
  const cx = w / 2;
  // mown-grass stripes
  let stripes = '';
  const n = 14;
  for (let i = 0; i < n; i++) {
    if (i % 2) stripes += `<rect x="${(i * w) / n}" y="0" width="${w / n}" height="${h}" fill="#ffffff" opacity="0.025"/>`;
  }
  // perspective court lines (generic court geometry)
  const top = h * 0.30, bot = h * 1.05;
  const tw = w * 0.36, bw = w * 1.25;
  const L = (x1, y1, x2, y2, o = 0.16, sw = 3) => `<line x1="${f(x1)}" y1="${f(y1)}" x2="${f(x2)}" y2="${f(y2)}" stroke="#f5eedc" stroke-opacity="${o}" stroke-width="${sw}"/>`;
  const at = (u, v) => { // u in [-1,1] across, v in [0,1] depth (0 far)
    const y = top + (bot - top) * v;
    const half = (tw + (bw - tw) * v) / 2;
    return [cx + u * half, y];
  };
  let court = '';
  for (const u of [-1, -0.78, 0.78, 1]) court += L(...at(u, 0), ...at(u, 1));
  for (const v of [0, 0.32, 1]) court += L(...at(-1, v), ...at(1, v));
  court += L(...at(0, 0.32), ...at(0, 1));
  court += L(...at(-0.78, 0.62), ...at(0.78, 0.62));
  // net band
  const [nx1, ny] = at(-1.08, 0.12);
  const [nx2] = at(1.08, 0.12);
  court += `<rect x="${f(nx1)}" y="${f(ny - 24)}" width="${f(nx2 - nx1)}" height="24" fill="#071a12" opacity="0.5"/>`;
  court += L(nx1, ny - 24, nx2, ny - 24, 0.35, 5);
  let rays = '';
  for (let i = 0; i < 48; i++) {
    const a = Math.PI + (i * Math.PI) / 47;
    const [x2, y2] = pol(cx, h * 0.3, Math.max(w, h), a);
    rays += `<line x1="${cx}" y1="${h * 0.3}" x2="${x2}" y2="${y2}" stroke="#e6d6a8" stroke-opacity="${i % 2 ? 0.02 : 0.045}" stroke-width="${i % 2 ? 2 : 6}"/>`;
  }
  const defs = `<radialGradient id="vig" cx="0.5" cy="0.45" r="0.75">
      <stop offset="0" stop-color="#000" stop-opacity="0"/><stop offset="0.65" stop-color="#000" stop-opacity="0.25"/>
      <stop offset="1" stop-color="#000" stop-opacity="0.82"/></radialGradient>
    <linearGradient id="bgG" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#06150f"/><stop offset="0.35" stop-color="#0f3b2a"/><stop offset="1" stop-color="#1b5a3e"/></linearGradient>`;
  return svg(w, h, `<defs>${defs}</defs>
    <rect width="${w}" height="${h}" fill="url(#bgG)"/>
    ${stripes}${rays}${court}
    <rect x="18" y="18" width="${w - 36}" height="${h - 36}" fill="none" stroke="#e3b552" stroke-opacity="0.22" stroke-width="2"/>
    <rect x="28" y="28" width="${w - 56}" height="${h - 56}" fill="none" stroke="#f5eedc" stroke-opacity="0.10" stroke-width="1"/>
    <rect width="${w}" height="${h}" fill="url(#vig)"/>`);
}

export const CELL = 200;
function reelFrame() {
  const iw = 5 * CELL, ih = 3 * CELL, m = 46;
  const w = iw + 2 * m, h = ih + 2 * m;
  const step = 18;
  const outline = (o) => `M${o + step},${o} H${w - o - step} L${w - o},${o + step} V${h - o - step} L${w - o - step},${h - o} H${o + step} L${o},${h - o - step} V${o + step} Z`;
  let seps = '';
  for (let i = 1; i < 5; i++) {
    const x = m + i * CELL;
    seps += `<line x1="${x}" y1="${m + 8}" x2="${x}" y2="${m + ih - 8}" stroke="#f5eedc" stroke-opacity="0.18" stroke-width="2"/>`;
  }
  let studs = '';
  for (const [x, y] of [[m / 2, m / 2], [w - m / 2, m / 2], [m / 2, h - m / 2], [w - m / 2, h - m / 2]]) {
    studs += `<circle cx="${x}" cy="${y}" r="12" fill="url(#gold)"/><circle cx="${x}" cy="${y}" r="6" fill="url(#ballG)"/>`;
  }
  return svg(w, h, `
    <path d="${outline(0)}" fill="url(#gold)"/>
    <path d="${outline(6)}" fill="#1a1204"/>
    <path d="${outline(9)}" fill="url(#ivory)"/>
    <path d="${outline(16)}" fill="#0b2a1e"/>
    <path d="${outline(26)}" fill="none" stroke="url(#gold)" stroke-width="3"/>
    <path d="M${m},${m} H${m + iw} V${m + ih} H${m} Z" fill="#06180f" fill-opacity="0.86"/>
    <path d="M${m},${m} H${m + iw} V${m + ih} H${m} Z" fill="none" stroke="url(#goldH)" stroke-width="4"/>
    ${seps}${studs}`);
}

function logo() {
  const w = 900, h = 260;
  const cx = w / 2;
  return svg(w, h, `
    <g filter="url(#shadow)">
      <g transform="translate(${cx} 48)">
        <g transform="rotate(-35)"><ellipse cx="0" cy="-12" rx="14" ry="19" fill="none" stroke="url(#gold)" stroke-width="5"/><rect x="-3" y="6" width="6" height="30" fill="url(#gold)"/></g>
        <g transform="rotate(35)"><ellipse cx="0" cy="-12" rx="14" ry="19" fill="none" stroke="url(#gold)" stroke-width="5"/><rect x="-3" y="6" width="6" height="30" fill="url(#gold)"/></g>
        ${ball(0, -30, 10)}
      </g>
      <text x="${cx}" y="168" text-anchor="middle" class="cinzel" font-size="96" letter-spacing="12" fill="url(#gold)" stroke="#3b2708" stroke-width="1.5">GOLDEN</text>
      <line x1="${cx - 330}" y1="198" x2="${cx - 140}" y2="198" stroke="url(#goldH)" stroke-width="2.5"/>
      <line x1="${cx + 140}" y1="198" x2="${cx + 330}" y2="198" stroke="url(#goldH)" stroke-width="2.5"/>
      <circle cx="${cx - 140}" cy="198" r="6" fill="url(#ballG)"/><circle cx="${cx + 140}" cy="198" r="6" fill="url(#ballG)"/>
      <text x="${cx}" y="214" text-anchor="middle" class="poiret" font-size="46" letter-spacing="26" fill="#f5eedc">RALLY</text>
    </g>`);
}

function rallyDial() {
  const s = 300, c = 150;
  const ladder = [1, 2, 3, 4, 5, 6, 8, 10];
  const a0 = Math.PI * 0.8, a1 = Math.PI * 2.2;
  let labels = '';
  ladder.forEach((m, i) => {
    const a = a0 + ((a1 - a0) * i) / (ladder.length - 1);
    const [x, y] = pol(c, c, 100, a);
    const [t1x, t1y] = pol(c, c, 118, a);
    const [t2x, t2y] = pol(c, c, 132, a);
    labels += `<line x1="${t1x}" y1="${t1y}" x2="${t2x}" y2="${t2y}" stroke="url(#gold)" stroke-width="4" stroke-linecap="round"/>`;
    labels += `<text x="${x}" y="${f(y + 9)}" text-anchor="middle" class="cinzel" font-size="${i === 7 ? 26 : 22}" fill="${i === 7 ? '#ffe7a0' : '#f5eedc'}">×${m}</text>`;
  });
  let minor = '';
  for (let i = 0; i <= 28; i++) {
    const a = a0 + ((a1 - a0) * i) / 28;
    const [x1, y1] = pol(c, c, 122, a);
    const [x2, y2] = pol(c, c, 128, a);
    minor += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#e3b552" stroke-opacity="0.6" stroke-width="1.5"/>`;
  }
  return svg(s, s, `
    <g filter="url(#shadow)">
      <circle cx="${c}" cy="${c}" r="146" fill="url(#gold)"/>
      <circle cx="${c}" cy="${c}" r="138" fill="#1a1204"/>
      <circle cx="${c}" cy="${c}" r="136" fill="url(#greenDisc)"/>
    </g>
    ${minor}${labels}
    <text x="${c}" y="${c + 112}" text-anchor="middle" class="poiret" font-size="16" letter-spacing="6" fill="#f5eedc" fill-opacity="0.85">RALLY</text>
  `);
}

function dialHand() {
  return svg(40, 150, `
    <path d="M20,4 L27,112 L20,124 L13,112 Z" fill="url(#ivory)" stroke="#5c3a0c" stroke-width="1"/>
    <circle cx="20" cy="124" r="14" fill="url(#gold)"/><circle cx="20" cy="124" r="6" fill="url(#ballG)"/>`);
}

function sparkle() {
  return svg(64, 64, `
    <circle cx="32" cy="32" r="30" fill="url(#halo)"/>
    <path d="M32,2 L36,28 L62,32 L36,36 L32,62 L28,36 L2,32 L28,28 Z" fill="#fff8d8"/>`);
}

function glowDot() {
  return svg(64, 64, `<circle cx="32" cy="32" r="32" fill="url(#halo)"/>`);
}

function coinBall() {
  return svg(96, 96, `<g filter="url(#shadow)">${ball(48, 48, 40)}</g>`);
}

const assets = {
  'sym_W': symWild(),
  'sym_S': symScatter(),
  'sym_H1': symGoldBall(),
  'sym_H2': symUmpireChair(),
  'sym_H3': symBallTube(),
  'sym_H4': symCap(),
  'sym_L1': scoreBadge('AD', 'url(#clay)', '#fff1d6', 74),
  'sym_L2': scoreBadge('40', 'url(#greenDisc)', 'url(#gold)', 92),
  'sym_L3': scoreBadge('30', 'url(#ivory)', '#1f6b47', 92),
  'sym_L4': scoreBadge('15', 'url(#navyDisc)', '#f5eedc', 92),
  'bg_landscape': background(1920, 1080),
  'bg_portrait': background(1080, 1920),
  'frame': reelFrame(),
  'logo': logo(),
  'dial': rallyDial(),
  'dial_hand': dialHand(),
  'deco_1': decoBall(150, 1),
  'deco_2': decoRacket(),
  'deco_3': decoBall(70, 1),
  'sparkle': sparkle(),
  'glow': glowDot(),
  'coin': coinBall(),
};

fs.rmSync(OUT, { recursive: true, force: true });
fs.mkdirSync(OUT, { recursive: true });
for (const [name, content] of Object.entries(assets)) {
  fs.writeFileSync(path.join(OUT, name + '.svg'), content);
}
console.log(`wrote ${Object.keys(assets).length} SVG files to ${OUT}`);
