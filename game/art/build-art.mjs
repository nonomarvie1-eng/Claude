// GOLDEN RALLY — MATCH POINT · procedural art generator ("fun premium").
// Night tournament of the fictional Golden Rally Club: deep court green, polished
// gold, tennis-ball yellow, off-white, orange accents.  Gradients, bevels,
// reflections and glows on every asset.  All artwork is drawn by this code:
// no third-party image, no AI image service, no real person/tournament/brand.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(HERE, 'svg');
const CFG = JSON.parse(fs.readFileSync(path.join(HERE, '..', '..', 'shared', 'game-config.json'), 'utf8'));
const TAU = Math.PI * 2;
const f = (n) => +(+n).toFixed(2);
const pol = (cx, cy, r, a) => [f(cx + r * Math.cos(a)), f(cy + r * Math.sin(a))];

const INK = '#16120f';
const ink = (w = 5) => `stroke="${INK}" stroke-width="${w}" stroke-linejoin="round" stroke-linecap="round"`;

const DEFS = `
<defs>
  <linearGradient id="gold" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fbf0cf"/><stop offset=".25" stop-color="#e8c47a"/><stop offset=".5" stop-color="#b8862f"/>
    <stop offset=".66" stop-color="#ecd096"/><stop offset=".85" stop-color="#a0701f"/><stop offset="1" stop-color="#6b4612"/></linearGradient>
  <linearGradient id="goldH" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#8a560a"/><stop offset=".25" stop-color="#ffe9a0"/><stop offset=".5" stop-color="#d99a1e"/><stop offset=".75" stop-color="#fff3c4"/><stop offset="1" stop-color="#8a560a"/></linearGradient>
  <radialGradient id="goldR" cx=".35" cy=".3" r=".8"><stop offset="0" stop-color="#fffbe0"/><stop offset=".35" stop-color="#ffd75e"/><stop offset=".75" stop-color="#c58512"/><stop offset="1" stop-color="#6e4205"/></radialGradient>
  <linearGradient id="silver" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset=".3" stop-color="#d7dee8"/><stop offset=".55" stop-color="#8a96a8"/><stop offset=".75" stop-color="#eef2f7"/><stop offset="1" stop-color="#5a6474"/></linearGradient>
  <linearGradient id="bronze" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffe2c4"/><stop offset=".35" stop-color="#d98a4e"/><stop offset=".6" stop-color="#ffc79a"/><stop offset="1" stop-color="#7a3d14"/></linearGradient>
  <radialGradient id="ballG" cx=".36" cy=".3" r=".85"><stop offset="0" stop-color="#fbffc9"/><stop offset=".5" stop-color="#e2f23c"/><stop offset="1" stop-color="#8fa313"/></radialGradient>
  <radialGradient id="skinL" cx=".38" cy=".3" r=".85"><stop offset="0" stop-color="#ffe6cc"/><stop offset=".6" stop-color="#f6c49a"/><stop offset="1" stop-color="#d9946a"/></radialGradient>
  <radialGradient id="skinM" cx=".38" cy=".3" r=".85"><stop offset="0" stop-color="#f6c9a0"/><stop offset=".6" stop-color="#df9e70"/><stop offset="1" stop-color="#b3704a"/></radialGradient>
  <radialGradient id="skinB" cx=".38" cy=".3" r=".85"><stop offset="0" stop-color="#d79a6e"/><stop offset=".6" stop-color="#a86a42"/><stop offset="1" stop-color="#6e3f22"/></radialGradient>
  <radialGradient id="fur" cx=".4" cy=".3" r=".85"><stop offset="0" stop-color="#f6d3a2"/><stop offset=".6" stop-color="#d9a066"/><stop offset="1" stop-color="#9c6532"/></radialGradient>
  <linearGradient id="white" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#d9dee6"/></linearGradient>
  <linearGradient id="green" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2f9a5e"/><stop offset="1" stop-color="#0f4a2c"/></linearGradient>
  <linearGradient id="navy" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2d4a8f"/><stop offset="1" stop-color="#121f45"/></linearGradient>
  <linearGradient id="burgundy" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#a8324a"/><stop offset="1" stop-color="#4f0e1c"/></linearGradient>
  <linearGradient id="red" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ff6a5a"/><stop offset="1" stop-color="#b8231c"/></linearGradient>
  <linearGradient id="hairD" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5a3a26"/><stop offset="1" stop-color="#1e120b"/></linearGradient>
  <linearGradient id="flame" x1="1" y1="0" x2="0" y2="0"><stop offset="0" stop-color="#fff7c0" stop-opacity="0"/><stop offset=".25" stop-color="#ffd23f"/><stop offset=".6" stop-color="#ff8a1e"/><stop offset="1" stop-color="#e8381e" stop-opacity="0"/></linearGradient>
  <pattern id="grain" width="6" height="6" patternUnits="userSpaceOnUse"><circle cx="1" cy="2" r=".6" fill="#000" opacity=".07"/><circle cx="4" cy="5" r=".5" fill="#fff" opacity=".06"/></pattern>
  <filter id="drop" x="-25%" y="-25%" width="150%" height="160%"><feDropShadow dx="0" dy="6" stdDeviation="5" flood-color="#000" flood-opacity=".55"/></filter>
  <filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="7"/></filter>
  <filter id="glowS" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3"/></filter>
</defs>`;

const svg = (w, h, body) => `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">
<style>.lg{font-family:'Luckiest Guy',sans-serif}.li{font-family:'Lilita One',sans-serif}</style>${DEFS}${body}</svg>`;

function burst(cx, cy, r1, r2, n, fill, extra = '') {
  let d = '';
  for (let i = 0; i < n * 2; i++) {
    const [x, y] = pol(cx, cy, i % 2 ? r1 : r2, (i * Math.PI) / n - Math.PI / 2);
    d += (i ? 'L' : 'M') + x + ',' + y;
  }
  return `<path d="${d}Z" fill="${fill}" ${extra}/>`;
}
function rays(cx, cy, r, n, color, op) {
  let s = '';
  for (let i = 0; i < n; i++) {
    const a0 = (i * TAU) / n, a1 = a0 + TAU / n / 2;
    s += `<path d="M${cx},${cy}L${pol(cx, cy, r, a0)}L${pol(cx, cy, r, a1)}Z" fill="${color}" opacity="${op}"/>`;
  }
  return s;
}
const sparkle = (x, y, r, c = '#fff') => burst(x, y, r * .22, r, 4, c) + `<circle cx="${x}" cy="${y}" r="${f(r * .35)}" fill="${c}" opacity=".6" filter="url(#glowS)"/>`;

function ball(cx, cy, r, w = 5, fill = 'url(#ballG)', seam = '#fffde8') {
  return `<circle cx="${cx}" cy="${cy}" r="${r}" fill="${fill}" ${ink(w)}/>
  <path d="M${f(cx - r * .92)},${f(cy - r * .35)} C${f(cx - r * .25)},${f(cy - r * .25)} ${f(cx - r * .2)},${f(cy + r * .8)} ${f(cx - r * .45)},${f(cy + r * .88)}" fill="none" stroke="${seam}" stroke-width="${f(r * .13)}" stroke-linecap="round"/>
  <path d="M${f(cx + r * .45)},${f(cy - r * .88)} C${f(cx + r * .2)},${f(cy - r * .8)} ${f(cx + r * .25)},${f(cy + r * .25)} ${f(cx + r * .92)},${f(cy + r * .35)}" fill="none" stroke="${seam}" stroke-width="${f(r * .13)}" stroke-linecap="round"/>
  <ellipse cx="${f(cx - r * .35)}" cy="${f(cy - r * .42)}" rx="${f(r * .28)}" ry="${f(r * .15)}" fill="#fff" opacity=".75" transform="rotate(-30 ${f(cx - r * .35)} ${f(cy - r * .42)})"/>`;
}

function eye(cx, cy, r, look = [0, 0], lid = 0, lidFill = 'url(#skinL)', iris = '#3b2a1e') {
  const px = cx + look[0] * r * .35, py = cy + look[1] * r * .3;
  let s = `<ellipse cx="${cx}" cy="${cy}" rx="${f(r * .8)}" ry="${r}" fill="#fff" ${ink(3.5)}/>
  <circle cx="${f(px)}" cy="${f(py + r * .08)}" r="${f(r * .55)}" fill="${iris}"/>
  <circle cx="${f(px)}" cy="${f(py + r * .08)}" r="${f(r * .3)}" fill="${INK}"/>
  <circle cx="${f(px - r * .2)}" cy="${f(py - r * .15)}" r="${f(r * .18)}" fill="#fff"/>
  <circle cx="${f(px + r * .18)}" cy="${f(py + r * .25)}" r="${f(r * .08)}" fill="#fff" opacity=".8"/>`;
  if (lid > 0) {
    const ly = cy - r + lid * 2 * r;
    s += `<path d="M${f(cx - r * .9)},${f(cy - r * .05)} Q${cx},${f(cy - r * 1.55)} ${f(cx + r * .9)},${f(cy - r * .05)} L${f(cx + r * .9)},${f(ly)} Q${cx},${f(ly - r * .2)} ${f(cx - r * .9)},${f(ly)}Z" fill="${lidFill}" ${ink(3.5)}/>`;
  }
  return s;
}

// ------------------------------------------------------------------ premium medallion
const GEMS = { p: '#e8343f', c: '#3d8bff', u: '#2fd06a', k: '#b44dff', d: '#ff9f1c' };
const MED = { cx: 128, cy: 140, r: 94 };
function medallion(id, accent, body) {
  const { cx, cy, r } = MED;
  const rnd = mulberry(id.charCodeAt(0));
  let bokeh = '';
  for (let i = 0; i < 14; i++) bokeh += `<circle cx="${f(cx - r + rnd() * 2 * r)}" cy="${f(cy - r + rnd() * 1.3 * r)}" r="${f(4 + rnd() * 12)}" fill="${['#fff', accent, '#ffe17a'][i % 3]}" opacity="${f(.08 + rnd() * .14)}" filter="url(#glowS)"/>`;
  return `
  <radialGradient id="st${id}" cx=".5" cy=".18" r=".95"><stop offset="0" stop-color="${accent}" stop-opacity=".95"/><stop offset=".45" stop-color="#123a2a"/><stop offset="1" stop-color="#05140d"/></radialGradient>
  <clipPath id="cc${id}"><circle cx="${cx}" cy="${cy}" r="${r}"/></clipPath>
  <clipPath id="ch${id}"><circle cx="${cx}" cy="${cy}" r="${r}"/><rect x="${cx - r - 22}" y="-60" width="${2 * r + 44}" height="${cy + 60}"/></clipPath>
  <clipPath id="lo${id}"><rect x="0" y="${cy - 8}" width="256" height="200"/></clipPath>
  <circle cx="${cx}" cy="${cy}" r="${r + 22}" fill="${accent}" opacity=".45" filter="url(#glow)"/>
  <g filter="url(#drop)">
    <circle cx="${cx}" cy="${cy}" r="${r + 13}" fill="url(#gold)" ${ink(5)}/>
    <circle cx="${cx}" cy="${cy}" r="${r + 5}" fill="none" stroke="#6e4205" stroke-width="2"/>
    <circle cx="${cx}" cy="${cy}" r="${r}" fill="url(#st${id})" ${ink(3.5)}/>
  </g>
  <g clip-path="url(#cc${id})">
    ${rays(cx, cy - r * .9, 2.2 * r, 14, '#fff', .06)}${bokeh}
    <ellipse cx="${cx}" cy="${cy + r - 6}" rx="${r}" ry="30" fill="#000" opacity=".25"/>
  </g>
  <g clip-path="url(#ch${id})">${body}</g>
  <g clip-path="url(#lo${id})">
    <circle cx="${cx}" cy="${cy}" r="${r + 13}" fill="none" ${ink(5)}/>
    <circle cx="${cx}" cy="${cy}" r="${r + 7}" fill="none" stroke="url(#gold)" stroke-width="10"/>
    <circle cx="${cx}" cy="${cy}" r="${r + 2}" fill="none" stroke="#6e4205" stroke-width="1.5"/>
    <circle cx="${cx}" cy="${cy}" r="${r}" fill="none" ${ink(3.5)}/>
  </g>
  <path d="M${cx - 76},${cy - 58} A${r + 9},${r + 9} 0 0,1 ${cx - 16},${cy - r - 8}" fill="none" stroke="#fff" stroke-width="3.5" stroke-linecap="round" opacity=".85"/>
  <g filter="url(#drop)"><path d="M${cx},${cy + r + 2} l13,13 l-13,13 l-13,-13Z" fill="${GEMS[id]}" ${ink(3.5)}/>
  <path d="M${cx},${cy + r + 5} l7,7 l-7,4Z" fill="#fff" opacity=".7"/></g>`;
}

const torso = (fill, extra = '') => `<path d="M24,262 C28,212 60,194 100,188 L156,188 C196,194 228,212 232,262Z" fill="${fill}" ${ink(5)}/>${extra}
  <path d="M154,190 C194,196 226,216 230,262 L160,262Z" fill="#000" opacity=".22"/>
  <path d="M40,226 C52,206 74,196 96,192" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round" opacity=".35"/>`;
const rim = (cx, cy, rx, ry, c = '#fff') => `<path d="M${pol(cx, cy, rx * .9, Math.PI * 1.1)} A${f(rx * .9)},${f(ry * .9)} 0 0,1 ${pol(cx, cy, rx * .9, Math.PI * 1.45)}" fill="none" stroke="${c}" stroke-width="5" stroke-linecap="round" opacity=".6"/>`;
const sideLight = (cx, cy, rx, ry) => `<path d="M${pol(cx, cy, rx, -Math.PI * .35)} A${rx},${ry} 0 0,1 ${pol(cx, cy, rx, Math.PI * .3)}" fill="none" stroke="#ffe9a0" stroke-width="4" opacity=".55"/>`;

// H1 — the Champion: cocky male star, golden headband, smirk
function champion() {
  let strings = '';
  for (let i = -4; i <= 4; i++) strings += `<line x1="${i * 9}" y1="-60" x2="${i * 9}" y2="60" stroke="#fff" stroke-width="1.8" opacity=".9"/>`;
  for (let j = -5; j <= 5; j++) strings += `<line x1="-46" y1="${j * 9}" x2="46" y2="${j * 9}" stroke="#fff" stroke-width="1.8" opacity=".9"/>`;
  const b = `
    <g transform="translate(60 92) rotate(-26)">
      <clipPath id="h1r"><ellipse cx="0" cy="0" rx="32" ry="44"/></clipPath>
      <rect x="-6" y="42" width="12" height="80" rx="5" fill="#2b2b2b" ${ink(3.5)}/>
      <ellipse cx="0" cy="0" rx="40" ry="52" fill="url(#gold)" ${ink(5)}/>
      <ellipse cx="0" cy="0" rx="32" ry="44" fill="#0f3a28"/><g clip-path="url(#h1r)">${strings}</g>
      <ellipse cx="0" cy="0" rx="32" ry="44" fill="none" ${ink(3)}/>
    </g>
    ${torso('url(#white)', `<path d="M100,188 L128,214 L156,188" fill="none" stroke="url(#gold)" stroke-width="9"/><path d="M100,188 L128,214 L156,188" fill="none" ${ink(3)}/>
      <path d="M168,212 h22 v14 q-11,11 -22,0Z" fill="url(#gold)" ${ink(3)}/><text x="179" y="223" text-anchor="middle" class="lg" font-size="10" fill="#16120f">GR</text>`)}
    <rect x="110" y="160" width="36" height="34" fill="url(#skinM)" ${ink(4)}/>
    <ellipse cx="72" cy="114" rx="12" ry="16" fill="url(#skinM)" ${ink(4)}/>
    <ellipse cx="184" cy="114" rx="12" ry="16" fill="url(#skinM)" ${ink(4)}/>
    <path d="M70,96 C66,140 86,174 128,176 C170,174 190,140 186,96 C186,58 162,40 128,40 C94,40 70,58 70,96Z" fill="url(#skinM)" ${ink(5)}/>
    ${rim(128, 108, 58, 68)}${sideLight(128, 108, 56, 66)}
    <path d="M66,86 C58,48 92,22 132,24 C170,22 196,44 190,84 C176,66 160,60 140,62 C150,52 148,44 136,40 C132,52 116,60 96,62 C84,66 72,74 66,86Z" fill="url(#hairD)" ${ink(4.5)}/>
    <path d="M110,34 C126,26 150,28 164,40" fill="none" stroke="#e8b25a" stroke-width="4" stroke-linecap="round" opacity=".8"/>
    <path d="M68,82 Q128,62 188,82 L188,94 Q128,74 68,94Z" fill="url(#gold)" ${ink(3.5)}/>
    <path d="M86,104 q14,-12 30,-4" fill="none" ${ink(6)}/>
    <path d="M140,96 q16,-10 30,0" fill="none" ${ink(6)}/>
    ${eye(102, 120, 12, [.4, .1], .45, 'url(#skinM)')}
    ${eye(154, 118, 12, [.4, .1], .3, 'url(#skinM)')}
    <path d="M124,126 q-6,14 4,18" fill="none" ${ink(3.5)}/>
    <path d="M104,152 Q132,166 158,146" fill="none" ${ink(4.5)}/>
    <path d="M150,148 q8,-2 10,-8" fill="none" ${ink(3.5)}/>
    ${[[98, 160], [108, 166], [148, 160], [140, 166], [120, 168], [130, 168]].map(([x, y]) => `<circle cx="${x}" cy="${y}" r="1.4" fill="#6e3f22" opacity=".7"/>`).join('')}
    ${sparkle(176, 132, 10)}`;
  return svg(256, 256, medallion('p', '#e8343f', b));
}

// H2 — the Star: confident champion, gold hoops, curly puff
function star() {
  let strings = '';
  for (let i = -4; i <= 4; i++) strings += `<line x1="${i * 9}" y1="-60" x2="${i * 9}" y2="60" stroke="#fff" stroke-width="1.8"/>`;
  for (let j = -5; j <= 5; j++) strings += `<line x1="-46" y1="${j * 9}" x2="46" y2="${j * 9}" stroke="#fff" stroke-width="1.8"/>`;
  const b = `
    <g transform="translate(198 92) rotate(26)">
      <clipPath id="h2r"><ellipse cx="0" cy="0" rx="32" ry="44"/></clipPath>
      <rect x="-6" y="42" width="12" height="80" rx="5" fill="#2b2b2b" ${ink(3.5)}/>
      <ellipse cx="0" cy="0" rx="40" ry="52" fill="url(#red)" ${ink(5)}/>
      <ellipse cx="0" cy="0" rx="32" ry="44" fill="#0f3a28"/><g clip-path="url(#h2r)">${strings}</g>
    </g>
    <path d="M62,44 C30,26 10,58 24,84 C12,104 28,130 54,124 C44,98 54,72 76,60Z" fill="url(#hairD)" ${ink(4.5)}/>
    <path d="M30,64 q10,-10 24,-6 M24,90 q10,-6 20,0" fill="none" stroke="#8a5a3a" stroke-width="3" opacity=".7"/>
    ${torso('url(#green)', `<path d="M100,188 L128,212 L156,188" fill="none" stroke="#fff" stroke-width="8"/><path d="M36,232 h184" stroke="url(#gold)" stroke-width="6"/>`)}
    <rect x="110" y="162" width="36" height="32" fill="url(#skinB)" ${ink(4)}/>
    <ellipse cx="128" cy="108" rx="58" ry="66" fill="url(#skinB)" ${ink(5)}/>
    ${rim(128, 108, 58, 66, '#ffd9b0')}${sideLight(128, 108, 58, 66)}
    <circle cx="70" cy="132" r="9" fill="none" stroke="url(#gold)" stroke-width="4"/>
    <circle cx="186" cy="132" r="9" fill="none" stroke="url(#gold)" stroke-width="4"/>
    <path d="M70,82 C68,40 100,28 128,30 C160,28 190,44 186,84 C174,64 150,56 128,60 C102,58 82,66 70,82Z" fill="url(#hairD)" ${ink(4.5)}/>
    <path d="M70,76 Q128,52 188,76 L188,92 Q128,68 70,92Z" fill="url(#white)" ${ink(3.5)}/>
    <path d="M72,84 Q128,61 186,84" fill="none" stroke="url(#gold)" stroke-width="3.5"/>
    <path d="M88,98 q14,-10 28,-2 M140,96 q14,-8 28,2" fill="none" ${ink(5.5)}/>
    ${eye(104, 116, 12.5, [.45, 0], .2, 'url(#skinB)')}
    ${eye(152, 116, 12.5, [.45, 0], .2, 'url(#skinB)')}
    <path d="M88,108 l-8,-4 M168,108 l8,-4" ${ink(3)}/>
    <path d="M124,122 q6,16 -2,20 q6,2 10,-2" fill="none" ${ink(3.5)}/>
    <path d="M100,146 Q128,174 158,144 Q156,162 128,166 Q104,164 100,146Z" fill="#fff" ${ink(4)}/>
    <path d="M100,146 Q128,156 158,144" fill="none" ${ink(2)}/>
    <path d="M108,134 q-6,4 -4,10 M152,134 q6,4 4,10" fill="none" stroke="#6e3f22" stroke-width="2" opacity=".6"/>
    ${sparkle(170, 150, 11)}`;
  return svg(256, 256, medallion('c', '#3d8bff', b));
}

// H3 — the Umpire: strict, shouting OUT!
function umpire() {
  const b = `
    ${torso('url(#green)', `<path d="M100,188 L128,226 L156,188Z" fill="url(#white)" ${ink(3.5)}/><path d="M122,202 h12 l4,32 l-10,10 l-10,-10Z" fill="url(#burgundy)" ${ink(3)}/>
      <circle cx="96" cy="222" r="4" fill="url(#gold)" ${ink(1.5)}/><circle cx="96" cy="242" r="4" fill="url(#gold)" ${ink(1.5)}/>`)}
    <rect x="112" y="164" width="32" height="30" fill="url(#skinM)" ${ink(4)}/>
    <ellipse cx="74" cy="120" rx="10" ry="14" fill="url(#skinM)" ${ink(4)}/>
    <path d="M70,112 C70,58 92,40 128,40 C164,40 186,58 186,112 C186,166 162,188 128,188 C94,188 70,166 70,112Z" fill="url(#skinM)" ${ink(5)}/>
    ${rim(128, 114, 56, 72)}${sideLight(128, 114, 56, 72)}
    <path d="M78,58 C82,22 176,22 180,58Z" fill="url(#white)" ${ink(4.5)}/>
    <path d="M78,56 h102" stroke="url(#gold)" stroke-width="6"/>
    <path d="M64,58 h128 l22,12 h-150Z" fill="url(#navy)" ${ink(4.5)}/>
    <path d="M74,128 C60,134 58,150 70,158" fill="none" ${ink(3)}/><circle cx="72" cy="160" r="6" fill="#2b2b2b" ${ink(2)}/>
    <path d="M86,92 l30,12 M170,92 l-30,12" ${ink(7)}/>
    <circle cx="106" cy="112" r="17" fill="#e8f3ff" fill-opacity=".9" ${ink(4.5)}/>
    <circle cx="152" cy="112" r="17" fill="#e8f3ff" fill-opacity=".9" ${ink(4.5)}/>
    <path d="M94,104 l8,-6 M140,104 l8,-6" stroke="#fff" stroke-width="3" stroke-linecap="round"/>
    <line x1="123" y1="112" x2="135" y2="112" ${ink(4.5)}/>
    <circle cx="108" cy="116" r="5" fill="${INK}"/><circle cx="150" cy="116" r="5" fill="${INK}"/>
    <path d="M124,124 q-4,16 6,18" fill="none" ${ink(3.5)}/>
    <ellipse cx="128" cy="160" rx="22" ry="17" fill="#6b1414" ${ink(4.5)}/>
    <path d="M112,168 q16,-10 32,0 q-16,10 -32,0Z" fill="#e8665a"/><path d="M112,151 h32" stroke="#fff" stroke-width="5"/>
    <g filter="url(#drop)"><path d="M132,4 h76 a12,12 0 0 1 12,12 v28 a12,12 0 0 1 -12,12 h-42 l-20,16 l4,-16 h-18 a12,12 0 0 1 -12,-12 v-28 a12,12 0 0 1 12,-12Z" fill="url(#white)" ${ink(4)}/></g>
    <text x="170" y="44" text-anchor="middle" class="lg" font-size="29" fill="url(#red)" stroke="${INK}" stroke-width="1.5">OUT!</text>`;
  return svg(256, 256, medallion('u', '#2fd06a', b));
}

// H4 — the President: chic club president with monocle
function president() {
  const b = `
    ${torso('url(#burgundy)', `<path d="M100,188 L128,230 L156,188Z" fill="url(#white)" ${ink(3.5)}/>
      <path d="M108,204 L128,212 L148,204 L148,224 L128,216 L108,224Z" fill="url(#gold)" ${ink(3.5)}/><circle cx="128" cy="214" r="4" fill="#e8343f" ${ink(1.5)}/>
      <path d="M58,214 h22 v14 q-11,11 -22,0Z" fill="url(#gold)" ${ink(3)}/>`)}
    <rect x="110" y="164" width="36" height="30" fill="url(#skinL)" ${ink(4)}/>
    <ellipse cx="64" cy="116" rx="12" ry="16" fill="url(#skinL)" ${ink(4)}/>
    <ellipse cx="192" cy="116" rx="12" ry="16" fill="url(#skinL)" ${ink(4)}/>
    <ellipse cx="128" cy="106" rx="62" ry="68" fill="url(#skinL)" ${ink(5)}/>
    ${rim(128, 106, 62, 68)}${sideLight(128, 106, 62, 68)}
    <path d="M66,100 q-16,-26 4,-42 q-2,20 18,24 q-12,12 -22,18Z" fill="url(#silver)" ${ink(3.5)}/>
    <path d="M190,100 q16,-26 -4,-42 q2,20 -18,24 q12,12 22,18Z" fill="url(#silver)" ${ink(3.5)}/>
    <ellipse cx="102" cy="58" rx="22" ry="10" fill="#fff" opacity=".8" transform="rotate(-20 102 58)"/>
    <path d="M82,82 q18,-18 36,-6" fill="none" stroke="#e6e9ef" stroke-width="12" stroke-linecap="round"/>
    <path d="M140,68 q18,-16 36,0" fill="none" stroke="#e6e9ef" stroke-width="12" stroke-linecap="round"/>
    <path d="M82,82 q18,-18 36,-6 M140,68 q18,-16 36,0" fill="none" ${ink(2.5)}/>
    ${eye(102, 102, 12, [.4, .2], .55)}
    ${eye(156, 100, 15, [-.3, .1], 0)}
    <circle cx="156" cy="100" r="21" fill="#cfeaff" fill-opacity=".35" stroke="url(#gold)" stroke-width="6"/>
    <circle cx="156" cy="100" r="21" fill="none" ${ink(2.5)}/>
    <path d="M143,90 l8,-6" stroke="#fff" stroke-width="3" stroke-linecap="round"/>
    <path d="M176,110 C192,140 186,170 176,196" fill="none" stroke="url(#gold)" stroke-width="3" stroke-dasharray="4 3"/>
    <ellipse cx="128" cy="132" rx="16" ry="13" fill="#e8665a" ${ink(4)}/>
    <ellipse cx="122" cy="127" rx="5" ry="3" fill="#fff" opacity=".75"/>
    <path d="M128,142 C112,134 92,140 80,128 C68,118 54,124 58,138 C46,132 50,114 64,112 C80,138 108,146 128,144 C148,146 176,138 192,112 C206,114 210,132 198,138 C202,124 188,118 176,128 C164,140 144,134 128,142Z" fill="url(#silver)" ${ink(4)}/>
    <path d="M112,160 q16,8 30,-2" fill="none" ${ink(3.5)}/>
    <circle cx="86" cy="138" r="8" fill="#ff8c8c" opacity=".45"/>`;
  return svg(256, 256, medallion('k', '#b44dff', b));
}

// H5 — ACE, the club mascot bulldog: proud, gold medal, headband
function ace() {
  const b = `
    <path d="M36,262 C40,214 72,198 128,198 C184,198 216,214 220,262Z" fill="url(#fur)" ${ink(5)}/>
    <path d="M62,212 Q128,236 194,212 L198,230 Q128,254 58,230Z" fill="url(#navy)" ${ink(4)}/>
    <g filter="url(#drop)"><circle cx="128" cy="238" r="16" fill="url(#gold)" ${ink(3.5)}/>
    <text x="128" y="243" text-anchor="middle" class="lg" font-size="11" fill="${INK}">ACE</text></g>
    <ellipse cx="128" cy="122" rx="84" ry="72" fill="url(#fur)" ${ink(5)}/>
    ${rim(128, 122, 84, 72)}${sideLight(128, 122, 84, 72)}
    <path d="M70,64 L26,72 Q32,104 58,106 Q56,86 76,76Z" fill="#7a4b2a" ${ink(4.5)}/>
    <path d="M186,64 L230,72 Q224,104 198,106 Q200,86 180,76Z" fill="#7a4b2a" ${ink(4.5)}/>
    <path d="M66,64 Q128,38 190,64 L192,82 Q128,56 64,82Z" fill="url(#ballG)" ${ink(4)}/>
    <text x="128" y="72" text-anchor="middle" class="lg" font-size="14" fill="#1f5e33" transform="rotate(0)">ACE</text>
    <path d="M98,96 q12,-6 22,2 M136,98 q10,-8 22,-2" fill="none" stroke="#9c6532" stroke-width="4" stroke-linecap="round"/>
    <path d="M82,110 q16,-10 30,-2 M174,110 q-16,-10 -30,-2" fill="none" ${ink(6)}/>
    ${eye(100, 124, 13, [.2, .1], .35, 'url(#fur)')}
    ${eye(156, 124, 13, [-.2, .1], .35, 'url(#fur)')}
    <path d="M68,150 C68,188 104,198 128,194 C152,198 188,188 188,150 C172,166 150,160 128,160 C106,160 84,166 68,150Z" fill="#f6ead6" ${ink(4.5)}/>
    <ellipse cx="128" cy="146" rx="24" ry="15" fill="${INK}"/>
    <ellipse cx="119" cy="140" rx="8" ry="4" fill="#fff" opacity=".65"/>
    <path d="M96,174 Q128,198 160,174 Q150,196 128,198 Q106,196 96,174Z" fill="#6b1414" ${ink(4)}/>
    <path d="M114,186 q14,10 28,0 q-4,12 -14,12 q-10,0 -14,-12Z" fill="#ff7a8a"/>
    <path d="M100,176 l6,-14 l6,16Z M144,178 l6,-16 l6,14Z" fill="#fff" ${ink(2)}/>
    ${sparkle(184, 186, 10)}`;
  return svg(256, 256, medallion('d', '#ff9f1c', b));
}

// WILD — the Golden Fireball
function wild() {
  let tongues = '';
  for (let i = 0; i < 5; i++) {
    const y = 108 + (i - 2) * 16, len = 120 - Math.abs(i - 2) * 22;
    tongues += `<path d="M128,${y} C${128 - len * .4},${y - 14} ${128 - len * .7},${y + 10} ${128 - len},${y - 4} C${128 - len * .7},${y + 22} ${128 - len * .35},${y + 20} 128,${y + 14}Z" fill="url(#flame)" opacity=".95"/>`;
  }
  return svg(256, 256, `
    <circle cx="150" cy="112" r="100" fill="#ff8a1e" opacity=".35" filter="url(#glow)"/>
    ${rays(150, 112, 130, 16, '#ffe17a', .14)}
    <g transform="rotate(-18 150 112)">${tongues}</g>
    <g filter="url(#drop)">${ball(156, 104, 54, 5, 'url(#goldR)', '#fff6c8')}</g>
    <circle cx="156" cy="104" r="54" fill="none" stroke="#fff" stroke-width="2" opacity=".5"/>
    ${sparkle(206, 48, 16)}${sparkle(98, 46, 10)}${sparkle(214, 160, 9)}
    <g filter="url(#drop)">
      <path d="M24,186 L232,186 L220,208 L232,230 L24,230 L36,208Z" fill="url(#gold)" ${ink(5)}/>
      <path d="M34,192 H222" stroke="#fff" stroke-width="3" opacity=".7"/>
    </g>
    <text x="128" y="223" text-anchor="middle" class="lg" font-size="40" fill="#5a1a0a" letter-spacing="4">WILD</text>
    <text x="128" y="221" text-anchor="middle" class="lg" font-size="40" fill="url(#red)" stroke="${INK}" stroke-width="1.5" letter-spacing="4">WILD</text>`);
}

// SCATTER — the Golden Rally Cup (our own fictional trophy)
function cup() {
  let laurel = '';
  for (const side of [-1, 1]) for (let i = 0; i < 7; i++) {
    const a = Math.PI / 2 + side * (0.5 + i * 0.3);
    const [x, y] = pol(128, 118, 92, a);
    laurel += `<ellipse cx="${x}" cy="${y}" rx="14" ry="6" fill="url(#gold)" stroke="#6e4205" stroke-width="1.5" transform="rotate(${f((a * 180) / Math.PI + (side > 0 ? -62 : 62))} ${x} ${y})"/>`;
  }
  return svg(256, 256, `
    <circle cx="128" cy="112" r="110" fill="#2fd06a" opacity=".35" filter="url(#glow)"/>
    ${rays(128, 104, 140, 20, '#fff6c8', .16)}
    ${laurel}
    <g filter="url(#drop)">
      <path d="M82,52 C42,50 40,104 90,114 M174,52 C214,50 216,104 166,114" fill="none" stroke="${INK}" stroke-width="15" stroke-linecap="round"/>
      <path d="M82,52 C42,50 40,104 90,114 M174,52 C214,50 216,104 166,114" fill="none" stroke="url(#gold)" stroke-width="8" stroke-linecap="round"/>
      <path d="M74,40 H182 C182,108 160,136 128,142 C96,136 74,108 74,40Z" fill="url(#gold)" ${ink(5)}/>
      <path d="M90,50 C90,98 102,122 120,132" fill="none" stroke="#fff" stroke-width="7" stroke-linecap="round" opacity=".85"/>
      <path d="M74,40 H182" stroke="#fff6c8" stroke-width="3"/>
      <rect x="116" y="140" width="24" height="22" fill="url(#goldH)" ${ink(4)}/>
      <path d="M84,162 H172 L182,188 H74Z" fill="url(#gold)" ${ink(5)}/>
      <rect x="92" y="168" width="72" height="12" rx="3" fill="#0f4a2c" stroke="#6e4205" stroke-width="1.5"/>
      <text x="128" y="178" text-anchor="middle" class="li" font-size="9" fill="#ffe17a" letter-spacing="1">GOLDEN RALLY</text>
    </g>
    ${ball(128, 26, 16, 4)}
    ${sparkle(46, 52, 14)}${sparkle(212, 40, 12)}${sparkle(220, 146, 9)}
    <g filter="url(#drop)">
      <path d="M20,196 L236,196 L224,214 L236,232 L20,232 L32,214Z" fill="url(#green)" ${ink(5)}/>
      <path d="M30,201 H226" stroke="url(#gold)" stroke-width="3"/>
    </g>
    <text x="128" y="227" text-anchor="middle" class="lg" font-size="31" fill="url(#gold)" stroke="${INK}" stroke-width="1.5" letter-spacing="3">BONUS</text>`);
}

// LOW — jewelled tournament tokens (hexagon, metal rim, glowing score)
function token(label, gem, metal, size) {
  const id = 't' + label;
  const hex = (r) => Array.from({ length: 6 }, (_, i) => pol(128, 134, r, -Math.PI / 2 + (i * TAU) / 6).join(',')).join(' ');
  let facets = '';
  const outer = Array.from({ length: 6 }, (_, i) => pol(128, 134, 88, -Math.PI / 2 + (i * TAU) / 6));
  const inner = Array.from({ length: 6 }, (_, i) => pol(128, 134, 58, -Math.PI / 2 + (i * TAU) / 6));
  for (let i = 0; i < 6; i++) {
    const j = (i + 1) % 6;
    facets += `<path d="M${outer[i]} L${outer[j]} L${inner[j]} L${inner[i]}Z" fill="${i < 3 ? '#fff' : '#000'}" opacity="${[.18, .1, .04, .12, .2, .08][i]}"/>`;
  }
  return svg(256, 256, `
    <radialGradient id="${id}" cx=".4" cy=".3" r=".9"><stop offset="0" stop-color="#ffffff" stop-opacity=".9"/><stop offset=".25" stop-color="${gem}"/><stop offset=".8" stop-color="${gem}" stop-opacity=".85"/><stop offset="1" stop-color="#000" stop-opacity=".6"/></radialGradient>
    <linearGradient id="n${id}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset=".55" stop-color="#ffffff"/><stop offset=".56" stop-color="#f1f1f1"/><stop offset="1" stop-color="#d9d9d9"/></linearGradient>
    <circle cx="128" cy="134" r="104" fill="${gem}" opacity=".4" filter="url(#glow)"/>
    <g filter="url(#drop)">
      <polygon points="${hex(106)}" fill="url(#${metal})" ${ink(5)}/>
      <polygon points="${hex(96)}" fill="none" stroke="#000" stroke-width="2" opacity=".35"/>
      <polygon points="${hex(88)}" fill="url(#${id})" ${ink(3.5)}/>
    </g>
    ${facets}
    <polygon points="${hex(88)}" fill="none" ${ink(3.5)}/>
    <path d="M${pol(128, 134, 99, -Math.PI / 2 - TAU / 6)} L${pol(128, 134, 99, -Math.PI / 2)}" stroke="#fff" stroke-width="4" stroke-linecap="round" opacity=".8"/>
    <text x="128" y="${f(134 + size * .36)}" text-anchor="middle" class="lg" font-size="${size}" fill="${gem}" opacity=".9" filter="url(#glow)">${label}</text>
    <text x="128" y="${f(138 + size * .36)}" text-anchor="middle" class="lg" font-size="${size}" fill="${INK}" opacity=".55">${label}</text>
    <text x="128" y="${f(134 + size * .36)}" text-anchor="middle" class="lg" font-size="${size}" fill="url(#n${id})" stroke="${INK}" stroke-width="5" stroke-linejoin="round" paint-order="stroke">${label}</text>`);
}

// ------------------------------------------------------------------ night stadium (animated layers)
const LAYERS = {};
function background(w, h, key) {
  const horizon = Math.round(h * (w > h ? 0.5 : 0.4));
  const rnd = mulberry(9);
  let stars = '';
  for (let i = 0; i < 60; i++) stars += `<circle cx="${f(rnd() * w)}" cy="${f(rnd() * horizon * .4)}" r="${f(.5 + rnd() * 1.3)}" fill="#F2E5C3" opacity="${f(.2 + rnd() * .5)}"/>`;
  const lamp = (x) => `<rect x="${x - 4}" y="${f(horizon * .18)}" width="8" height="${f(horizon * .6)}" fill="#05121a"/>
    <rect x="${x - 46}" y="${f(horizon * .1)}" width="92" height="36" rx="5" fill="#0d2430" stroke="#05121a" stroke-width="3"/>
    ${Array.from({ length: 8 }, (_, i) => `<circle cx="${x - 34 + (i % 4) * 22.6}" cy="${f(horizon * .1 + 10 + Math.floor(i / 4) * 16)}" r="6.5" fill="#fff7e2"/>`).join('')}
    <circle cx="${x}" cy="${f(horizon * .1 + 18)}" r="70" fill="#ffefc8" opacity=".28" filter="url(#glow)"/>`;
  const sky = svg(w, h, `
    <linearGradient id="nsky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#040e14"/><stop offset=".55" stop-color="#081B23"/><stop offset="1" stop-color="#0c2e33"/></linearGradient>
    <linearGradient id="stand" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0a1e27"/><stop offset="1" stop-color="#082a26"/></linearGradient>
    <rect width="${w}" height="${h}" fill="url(#nsky)"/>
    ${stars}
    <path d="M0,${horizon - 230} Q${w / 2},${horizon - 296} ${w},${horizon - 230} L${w},${horizon - 204} Q${w / 2},${horizon - 266} 0,${horizon - 204}Z" fill="#05121a"/>
    ${lamp(w * .1)}${lamp(w * .9)}
    <path d="M-10,${horizon - 204} Q${w / 2},${horizon - 262} ${w + 10},${horizon - 204} L${w + 10},${horizon + 10} L-10,${horizon + 10}Z" fill="url(#stand)"/>
    ${Array.from({ length: 6 }, (_, i) => `<path d="M-10,${horizon - 172 + i * 30} Q${w / 2},${horizon - 222 + i * 28} ${w + 10},${horizon - 172 + i * 30}" fill="none" stroke="#123542" stroke-width="2" opacity=".6"/>`).join('')}
    <rect x="0" y="${horizon}" width="${w}" height="${h - horizon}" fill="#062a22"/>`);
  // crowd: softly blurred silhouettes, muted colours
  let crowd = '';
  const cols = ['#5b6f7a', '#8a7a5a', '#4d6b5e', '#6f5f6a', '#9a8f78', '#3f5866'];
  for (let row = 0; row < 6; row++) {
    for (let i = 0; i < w / 24 + 1; i++) {
      const x = i * 24 + (row % 2) * 12 + rnd() * 5;
      const y = horizon - 28 - row * 27 - Math.sin((x / w) * Math.PI) * (row * 8);
      crowd += `<rect x="${f(x - 8)}" y="${f(y + 4)}" width="16" height="22" rx="6" fill="${cols[Math.floor(rnd() * cols.length)]}" opacity=".7"/><circle cx="${f(x)}" cy="${f(y)}" r="7" fill="#1d2a30"/>`;
    }
  }
  const cy0 = horizon - 240, ch = 270;
  const crowdSvg = svg(w, ch, `<filter id="cblur"><feGaussianBlur stdDeviation="1.6"/></filter><g transform="translate(0 ${-cy0})" filter="url(#cblur)">${crowd}</g>`);
  // fore: LED board + emerald court in perspective
  const fy0 = horizon - 16;
  const cx = w / 2, top = horizon + 30, bot = h + 60, tw = w * .6, bw = w * 1.8;
  const at = (u, v) => [f(cx + (u * (tw + (bw - tw) * v)) / 2), f(top + (bot - top) * v)];
  const L = (a, b, sw = 7) => `<line x1="${a[0]}" y1="${a[1]}" x2="${b[0]}" y2="${b[1]}" stroke="#F2E5C3" stroke-width="${sw}" opacity=".85"/>`;
  let court = `<path d="M${at(-1.2, 0)} L${at(1.2, 0)} L${at(1.2, 1)} L${at(-1.2, 1)}Z" fill="#073328"/>`;
  court += `<path d="M${at(-1, 0)} L${at(1, 0)} L${at(1, 1)} L${at(-1, 1)}Z" fill="#093A31"/>`;
  for (const u of [-1, -.78, .78, 1]) court += L(at(u, 0), at(u, 1));
  for (const v of [0, .45]) court += L(at(-1, v), at(1, v));
  court += L(at(0, .45), at(0, 1));
  let led = '';
  for (let i = 0; i < Math.ceil(w / 560) + 1; i++) led += `<text x="${i * 560 + 30}" y="${horizon + 20}" style="font-family:'Cinzel',serif;font-weight:700" font-size="19" fill="#D5A64B" opacity=".8" letter-spacing="5">ACE! · CHAMPIONSHIP NIGHT ·</text>`;
  const fore = svg(w, h - fy0, `<g transform="translate(0 ${-fy0})">
    <radialGradient id="courtGlow" cx=".5" cy=".15" r=".7"><stop offset="0" stop-color="#fff2d6" stop-opacity=".18"/><stop offset="1" stop-color="#fff2d6" stop-opacity="0"/></radialGradient>
    <rect x="-10" y="${horizon - 14}" width="${w + 20}" height="44" fill="#041016"/>
    <line x1="0" y1="${horizon - 14}" x2="${w}" y2="${horizon - 14}" stroke="#D5A64B" stroke-width="1.5" opacity=".5"/>
    ${led}
    <rect x="0" y="${horizon + 30}" width="${w}" height="${h}" fill="#062a22"/>
    ${court}
    <rect x="0" y="${horizon + 30}" width="${w}" height="${h}" fill="url(#courtGlow)"/></g>`);
  const beam = (x, ang) => `<g transform="rotate(${ang} ${x} ${horizon * .12})"><path d="M${x - 34},${horizon * .12} L${x + 34},${horizon * .12} L${x + 300},${h} L${x - 300},${h}Z" fill="url(#beamG)"/></g>`;
  const beams = svg(w, h, `<linearGradient id="beamG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff2d6" stop-opacity=".24"/><stop offset=".6" stop-color="#fff2d6" stop-opacity=".05"/><stop offset="1" stop-color="#fff2d6" stop-opacity="0"/></linearGradient>
    ${beam(w * .1, -26)}${beam(w * .9, 26)}`);
  LAYERS[key] = { width: w, height: h, crowdY: cy0, foreY: fy0, flagsY: 0, crowdH: ch, horizon };
  return { sky, crowd: crowdSvg, fore, flags: beams };
}

// ------------------------------------------------------------------ frame: polished gold, dark glass field
export const CELL = 170;
function frame() {
  const iw = 6 * CELL, ih = 5 * CELL, m = 30;
  const w = iw + 2 * m, h = ih + 2 * m;
  let seps = '';
  for (let r = 1; r < 6; r++) seps += `<line x1="${m + r * CELL}" y1="${m + 22}" x2="${m + r * CELL}" y2="${m + ih - 22}" stroke="url(#sepG)" stroke-width="1.5"/>`;
  const corner = (x, y, sx, sy) => `<g transform="translate(${x} ${y}) scale(${sx} ${sy})">
      <path d="M0,34 L0,6 Q0,0 6,0 L34,0" fill="none" stroke="#F2E5C3" stroke-width="1.5" opacity=".7"/>
      <path d="M10,26 L10,12 Q10,10 12,10 L26,10" fill="none" stroke="#D5A64B" stroke-width="2"/>
      <circle cx="10" cy="10" r="3.5" fill="#D4E948" stroke="#3a2a10" stroke-width="1"/></g>`;
  return svg(w, h, `
    <linearGradient id="sepG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#D5A64B" stop-opacity="0"/><stop offset=".5" stop-color="#D5A64B" stop-opacity=".55"/><stop offset="1" stop-color="#D5A64B" stop-opacity="0"/></linearGradient>
    <radialGradient id="glass" cx=".5" cy="0" r="1.1"><stop offset="0" stop-color="#0f4a3d"/><stop offset=".55" stop-color="#093A31"/><stop offset="1" stop-color="#041a17"/></radialGradient>
    <linearGradient id="sheen" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".08"/><stop offset=".2" stop-color="#fff" stop-opacity="0"/></linearGradient>
    <filter id="fshadow" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="10" stdDeviation="12" flood-color="#000" flood-opacity=".6"/></filter>
    <rect x="6" y="6" width="${w - 12}" height="${h - 12}" rx="26" fill="url(#gold)" filter="url(#fshadow)"/>
    <rect x="6" y="6" width="${w - 12}" height="${h - 12}" rx="26" fill="none" stroke="#3a2a10" stroke-width="2.5"/>
    <rect x="12" y="12" width="${w - 24}" height="${h - 24}" rx="21" fill="none" stroke="#fbf0cf" stroke-width="1.2" opacity=".75"/>
    <rect x="${m - 6}" y="${m - 6}" width="${iw + 12}" height="${ih + 12}" rx="17" fill="#2a1d0b"/>
    <rect x="${m}" y="${m}" width="${iw}" height="${ih}" rx="13" fill="url(#glass)"/>
    ${seps}
    <rect x="${m}" y="${m}" width="${iw}" height="${ih}" rx="13" fill="url(#sheen)"/>
    <rect x="${m}" y="${m}" width="${iw}" height="${ih}" rx="13" fill="none" stroke="#000" stroke-width="2" opacity=".6"/>
    ${corner(m + 6, m + 6, 1, 1)}${corner(m + iw - 6, m + 6, -1, 1)}${corner(m + 6, m + ih - 6, 1, -1)}${corner(m + iw - 6, m + ih - 6, -1, -1)}`);
}

// ------------------------------------------------------------------ logo
function logo() {
  const w = 1000, h = 330;
  let laurel = '';
  for (const side of [-1, 1]) for (let i = 0; i < 5; i++) {
    const a = Math.PI / 2 + side * (1.15 + i * .22);
    const [x, y] = pol(500, 66, 54, a);
    laurel += `<ellipse cx="${x}" cy="${y}" rx="11" ry="4.5" fill="url(#gold)" stroke="#3a2a10" stroke-width="1" transform="rotate(${f((a * 180) / Math.PI + (side > 0 ? -70 : 70))} ${x} ${y})"/>`;
  }
  const emblem = `<g>
      ${laurel}
      <g transform="translate(500 58)">
        <g transform="rotate(-38)"><ellipse cx="0" cy="-20" rx="13" ry="18" fill="none" stroke="url(#gold)" stroke-width="4.5"/><rect x="-2.5" y="-2" width="5" height="30" rx="2" fill="url(#gold)"/></g>
        <g transform="rotate(38)"><ellipse cx="0" cy="-20" rx="13" ry="18" fill="none" stroke="url(#gold)" stroke-width="4.5"/><rect x="-2.5" y="-2" width="5" height="30" rx="2" fill="url(#gold)"/></g>
        ${ball(0, 18, 11, 2.5)}
      </g></g>`;
  const word = (t, y, size, ls) => `
      <text x="503" y="${y + 6}" text-anchor="middle" style="font-family:'Cinzel',serif;font-weight:700" font-size="${size}" fill="#000" opacity=".55" letter-spacing="${ls}">${t}</text>
      <text x="500" y="${y}" text-anchor="middle" style="font-family:'Cinzel',serif;font-weight:700" font-size="${size}" fill="url(#lgGold)" stroke="#3a2a10" stroke-width="3" paint-order="stroke" letter-spacing="${ls}">${t}</text>
      <text x="500" y="${y - 2}" text-anchor="middle" style="font-family:'Cinzel',serif;font-weight:700" font-size="${size}" fill="none" stroke="#fffaf0" stroke-width="1" opacity=".6" letter-spacing="${ls}">${t}</text>`;
  return svg(w, h, `
    <linearGradient id="lgGold" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fdf4d8"/><stop offset=".4" stop-color="#e8c47a"/><stop offset=".55" stop-color="#b8862f"/><stop offset=".7" stop-color="#f0d69c"/><stop offset="1" stop-color="#9a6a1c"/></linearGradient>
    ${emblem}
    ${word('GOLDEN RALLY', 210, 112, 6)}
    <line x1="250" y1="262" x2="372" y2="262" stroke="#D5A64B" stroke-width="2"/>
    <line x1="628" y1="262" x2="750" y2="262" stroke="#D5A64B" stroke-width="2"/>
    <circle cx="380" cy="262" r="4" fill="#D4E948"/><circle cx="620" cy="262" r="4" fill="#D4E948"/>
    <text x="500" y="274" text-anchor="middle" style="font-family:'Cinzel',serif;font-weight:700" font-size="34" fill="#F2E5C3" letter-spacing="12">MATCH POINT</text>`);
}

// ------------------------------------------------------------------ rally gauge
function rallyDial() {
  const s = 320, c = 160;
  const ladder = CFG.rallyLadder;
  const a0 = Math.PI * 0.78, a1 = Math.PI * 2.22;
  let seg = '';
  for (let i = 0; i < ladder.length; i++) {
    const aa = a0 + ((a1 - a0) * i) / ladder.length + .015, ab = a0 + ((a1 - a0) * (i + 1)) / ladder.length - .015;
    const t = i / (ladder.length - 1);
    const col = `hsl(${f(95 - t * 95)} 90% ${f(52 + t * 6)}%)`;
    seg += `<path d="M${pol(c, c, 136, aa)} A136,136 0 0,1 ${pol(c, c, 136, ab)} L${pol(c, c, 104, ab)} A104,104 0 0,0 ${pol(c, c, 104, aa)}Z" fill="${col}" stroke="${INK}" stroke-width="2.5"/>`;
    const [lx, ly] = pol(c, c, 120, (aa + ab) / 2);
    seg += `<text x="${lx}" y="${f(ly + 5)}" text-anchor="middle" class="lg" font-size="${ladder[i] >= 10 ? 14 : 16}" fill="#fff" stroke="${INK}" stroke-width="3.5" paint-order="stroke">×${ladder[i]}</text>`;
  }
  return svg(s, s, `
    <radialGradient id="dglass" cx=".5" cy=".3" r=".8"><stop offset="0" stop-color="#1f6b4c"/><stop offset="1" stop-color="#03130c"/></radialGradient>
    <g filter="url(#drop)"><circle cx="${c}" cy="${c}" r="154" fill="url(#gold)" ${ink(6)}/></g>
    <circle cx="${c}" cy="${c}" r="144" fill="url(#dglass)" ${ink(3)}/>
    ${seg}
    <circle cx="${c}" cy="${c}" r="98" fill="url(#dglass)" stroke="url(#gold)" stroke-width="4"/>
    <path d="M${c - 120},${c - 40} A128,128 0 0,1 ${c - 30},${c - 128}" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round" opacity=".5"/>
    <g filter="url(#drop)"><path d="M${c - 70},${c + 112} L${c + 70},${c + 112} L${c + 62},${c + 132} L${c + 70},${c + 152} L${c - 70},${c + 152} L${c - 62},${c + 132}Z" fill="url(#green)" ${ink(4)}/></g>
    <text x="${c}" y="${c + 143}" text-anchor="middle" class="lg" font-size="24" fill="url(#gold)" stroke="${INK}" stroke-width="1.5" letter-spacing="4">RALLY</text>`);
}

function dialHand() {
  return svg(40, 150, `<path d="M20,6 L29,112 L20,126 L11,112Z" fill="url(#red)" ${ink(3.5)}/>${ball(20, 124, 13, 4, 'url(#goldR)', '#fff6c8')}`);
}

function decoRacket() {
  const w = 300, h = 640, cx = 150;
  let strings = '';
  for (let i = -8; i <= 8; i++) strings += `<line x1="${cx + i * 13}" y1="20" x2="${cx + i * 13}" y2="400" stroke="#fff" stroke-width="3" opacity=".8"/>`;
  for (let j = 0; j < 30; j++) strings += `<line x1="${cx - 130}" y1="${30 + j * 13}" x2="${cx + 130}" y2="${30 + j * 13}" stroke="#fff" stroke-width="3" opacity=".8"/>`;
  return svg(w, h, `<clipPath id="rh"><ellipse cx="${cx}" cy="200" rx="112" ry="160"/></clipPath>
    <rect x="${cx - 18}" y="430" width="36" height="200" rx="10" fill="#2b2b2b" ${ink(8)}/>
    <ellipse cx="${cx}" cy="200" rx="128" ry="178" fill="url(#gold)" ${ink(10)}/>
    <ellipse cx="${cx}" cy="200" rx="112" ry="160" fill="#0b3326"/>
    <g clip-path="url(#rh)">${strings}</g>
    <ellipse cx="${cx}" cy="200" rx="112" ry="160" fill="none" ${ink(5)}/>`);
}

function mulberry(a) {
  return () => {
    a |= 0; a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function layerAssets(key, w, h) {
  const b = background(w, h, key);
  return { [`bg_${key}`]: b.sky, [`crowd_${key}`]: b.crowd, [`fore_${key}`]: b.fore, [`flags_${key}`]: b.flags };
}

const assets = {
  // reel symbols now come from the 15-symbol pack (art/import-pack.mjs)
  ...layerAssets('landscape', 1920, 1080),
  ...layerAssets('portrait', 1080, 1920),
  frame: frame(),
  logo: logo(),
  sparkle: svg(64, 64, `<circle cx="32" cy="32" r="14" fill="#f3d58f" opacity=".5" filter="url(#glowS)"/>${burst(32, 32, 5, 28, 4, '#fff8e6')}`),
  glow: svg(64, 64, `<radialGradient id="g"><stop offset="0" stop-color="#fff4d6" stop-opacity=".85"/><stop offset=".5" stop-color="#D5A64B" stop-opacity=".3"/><stop offset="1" stop-color="#D5A64B" stop-opacity="0"/></radialGradient><circle cx="32" cy="32" r="32" fill="url(#g)"/>`),
};

fs.rmSync(OUT, { recursive: true, force: true });
fs.mkdirSync(OUT, { recursive: true });
for (const [name, content] of Object.entries(assets)) fs.writeFileSync(path.join(OUT, name + '.svg'), content);
fs.writeFileSync(path.join(HERE, '..', 'src', 'assets', 'layers.json'), JSON.stringify(LAYERS, null, 1));
console.log(`wrote ${Object.keys(assets).length} SVG files to ${OUT}`);
