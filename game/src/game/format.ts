import { MONEY_SCALE } from '../rgs/types';

/** Formats an RGS integer amount (6 decimals).  Demo credits use "DEMO". */
export function money(amount: number, currency = 'DEMO', lang = 'fr'): string {
  const v = amount / MONEY_SCALE;
  const n = new Intl.NumberFormat(lang === 'fr' ? 'fr-FR' : 'en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(v);
  if (currency === 'DEMO') return n;
  const sym: Record<string, string> = { USD: '$', EUR: '€', CAD: 'CA$', BRL: 'R$', XGC: 'GC ', XSC: 'SC ' };
  return (sym[currency] ?? currency + ' ') + n;
}

/** Win in money units for a payoutMultiplier (bet multiple x100). */
export function winAmount(bet: number, payoutMultiplier: number): number {
  return Math.round((bet * payoutMultiplier) / 100);
}
