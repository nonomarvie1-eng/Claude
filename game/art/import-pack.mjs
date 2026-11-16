// Imports the 15-symbol pack (art/pack/png) into the game.
// * Maps pack files onto the symbol IDs that really exist in the math engine
//   (IDs, reels, pays and probabilities are untouched — visuals only).
// * Crops each 512x512 sprite to a centred 330x330 square (the artwork of
//   every file sits in a ~305 px centred box) so symbols fill their cells;
//   no up-scaling, alpha preserved.
// * Writes WebP (primary) + PNG (fallback) for the reel symbols, and keeps the
//   unused pack items as UI/reserve resources.
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.dirname(HERE);
const SRC = path.join(HERE, 'pack', 'png');
const OUT = path.join(ROOT, 'src', 'assets', 'img');
const FALLBACK = path.join(ROOT, 'src', 'assets', 'img-png');
fs.mkdirSync(OUT, { recursive: true });
fs.mkdirSync(FALLBACK, { recursive: true });

// engine symbol id -> pack asset
export const SYMBOL_MAP = {
  W: 'wild',
  S: 'scatter',
  H1: 'champion_male',
  H2: 'champion_female',
  H3: 'umpire',
  H4: 'victory_trophy',
  H5: 'ace_mascot',
  L1: 'advantage',
  L2: 'score_40',
  L3: 'score_30',
  L4: 'score_15',
  L5: 'love',
};
// not on the reels: interface / transition resources
const UI_ASSETS = { ui_golden_ball: 'golden_ball', ui_tiebreak: 'tiebreak_bonus' };
// kept for a later evolution, not loaded by the game
const RESERVE = ['champion_racket'];

function crop(src, dst) {
  execFileSync('convert', [src, '-crop', '330x330+91+91', '+repage', dst]);
}
function webp(src, dst) {
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', src, '-c:v', 'libwebp', '-quality', '92', '-compression_level', '6', dst]);
}

for (const [id, asset] of Object.entries({ ...Object.fromEntries(Object.entries(SYMBOL_MAP).map(([k, v]) => [`sym_${k}`, v])), ...UI_ASSETS })) {
  const src = path.join(SRC, `${asset}.png`);
  const png = path.join(FALLBACK, `${id}.png`);
  crop(src, png);
  webp(png, path.join(OUT, `${id}.webp`));
  console.log(`✓ ${asset} -> ${id}`);
}
console.log('reserve (not loaded):', RESERVE.join(', '));
