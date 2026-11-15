import raw from '$shared/game-config.json';
import type { GameConfig } from './types';

/** Game rules exported by the Python math engine (single source of truth). */
export const RULES = raw as unknown as GameConfig;

export const WINCAP = RULES.wincapX * 100; // in payoutMultiplier units
