// Imports the 11-symbol colour pack (art/pack-v5/png) into the game (v5).
// * Maps each pack file onto an engine symbol id (mapping documented in
//   docs/GAME_MODES.md; the maths define the ids, not the file names).
// * Each 512x512 sprite is trimmed to its artwork, scaled so its largest side
//   is the same for every symbol (Wild/Scatter slightly bigger) and centred in
//   a 300x300 transparent square: uniform size, distinct silhouettes, no frame.
// * Writes WebP (primary) + PNG (fallback).  Originals stay in art/pack-v5.
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.dirname(HERE);
const SRC = path.join(HERE, 'pack-v5', 'png');
const OUT = path.join(ROOT, 'src', 'assets', 'img');
const FALLBACK = path.join(ROOT, 'src', 'assets', 'img-png');

// engine symbol id -> pack file (also exported as "art" in math/rally_math/config.py)
export const SYMBOL_MAP = {
  W: 'wild_magenta',
  S: 'scatter_blue',
  H1: 'ace_mascot',
  H2: 'gold_trophy',
  H3: 'tennis_bag',
  H4: 'tennis_racket',
  L1: 'tennis_ball',
  L2: 'tennis_shoe',
  L3: 'tennis_cap',
  L4: 'water_bottle',
  L5: 'red_wristband',
};
const BIG = new Set(['W', 'S']);

function prepare(src, dst, size) {
  execFileSync('convert', [src, '-trim', '+repage', '-resize', `${size}x${size}`, '-gravity', 'center', '-background', 'none', '-extent', '300x300', dst]);
}
function webp(src, dst) {
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', src, '-c:v', 'libwebp', '-quality', '92', '-compression_level', '6', dst]);
}

for (const f of fs.readdirSync(OUT)) if (/^sym_.*\.webp$/.test(f)) fs.rmSync(path.join(OUT, f));
for (const f of fs.readdirSync(FALLBACK)) if (/^sym_.*\.png$/.test(f)) fs.rmSync(path.join(FALLBACK, f));
for (const [id, file] of Object.entries(SYMBOL_MAP)) {
  const png = path.join(FALLBACK, `sym_${id}.png`);
  prepare(path.join(SRC, `${file}.png`), png, BIG.has(id) ? 292 : 262);
  webp(png, path.join(OUT, `sym_${id}.webp`));
  console.log(`✓ ${file} -> sym_${id}`);
}
