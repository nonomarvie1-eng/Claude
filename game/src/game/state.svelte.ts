import { detectLang, STRINGS, type Lang } from '../i18n/strings';
import type { BookEvent } from '../engine/types';
import type { Jurisdiction } from '../rgs/types';

export interface HistoryEntry {
  id: string | number;
  time: number;
  bet: number;
  cost?: number;
  win: number;
  payoutMultiplier: number;
  bonus: boolean;
  forced?: string;
  events: BookEvent[];
}

const PREFS_KEY = 'golden-rally-prefs-v1';
const HIST_KEY = 'golden-rally-history-v1';

function readJSON<T>(key: string, fallback: T): T {
  try {
    const v = localStorage.getItem(key);
    return v ? { ...fallback, ...JSON.parse(v) } : fallback;
  } catch {
    return fallback;
  }
}

function readArr<T>(key: string): T[] {
  try {
    const v = localStorage.getItem(key);
    const a = v ? JSON.parse(v) : [];
    return Array.isArray(a) ? a : [];
  } catch {
    return [];
  }
}

const prefersReduced = (() => {
  try {
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  } catch {
    return false;
  }
})();

export type Phase = 'loading' | 'ready' | 'idle' | 'spinning' | 'replay' | 'error';

class GameState {
  phase = $state<Phase>('loading');
  loadProgress = $state(0);
  balance = $state(0);
  currency = $state('DEMO');
  bet = $state(1_000_000);
  betLevels = $state<number[]>([]);
  win = $state(0);
  inBonus = $state(false);
  fsCurrent = $state(0);
  fsTotal = $state(0);
  multiplier = $state(1);
  modal = $state<null | 'paytable' | 'settings' | 'history' | 'buy' | 'auto'>(null);
  autoplay = $state<{ remaining: number } | null>(null);
  notice = $state<string | null>(null);
  error = $state<{ message: string; retryable: boolean; fatal: boolean } | null>(null);
  banner = $state<string | null>(null);
  jurisdiction = $state<Jurisdiction>({});
  isDemo = $state(true);
  history = $state<HistoryEntry[]>(readArr<HistoryEntry>(HIST_KEY));
  prefs = $state(
    readJSON(PREFS_KEY, {
      master: 0.8,
      music: 0.45,
      sfx: 0.9,
      sound: true,
      reducedMotion: prefersReduced,
      turbo: false,
      lang: detectLang(typeof location !== 'undefined' ? location.search : '') as Lang,
    }),
  );

  get t() {
    return STRINGS[this.prefs.lang];
  }

  savePrefs() {
    try {
      localStorage.setItem(PREFS_KEY, JSON.stringify(this.prefs));
    } catch {
      /* ignore */
    }
  }

  addHistory(e: HistoryEntry) {
    this.history = [e, ...this.history].slice(0, 30);
    try {
      localStorage.setItem(HIST_KEY, JSON.stringify(this.history));
    } catch {
      /* ignore */
    }
  }
}

export const game = new GameState();
