// GOLDEN RALLY — procedural CARTOON art generator.
// Thick ink outlines, flat colours with cel shading, hard comic shadows,
// halftone dots.  Every asset is drawn from code written for this project:
// no third-party image, no AI image service, no real person, tournament,
// trophy or brand.  Output: art/svg/*.svg -> rasterised by art/rasterize.mjs.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(HERE, 'svg');
const CFG = JSON.parse(fs.readFileSync(path.join(HERE, '..', '..', 'shared', 'game-config.json'), 'utf8'));
const TAU = Math.PI * 2;
const f = (n) => +n.toFixed(2);
const pol = (cx, cy, r, a) => [f(cx + r * Math.cos(a)), f(cy + r * Math.sin(a))];

const INK = '#1b1410';
const LW = 6;
const SKIN = { light: '#f7cfa6', mid: '#e8a97a', brown: '#b9784c', shadeL: '#e2a87f', shadeM: '#c98557', shadeB: '#94593a' };

const DEFS = `
<defs>
  <linearGradient id="gold" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff2a8"/><stop offset=".45" stop-color="#ffc83a"/><stop offset="1" stop-color="#e08a12"/></linearGradient>
  <linearGradient id="goldText" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff7c2"/><stop offset=".5" stop-color="#ffd23f"/><stop offset=".51" stop-color="#ffb21e"/><stop offset="1" stop-color="#f47d12"/></linearGradient>
  <radialGradient id="ballG" cx=".38" cy=".32" r=".8"><stop offset="0" stop-color="#fbffb0"/><stop offset=".55" stop-color="#d9ef3b"/><stop offset="1" stop-color="#a9c21c"/></radialGradient>
  <pattern id="dots" width="9" height="9" patternUnits="userSpaceOnUse"><circle cx="4.5" cy="4.5" r="1.6" fill="#000" opacity=".16"/></pattern>
  <pattern id="dotsL" width="9" height="9" patternUnits="userSpaceOnUse"><circle cx="4.5" cy="4.5" r="1.6" fill="#fff" opacity=".18"/></pattern>
  <pattern id="grain" width="6" height="6" patternUnits="userSpaceOnUse"><circle cx="1" cy="2" r=".6" fill="#000" opacity=".06"/><circle cx="4" cy="5" r=".5" fill="#fff" opacity=".07"/></pattern>
  <filter id="comic" x="-20%" y="-20%" width="150%" height="150%">
    <feOffset dx="5" dy="6" in="SourceAlpha" result="o"/><feFlood flood-color="#000" flood-opacity=".38"/><feComposite in2="o" operator="in" result="s"/>
    <feMerge><feMergeNode in="s"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
</defs>`;

const svg = (w, h, body) => `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">
<style>.lg{font-family:'Luckiest Guy',sans-serif}.li{font-family:'Lilita One',sans-serif}</style>${DEFS}${body}</svg>`;

const ink = (w = LW) => `stroke="${INK}" stroke-width="${w}" stroke-linejoin="round" stroke-linecap="round"`;

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
    const [x0, y0] = pol(cx, cy, r, a0), [x1, y1] = pol(cx, cy, r, a1);
    s += `<path d="M${cx},${cy}L${x0},${y0}L${x1},${y1}Z" fill="${color}" opacity="${op}"/>`;
  }
  return s;
}

function ball(cx, cy, r, w = LW) {
  return `<circle cx="${cx}" cy="${cy}" r="${r}" fill="url(#ballG)" ${ink(w)}/>
  <path d="M${f(cx - r * .92)},${f(cy - r * .35)} C${f(cx - r * .25)},${f(cy - r * .25)} ${f(cx - r * .2)},${f(cy + r * .8)} ${f(cx - r * .45)},${f(cy + r * .88)}" fill="none" stroke="#fffde8" stroke-width="${f(r * .14)}" stroke-linecap="round"/>
  <path d="M${f(cx + r * .45)},${f(cy - r * .88)} C${f(cx + r * .2)},${f(cy - r * .8)} ${f(cx + r * .25)},${f(cy + r * .25)} ${f(cx + r * .92)},${f(cy + r * .35)}" fill="none" stroke="#fffde8" stroke-width="${f(r * .14)}" stroke-linecap="round"/>
  <ellipse cx="${f(cx - r * .35)}" cy="${f(cy - r * .4)}" rx="${f(r * .25)}" ry="${f(r * .14)}" fill="#fff" opacity=".7" transform="rotate(-30 ${f(cx - r * .35)} ${f(cy - r * .4)})"/>`;
}

function eye(cx, cy, r, look = [0, 0], lid = 0, lidColor = SKIN.light) {
  const px = cx + look[0] * r * .35, py = cy + look[1] * r * .35;
  let s = `<ellipse cx="${cx}" cy="${cy}" rx="${f(r * .78)}" ry="${r}" fill="#fff" ${ink(4)}/>
  <circle cx="${f(px)}" cy="${f(py + r * .1)}" r="${f(r * .48)}" fill="${INK}"/>
  <circle cx="${f(px - r * .16)}" cy="${f(py - r * .12)}" r="${f(r * .17)}" fill="#fff"/>`;
  if (lid > 0) {
    const ly = cy - r + lid * 2 * r;
    s += `<path d="M${f(cx - r * .85)},${f(cy - r * .1)} Q${cx},${f(cy - r * 1.5)} ${f(cx + r * .85)},${f(cy - r * .1)} L${f(cx + r * .85)},${f(ly)} Q${cx},${f(ly - r * .15)} ${f(cx - r * .85)},${f(ly)}Z" fill="${lidColor}" ${ink(4)}/>`;
  }
  return s;
}

// character card: the head pops out above the top edge
function card(id, c1, c2, body) {
  return `
  <radialGradient id="bg${id}" cx=".5" cy=".4" r=".75"><stop offset="0" stop-color="${c1}"/><stop offset="1" stop-color="${c2}"/></radialGradient>
  <clipPath id="cc${id}"><rect x="16" y="34" width="224" height="206" rx="30"/></clipPath>
  <clipPath id="ch${id}"><rect x="16" y="-80" width="224" height="320" rx="30"/></clipPath>
  <clipPath id="bot${id}"><rect x="0" y="200" width="256" height="60"/></clipPath>
  <g filter="url(#comic)">
    <rect x="16" y="34" width="224" height="206" rx="30" fill="url(#bg${id})"/>
    <g clip-path="url(#cc${id})">${rays(128, 140, 220, 16, '#fff', .1)}<rect x="16" y="34" width="224" height="206" fill="url(#dotsL)"/></g>
    <rect x="16" y="34" width="224" height="206" rx="30" fill="none" ${ink(LW + 1)}/>
  </g>
  <g clip-path="url(#ch${id})">${body}</g>
  <rect x="16" y="34" width="224" height="206" rx="30" fill="none" stroke="${INK}" stroke-width="${LW + 1}" clip-path="url(#bot${id})"/>`;
}

const torso = (fill) => `<path d="M30,262 C32,214 62,196 100,190 L156,190 C194,196 224,214 226,262Z" fill="${fill}" ${ink()}/>`;

function president() {
  const body = `
    ${torso('#26346a')}
    <path d="M100,190 L128,234 L156,190Z" fill="#fff" ${ink(4)}/>
    <path d="M110,204 L128,212 L146,204 L146,224 L128,216 L110,224Z" fill="#d93b3b" ${ink(4)}/>
    <path d="M172,212 h20 v14 q-10,10 -20,0Z" fill="url(#gold)" ${ink(3)}/>
    <rect x="110" y="166" width="36" height="30" fill="${SKIN.light}" ${ink(4)}/>
    <ellipse cx="62" cy="116" rx="13" ry="17" fill="${SKIN.light}" ${ink(5)}/>
    <ellipse cx="194" cy="116" rx="13" ry="17" fill="${SKIN.light}" ${ink(5)}/>
    <ellipse cx="128" cy="104" rx="64" ry="70" fill="${SKIN.light}" ${ink()}/>
    <path d="M78,150 Q128,186 178,150 Q170,176 128,178 Q86,176 78,150Z" fill="${SKIN.shadeL}" opacity=".7"/>
    <path d="M66,98 q-14,-24 4,-38 q-2,18 16,22 q-10,10 -20,16Z" fill="#ececf2" ${ink(4)}/>
    <path d="M190,98 q14,-24 -4,-38 q2,18 -16,22 q10,10 20,16Z" fill="#ececf2" ${ink(4)}/>
    <ellipse cx="104" cy="56" rx="22" ry="11" fill="#fff" opacity=".75" transform="rotate(-20 104 56)"/>
    <path d="M118,38 q22,-18 34,4 q-14,-6 -22,4" fill="none" ${ink(4)}/>
    <path d="M82,80 q18,-18 36,-6" fill="none" stroke="#d2d2da" stroke-width="12" stroke-linecap="round"/>
    <path d="M140,66 q18,-14 36,0" fill="none" stroke="#d2d2da" stroke-width="12" stroke-linecap="round"/>
    <path d="M82,80 q18,-18 36,-6 M140,66 q18,-14 36,0" fill="none" stroke="${INK}" stroke-width="2.5" opacity=".6"/>
    ${eye(102, 100, 13, [.4, .2], .55)}
    ${eye(156, 98, 15, [-.3, .1])}
    <circle cx="156" cy="98" r="21" fill="#bfe6ff" fill-opacity=".35" stroke="#ffc83a" stroke-width="6"/>
    <circle cx="156" cy="98" r="21" fill="none" stroke="${INK}" stroke-width="2.5"/>
    <path d="M176,106 C192,138 186,170 176,196" fill="none" stroke="#ffc83a" stroke-width="3" stroke-dasharray="4 3"/>
    <ellipse cx="128" cy="130" rx="17" ry="14" fill="#e8665a" ${ink(5)}/>
    <ellipse cx="122" cy="125" rx="5" ry="3" fill="#fff" opacity=".7"/>
    <path d="M128,140 C108,132 86,140 74,130 C64,124 58,132 66,140 C54,140 52,128 62,120 C80,150 108,150 128,146 C148,150 176,150 194,120 C204,128 202,140 190,140 C198,132 192,124 182,130 C170,140 148,132 128,140Z" fill="#f4f4f8" ${ink(5)}/>
    <path d="M114,160 q14,8 28,-2" fill="none" ${ink(4)}/>
    <circle cx="86" cy="136" r="8" fill="#ff8c8c" opacity=".45"/>`;
  return svg(256, 256, card('p', '#c0485a', '#5c1424', body));
}

function champion() {
  let strings = '';
  for (let i = -4; i <= 4; i++) strings += `<line x1="${i * 9}" y1="-60" x2="${i * 9}" y2="60" stroke="#fff" stroke-width="2"/>`;
  for (let j = -5; j <= 5; j++) strings += `<line x1="-46" y1="${j * 9}" x2="46" y2="${j * 9}" stroke="#fff" stroke-width="2"/>`;
  const body = `
    <g transform="translate(198 90) rotate(28)">
      <clipPath id="rhc"><ellipse cx="0" cy="0" rx="34" ry="46"/></clipPath>
      <rect x="-6" y="44" width="12" height="80" rx="5" fill="#2b2b2b" ${ink(4)}/>
      <ellipse cx="0" cy="0" rx="42" ry="54" fill="#d93b3b" ${ink()}/>
      <ellipse cx="0" cy="0" rx="34" ry="46" fill="#1f5e33"/>
      <g clip-path="url(#rhc)">${strings}</g>
      <ellipse cx="0" cy="0" rx="34" ry="46" fill="none" ${ink(3)}/>
    </g>
    <path d="M70,52 C40,36 18,64 30,92 C22,116 38,134 60,126 C50,100 60,76 80,64Z" fill="#2a1a12" ${ink(5)}/>
    ${torso('#ffffff')}
    <path d="M100,190 L128,214 L156,190" fill="none" stroke="#2f9a4a" stroke-width="9"/>
    <path d="M100,190 L128,214 L156,190" fill="none" ${ink(3)}/>
    <path d="M40,232 h176" stroke="#2f9a4a" stroke-width="7"/>
    <rect x="110" y="164" width="36" height="32" fill="${SKIN.brown}" ${ink(4)}/>
    <ellipse cx="128" cy="108" rx="60" ry="66" fill="${SKIN.brown}" ${ink()}/>
    <path d="M78,150 Q128,186 178,150 Q170,174 128,176 Q86,174 78,150Z" fill="${SKIN.shadeB}" opacity=".6"/>
    <path d="M68,84 C66,40 100,28 128,30 C160,28 192,44 188,86 C176,64 150,56 128,60 C102,58 82,66 68,84Z" fill="#2a1a12" ${ink(5)}/>
    <path d="M68,78 Q128,54 190,78 L190,94 Q128,70 68,94Z" fill="#d93b3b" ${ink(4)}/>
    <path d="M70,86 Q128,63 188,86" fill="none" stroke="#fff" stroke-width="3"/>
    <path d="M88,94 l26,8 M168,94 l-26,8" ${ink(7)}/>
    ${eye(104, 114, 12, [.5, 0], 0, SKIN.brown)}
    ${eye(152, 114, 12, [.5, 0], 0, SKIN.brown)}
    <path d="M124,120 q6,16 -2,20 q6,2 10,-2" fill="none" ${ink(4)}/>
    <path d="M100,146 Q128,172 158,144 Q156,162 128,166 Q104,164 100,146Z" fill="#fff" ${ink(4)}/>
    <path d="M110,149 v9 M120,152 v11 M130,153 v11 M140,152 v11 M150,148 v9" stroke="${INK}" stroke-width="1.5"/>
    <path d="M180,122 q9,11 0,17 q-9,-6 0,-17Z" fill="#7cd3ff" ${ink(3)}/>
    ${burst(176, 152, 4, 12, 4, '#fff', ink(2))}`;
  return svg(256, 256, card('c', '#5fc06e', '#1f5e33', body));
}

function umpire() {
  const body = `
    ${torso('#1f5e33')}
    <path d="M100,190 L128,228 L156,190Z" fill="#fff" ${ink(4)}/>
    <path d="M122,204 h12 l4,32 l-10,10 l-10,-10Z" fill="#26346a" ${ink(3)}/>
    <rect x="112" y="166" width="32" height="30" fill="${SKIN.mid}" ${ink(4)}/>
    <ellipse cx="72" cy="122" rx="11" ry="15" fill="${SKIN.mid}" ${ink(5)}/>
    <ellipse cx="128" cy="112" rx="54" ry="74" fill="${SKIN.mid}" ${ink()}/>
    <path d="M80,160 Q128,198 176,160 Q166,182 128,186 Q90,182 80,160Z" fill="${SKIN.shadeM}" opacity=".7"/>
    <path d="M72,60 C76,20 180,20 184,60Z" fill="#ffffff" ${ink(5)}/>
    <path d="M62,58 h132 l20,12 h-152Z" fill="#26346a" ${ink(5)}/>
    <path d="M84,90 l30,10 M172,90 l-30,10" ${ink(8)}/>
    <circle cx="106" cy="110" r="17" fill="#fff" ${ink(5)}/>
    <circle cx="152" cy="110" r="17" fill="#fff" ${ink(5)}/>
    <line x1="123" y1="110" x2="135" y2="110" ${ink(5)}/>
    <circle cx="108" cy="113" r="5" fill="${INK}"/><circle cx="150" cy="113" r="5" fill="${INK}"/>
    <path d="M124,122 q-4,16 6,18" fill="none" ${ink(4)}/>
    <ellipse cx="128" cy="160" rx="22" ry="18" fill="#7a1f1f" ${ink(5)}/>
    <path d="M112,168 q16,-10 32,0 q-16,10 -32,0Z" fill="#e8665a"/>
    <path d="M112,151 h32" stroke="#fff" stroke-width="5"/>
    <path d="M58,150 l-14,6 M56,166 l-16,0 M198,150 l14,6 M200,166 l16,0" ${ink(4)}/>
    <g filter="url(#comic)">
      <path d="M140,4 h80 a12,12 0 0 1 12,12 v30 a12,12 0 0 1 -12,12 h-48 l-20,18 l4,-18 h-16 a12,12 0 0 1 -12,-12 v-30 a12,12 0 0 1 12,-12Z" fill="#fff" ${ink(5)}/>
    </g>
    <text x="182" y="45" text-anchor="middle" class="lg" font-size="30" fill="#d93b3b" stroke="${INK}" stroke-width="2">OUT!</text>`;
  return svg(256, 256, card('u', '#4f73c9', '#182650', body));
}

function ballKid() {
  const body = `
    ${torso('#2f9a4a')}
    <path d="M30,232 h196" stroke="#fff" stroke-width="8"/>
    <rect x="112" y="168" width="32" height="28" fill="${SKIN.light}" ${ink(4)}/>
    <ellipse cx="62" cy="122" rx="16" ry="20" fill="${SKIN.light}" ${ink(5)}/>
    <ellipse cx="190" cy="122" rx="16" ry="20" fill="${SKIN.light}" ${ink(5)}/>
    <circle cx="126" cy="116" r="62" fill="${SKIN.light}" ${ink()}/>
    <path d="M70,140 Q126,190 182,140 Q172,172 126,176 Q80,172 70,140Z" fill="${SKIN.shadeL}" opacity=".6"/>
    <path d="M68,92 C66,46 104,34 128,36 C160,34 190,52 186,92 C170,74 150,70 128,70 C106,70 84,76 68,92Z" fill="#2f9a4a" ${ink(5)}/>
    <path d="M60,86 C44,86 30,94 28,104 C46,102 60,100 72,96Z" fill="#2f9a4a" ${ink(5)}/>
    <path d="M150,72 q14,-14 10,6 q12,-6 6,10" fill="#e8742a" ${ink(4)}/>
    <path d="M88,98 q12,-12 26,-4 M140,94 q14,-8 26,4" fill="none" ${ink(6)}/>
    ${eye(104, 118, 16, [.25, -.1])}
    ${eye(152, 118, 16, [.25, -.1])}
    ${[[86, 140], [94, 146], [80, 148], [162, 140], [170, 146], [158, 148]].map(([x, y]) => `<circle cx="${x}" cy="${y}" r="2.6" fill="#c9733f"/>`).join('')}
    <path d="M96,152 Q126,190 160,150 Q156,176 126,178 Q100,176 96,152Z" fill="#7a1f1f" ${ink(5)}/>
    <path d="M100,154 Q126,166 156,152 L154,160 Q126,170 102,162Z" fill="#fff"/>
    <rect x="124" y="155" width="9" height="10" fill="#7a1f1f"/>
    <circle cx="206" cy="180" r="20" fill="${SKIN.light}" ${ink(5)}/>
    ${ball(206, 152, 22)}`;
  return svg(256, 256, card('k', '#f4934f', '#a8461c', body));
}

function bulldog() {
  const fur = '#d8a46a';
  const body = `
    <path d="M34,262 C36,216 70,200 128,200 C186,200 220,216 222,262Z" fill="${fur}" ${ink()}/>
    <path d="M60,214 Q128,236 196,214 L200,232 Q128,254 56,232Z" fill="#d93b3b" ${ink(5)}/>
    <circle cx="128" cy="242" r="11" fill="url(#gold)" ${ink(4)}/>
    <ellipse cx="128" cy="124" rx="86" ry="74" fill="${fur}" ${ink()}/>
    <path d="M70,66 L28,72 Q34,100 58,104 Q56,84 76,76Z" fill="#7a4b2a" ${ink(5)}/>
    <path d="M186,66 L228,72 Q222,100 198,104 Q200,84 180,76Z" fill="#7a4b2a" ${ink(5)}/>
    <path d="M48,150 Q40,184 70,196 M208,150 Q216,184 186,196" fill="none" ${ink(5)}/>
    <path d="M66,66 Q128,40 190,66 L192,84 Q128,58 64,84Z" fill="#fff" ${ink(4)}/>
    <path d="M66,73 Q128,49 191,73" fill="none" stroke="#d93b3b" stroke-width="5"/>
    <path d="M98,98 q12,-6 22,2 M136,100 q10,-8 22,-2" fill="none" stroke="#9c6a3c" stroke-width="4" stroke-linecap="round"/>
    <path d="M80,108 l24,8 M176,108 l-24,8" ${ink(7)}/>
    ${eye(100, 124, 13, [0, .3], .5, fur)}
    ${eye(156, 124, 13, [0, .3], .5, fur)}
    <path d="M70,150 C70,186 104,196 128,192 C152,196 186,186 186,150 C170,166 150,160 128,160 C106,160 86,166 70,150Z" fill="#f3e6d2" ${ink(5)}/>
    <ellipse cx="128" cy="146" rx="24" ry="15" fill="${INK}"/>
    <ellipse cx="120" cy="141" rx="7" ry="4" fill="#fff" opacity=".6"/>
    <path d="M128,160 v12" ${ink(4)}/>
    <path d="M92,182 Q128,206 164,182" fill="#7a1f1f" ${ink(5)}/>
    <path d="M104,186 l6,-14 l6,16Z M140,188 l6,-16 l6,14Z" fill="#fff" ${ink(2.5)}/>
    ${ball(196, 194, 24)}
    <path d="M84,196 q-4,14 2,20 q6,-6 -2,-20Z" fill="#9fe1ff" ${ink(3)}/>`;
  return svg(256, 256, card('d', '#86c9f0', '#2f78b0', body));
}

function wild() {
  let strings = '';
  for (let i = -5; i <= 5; i++) strings += `<line x1="${i * 8}" y1="-70" x2="${i * 8}" y2="60" stroke="#fff" stroke-width="2.2"/>`;
  for (let j = -7; j <= 6; j++) strings += `<line x1="-50" y1="${j * 9}" x2="50" y2="${j * 9}" stroke="#fff" stroke-width="2.2"/>`;
  let speed = '';
  for (let i = 0; i < 5; i++) speed += `<line x1="${22 + i * 3}" y1="${70 + i * 11}" x2="${62 + i * 4}" y2="${70 + i * 11}" stroke="#fff" stroke-width="5" stroke-linecap="round"/>`;
  return svg(256, 256, `
    <g filter="url(#comic)">
      ${burst(128, 112, 80, 118, 14, '#ffd23f', ink())}
      ${burst(128, 112, 58, 88, 14, '#ff8a1e')}
    </g>
    <g transform="translate(152 100) rotate(-38)">
      <clipPath id="wh"><ellipse cx="0" cy="-10" rx="40" ry="54"/></clipPath>
      <rect x="-8" y="44" width="16" height="78" rx="6" fill="#2b2b2b" ${ink(5)}/>
      <ellipse cx="0" cy="-10" rx="48" ry="62" fill="#d93b3b" ${ink()}/>
      <ellipse cx="0" cy="-10" rx="40" ry="54" fill="#26346a"/>
      <g clip-path="url(#wh)">${strings}</g>
      <ellipse cx="0" cy="-10" rx="40" ry="54" fill="none" ${ink(3)}/>
    </g>
    ${speed}
    ${ball(84, 92, 26)}
    ${burst(60, 60, 6, 17, 4, '#fff', ink(2.5))}
    <g filter="url(#comic)"><path d="M28,184 L228,170 L234,224 L22,234Z" fill="#d93b3b" ${ink()}/></g>
    <text x="128" y="222" text-anchor="middle" class="lg" font-size="46" fill="url(#goldText)" stroke="${INK}" stroke-width="3" letter-spacing="2" transform="rotate(-3 128 208)">WILD</text>`);
}

function scatter() {
  let stars = '';
  for (const [x, y, r] of [[40, 52, 13], [216, 40, 11], [224, 144, 9], [30, 150, 8]]) stars += burst(x, y, r * .35, r, 4, '#fff', ink(2));
  return svg(256, 256, `
    <circle cx="128" cy="110" r="110" fill="#7cd3ff" opacity=".4"/>
    ${rays(128, 110, 130, 18, '#fff', .28)}
    <g filter="url(#comic)">
      <path d="M78,46 C40,44 36,96 84,108 M178,46 C216,44 220,96 172,108" fill="none" stroke="${INK}" stroke-width="16" stroke-linecap="round"/>
      <path d="M78,46 C40,44 36,96 84,108 M178,46 C216,44 220,96 172,108" fill="none" stroke="#ffc83a" stroke-width="7" stroke-linecap="round"/>
      <path d="M70,34 H186 C186,104 162,134 128,140 C94,134 70,104 70,34Z" fill="url(#gold)" ${ink()}/>
      <path d="M86,44 C86,92 98,118 118,128" fill="none" stroke="#fff" stroke-width="7" stroke-linecap="round" opacity=".8"/>
      <rect x="116" y="138" width="24" height="26" fill="url(#gold)" ${ink(5)}/>
      <path d="M86,164 H170 L178,188 H78Z" fill="url(#gold)" ${ink()}/>
    </g>
    ${ball(128, 78, 20)}
    ${stars}
    <g filter="url(#comic)"><path d="M22,196 L234,196 L224,214 L234,232 L22,232 L32,214Z" fill="#2f6fd0" ${ink()}/></g>
    <text x="128" y="227" text-anchor="middle" class="lg" font-size="34" fill="#fff" stroke="${INK}" stroke-width="2.5" letter-spacing="3">BONUS</text>`);
}

function plate(label, color, tilt, size) {
  return svg(256, 256, `
    <g transform="rotate(${tilt} 128 132)">
      <path d="M128,22 L84,64 M128,22 L172,64" stroke="${INK}" stroke-width="4"/>
      <circle cx="128" cy="22" r="7" fill="#9a9a9a" ${ink(3)}/>
      <g filter="url(#comic)"><rect x="44" y="58" width="168" height="168" rx="18" fill="#fff3d6" ${ink()}/></g>
      <rect x="44" y="58" width="168" height="168" rx="18" fill="url(#grain)"/>
      <rect x="56" y="70" width="144" height="144" rx="12" fill="none" stroke="${color}" stroke-width="5" opacity=".55"/>
      <text x="132" y="${f(142 + size * .38)}" text-anchor="middle" class="lg" font-size="${size}" fill="${INK}" opacity=".3">${label}</text>
      <text x="128" y="${f(139 + size * .36)}" text-anchor="middle" class="lg" font-size="${size}" fill="${color}" stroke="${INK}" stroke-width="7" stroke-linejoin="round" paint-order="stroke">${label}</text>
    </g>`);
}

function cloud(x, y, s) {
  return `<g transform="translate(${x} ${y}) scale(${s})"><path d="M0,40 C-10,10 30,-6 50,12 C60,-14 110,-10 112,20 C140,14 150,44 128,52 L4,54 C-12,54 -12,42 0,40Z" fill="#fff" ${ink(5)}/></g>`;
}

function background(w, h) {
  const horizon = h * (w > h ? 0.5 : 0.42);
  const cols = ['#d93b3b', '#ffd23f', '#2f9a4a', '#2f6fd0', '#fff'];
  const nf = Math.ceil(w / 60);
  const sag = (i) => Math.sin((i / nf) * Math.PI) * 40;
  let flags = '';
  for (let i = 0; i < nf; i++) flags += `<path d="M${i * 60},${f(30 + sag(i))} L${(i + 1) * 60},${f(30 + sag(i + 1))} L${i * 60 + 30},${f(80 + sag(i))}Z" fill="${cols[i % 5]}" ${ink(3)}/>`;
  let crowd = '';
  const rnd = mulberry(5);
  for (let row = 0; row < 4; row++) {
    for (let i = 0; i < w / 34 + 1; i++) {
      const x = i * 34 + (row % 2) * 17 + rnd() * 6;
      const y = horizon - 34 - row * 26;
      const c = ['#f4c7a1', '#c98557', '#8d5a3b', '#f6d7b0'][Math.floor(rnd() * 4)];
      crowd += `<rect x="${f(x - 12)}" y="${f(y + 6)}" width="24" height="26" rx="8" fill="${cols[Math.floor(rnd() * 5)]}" stroke="${INK}" stroke-width="2.5"/><circle cx="${f(x)}" cy="${f(y)}" r="10" fill="${c}" stroke="${INK}" stroke-width="2.5"/>`;
    }
  }
  const cx = w / 2, top = horizon + 30, bot = h + 40;
  const tw = w * 0.55, bw = w * 1.7;
  const at = (u, v) => [f(cx + (u * (tw + (bw - tw) * v)) / 2), f(top + (bot - top) * v)];
  const L = (a, b) => `<line x1="${a[0]}" y1="${a[1]}" x2="${b[0]}" y2="${b[1]}" stroke="#fff" stroke-width="7" opacity=".9"/>`;
  let court = `<path d="M${at(-1.15, 0)} L${at(1.15, 0)} L${at(1.15, 1)} L${at(-1.15, 1)}Z" fill="#d9733a"/>`;
  for (const u of [-1, -0.78, 0.78, 1]) court += L(at(u, 0), at(u, 1));
  for (const v of [0, 0.45]) court += L(at(-1, v), at(1, v));
  court += L(at(0, 0.45), at(0, 1));
  const hills = Array.from({ length: 24 }, (_, i) => `Q${f(((i + .5) * w) / 24)},${f(horizon - 230 - (i % 3) * 22)} ${f(((i + 1) * w) / 24)},${f(horizon - 170)}`).join(' ');
  return svg(w, h, `
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3f9fe0"/><stop offset=".7" stop-color="#9fdcf6"/><stop offset="1" stop-color="#ffe9b0"/></linearGradient>
    <rect width="${w}" height="${h}" fill="url(#sky)"/>
    ${rays(w / 2, horizon, Math.max(w, h), 24, '#fff', .08)}
    ${cloud(w * .06, h * .1, 1.3)}${cloud(w * .74, h * .06, 1.0)}${cloud(w * .46, h * .17, .8)}
    <path d="M0,${f(horizon - 170)} ${hills} V${horizon} H0Z" fill="#3e8f4e" ${ink(5)}/>
    <rect x="-10" y="${horizon - 140}" width="${w + 20}" height="140" fill="#2b6b45" ${ink(5)}/>
    ${crowd}
    <rect x="-10" y="${horizon - 20}" width="${w + 20}" height="28" fill="#1f5e33" ${ink(5)}/>
    <rect x="0" y="${horizon + 8}" width="${w}" height="${h}" fill="#3e9b4f"/>
    ${court}
    <rect width="${w}" height="${h}" fill="url(#dots)" opacity=".45"/>
    ${flags}
    <path d="M0,30 ${Array.from({ length: nf }, (_, i) => `L${(i + 1) * 60},${f(30 + sag(i + 1))}`).join(' ')}" fill="none" ${ink(3)}/>`);
}

export const CELL = 170;
function scoreboard() {
  const iw = 6 * CELL, ih = 5 * CELL, m = 46;
  const w = iw + 2 * m, h = ih + 2 * m;
  let grain = '';
  const rnd = mulberry(3);
  for (let i = 0; i < 40; i++) {
    const y = rnd() * h;
    grain += `<path d="M0,${f(y)} q${w / 4},${f(rnd() * 10 - 5)} ${w / 2},0 t${w / 2},0" fill="none" stroke="#5a3418" stroke-width="2" opacity=".35"/>`;
  }
  let nails = '';
  for (const [x, y] of [[22, 22], [w - 22, 22], [22, h - 22], [w - 22, h - 22], [w / 2, 22], [w / 2, h - 22], [22, h / 2], [w - 22, h / 2]]) {
    nails += `<circle cx="${x}" cy="${y}" r="8" fill="#c9c9c9" ${ink(3)}/><circle cx="${x - 2}" cy="${y - 2}" r="2.5" fill="#fff"/>`;
  }
  let chalk = '';
  for (let r = 1; r < 6; r++) chalk += `<line x1="${m + r * CELL}" y1="${m + 10}" x2="${m + r * CELL}" y2="${m + ih - 10}" stroke="#e8f5e0" stroke-width="3" stroke-dasharray="14 8" opacity=".35"/>`;
  for (let r = 1; r < 5; r++) chalk += `<line x1="${m + 10}" y1="${m + r * CELL}" x2="${m + iw - 10}" y2="${m + r * CELL}" stroke="#e8f5e0" stroke-width="2" stroke-dasharray="6 10" opacity=".18"/>`;
  return svg(w, h, `
    <linearGradient id="wood" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#b9763e"/><stop offset="1" stop-color="#8a5228"/></linearGradient>
    <rect x="4" y="4" width="${w - 8}" height="${h - 8}" rx="22" fill="url(#wood)" ${ink(8)}/>
    ${grain}
    <rect x="${m - 10}" y="${m - 10}" width="${iw + 20}" height="${ih + 20}" rx="10" fill="#6b3f1e" ${ink(5)}/>
    <rect x="${m}" y="${m}" width="${iw}" height="${ih}" rx="6" fill="#1f5e3a"/>
    <rect x="${m}" y="${m}" width="${iw}" height="${ih}" rx="6" fill="url(#dotsL)" opacity=".5"/>
    <rect x="${m}" y="${m}" width="${iw}" height="${ih}" rx="6" fill="none" ${ink(5)}/>
    ${chalk}${nails}`);
}

function logo() {
  const w = 1000, h = 330;
  let speed = '';
  for (let i = 0; i < 4; i++) speed += `<line x1="${770 + i * 8}" y1="${150 + i * 18}" x2="${840 + i * 10}" y2="${150 + i * 18}" stroke="#fff" stroke-width="8" stroke-linecap="round" ${''}/>`;
  return svg(w, h, `
    <g transform="rotate(-4 500 165)">
      <text x="508" y="158" text-anchor="middle" class="lg" font-size="136" fill="${INK}" stroke="${INK}" stroke-width="26" stroke-linejoin="round" letter-spacing="6">GOLDEN</text>
      <text x="500" y="148" text-anchor="middle" class="lg" font-size="136" fill="url(#goldText)" stroke="${INK}" stroke-width="14" stroke-linejoin="round" paint-order="stroke" letter-spacing="6">GOLDEN</text>
      <text x="458" y="300" text-anchor="middle" class="lg" font-size="150" fill="${INK}" stroke="${INK}" stroke-width="26" stroke-linejoin="round" letter-spacing="10">RALLY</text>
      <text x="450" y="290" text-anchor="middle" class="lg" font-size="150" fill="#d9f04a" stroke="${INK}" stroke-width="14" stroke-linejoin="round" paint-order="stroke" letter-spacing="10">RALLY</text>
      ${speed}
      ${ball(905, 200, 54, 9)}
    </g>`);
}

function rallyDial() {
  const s = 320, c = 160;
  const ladder = CFG.rallyLadder;
  const a0 = Math.PI * 0.78, a1 = Math.PI * 2.22;
  const cols = ['#5fc06e', '#9fd84a', '#cfe63f', '#ffd23f', '#ffb21e', '#ff8a1e', '#f4642a', '#e8452e', '#d93b3b', '#c22a5a', '#9b2fb0'];
  let seg = '';
  for (let i = 0; i < ladder.length; i++) {
    const aa = a0 + ((a1 - a0) * i) / ladder.length, ab = a0 + ((a1 - a0) * (i + 1)) / ladder.length;
    const [x1, y1] = pol(c, c, 138, aa), [x2, y2] = pol(c, c, 138, ab), [x3, y3] = pol(c, c, 100, ab), [x4, y4] = pol(c, c, 100, aa);
    seg += `<path d="M${x1},${y1} A138,138 0 0,1 ${x2},${y2} L${x3},${y3} A100,100 0 0,0 ${x4},${y4}Z" fill="${cols[i % cols.length]}" stroke="${INK}" stroke-width="3"/>`;
    const [lx, ly] = pol(c, c, 119, (aa + ab) / 2);
    seg += `<text x="${lx}" y="${f(ly + 6)}" text-anchor="middle" class="lg" font-size="${ladder[i] >= 10 ? 15 : 17}" fill="#fff" stroke="${INK}" stroke-width="4" paint-order="stroke">×${ladder[i]}</text>`;
  }
  return svg(s, s, `
    <g filter="url(#comic)"><circle cx="${c}" cy="${c}" r="152" fill="#fff3d6" ${ink(8)}/></g>
    ${seg}
    <circle cx="${c}" cy="${c}" r="96" fill="#fff3d6" stroke="${INK}" stroke-width="3"/>
    <circle cx="${c}" cy="${c}" r="96" fill="url(#grain)"/>
    <text x="${c}" y="${c + 128}" text-anchor="middle" class="lg" font-size="30" fill="#d93b3b" stroke="${INK}" stroke-width="6" stroke-linejoin="round" paint-order="stroke" letter-spacing="3">RALLY</text>`);
}

function dialHand() {
  return svg(40, 150, `<path d="M20,6 L30,112 L20,126 L10,112Z" fill="#d93b3b" ${ink(4)}/>${ball(20, 124, 13, 4)}`);
}

function decoRacket() {
  const w = 300, h = 640, cx = 150;
  let strings = '';
  for (let i = -8; i <= 8; i++) strings += `<line x1="${cx + i * 13}" y1="20" x2="${cx + i * 13}" y2="400" stroke="#fff" stroke-width="3"/>`;
  for (let j = 0; j < 30; j++) strings += `<line x1="${cx - 130}" y1="${30 + j * 13}" x2="${cx + 130}" y2="${30 + j * 13}" stroke="#fff" stroke-width="3"/>`;
  return svg(w, h, `
    <clipPath id="rh"><ellipse cx="${cx}" cy="200" rx="112" ry="160"/></clipPath>
    <rect x="${cx - 18}" y="430" width="36" height="200" rx="10" fill="#2b2b2b" ${ink(8)}/>
    <ellipse cx="${cx}" cy="200" rx="128" ry="178" fill="#d93b3b" ${ink(10)}/>
    <ellipse cx="${cx}" cy="200" rx="112" ry="160" fill="#26346a"/>
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

const assets = {
  sym_W: wild(),
  sym_S: scatter(),
  sym_H1: president(),
  sym_H2: champion(),
  sym_H3: umpire(),
  sym_H4: ballKid(),
  sym_H5: bulldog(),
  sym_L1: plate('AD', '#d93b3b', -5, 92),
  sym_L2: plate('40', '#2f9a4a', 4, 108),
  sym_L3: plate('30', '#2f6fd0', -3, 108),
  sym_L4: plate('15', '#f08a12', 5, 108),
  sym_L5: plate('0', '#9b2fb0', -4, 124),
  bg_landscape: background(1920, 1080),
  bg_portrait: background(1080, 1920),
  frame: scoreboard(),
  logo: logo(),
  dial: rallyDial(),
  dial_hand: dialHand(),
  deco_1: svg(320, 320, ball(160, 160, 150, 10)),
  deco_2: decoRacket(),
  deco_3: svg(160, 160, ball(80, 80, 72, 8)),
  sparkle: svg(64, 64, burst(32, 32, 9, 28, 4, '#fff6a0', ink(3))),
  glow: svg(64, 64, `<radialGradient id="g"><stop offset="0" stop-color="#fff9c0" stop-opacity=".9"/><stop offset=".5" stop-color="#ffd23f" stop-opacity=".35"/><stop offset="1" stop-color="#ffd23f" stop-opacity="0"/></radialGradient><circle cx="32" cy="32" r="32" fill="url(#g)"/>`),
  coin: svg(96, 96, ball(48, 48, 40, 5)),
};

fs.rmSync(OUT, { recursive: true, force: true });
fs.mkdirSync(OUT, { recursive: true });
for (const [name, content] of Object.entries(assets)) fs.writeFileSync(path.join(OUT, name + '.svg'), content);
console.log(`wrote ${Object.keys(assets).length} SVG files to ${OUT}`);
