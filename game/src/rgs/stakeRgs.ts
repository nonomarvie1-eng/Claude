// Stake Engine RGS client — written from the public RGS specification
// (engineio/math-sdk docs/rgs_docs/RGS.md).  NOT ACTIVATED in the demo:
// it is only selected when the page is launched by an operator with
// `sessionID` and `rgs_url` query parameters AND the build flag
// VITE_ENABLE_RGS=1.  Never test it with real player credentials.
import { RgsError, validateRound, type AuthResult, type Balance, type RgsClient, type RgsErrorCode, type Round } from './types';

type Fetch = typeof fetch;

export class StakeRgs implements RgsClient {
  readonly kind = 'stake' as const;
  private base: string;

  constructor(rgsUrl: string, private sessionID: string, private fetchImpl: Fetch = fetch.bind(globalThis), private timeoutMs = 15_000) {
    this.base = /^https?:\/\//.test(rgsUrl) ? rgsUrl.replace(/\/$/, '') : `https://${rgsUrl.replace(/\/$/, '')}`;
  }

  private async post<T>(path: string, body: Record<string, unknown>): Promise<T> {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), this.timeoutMs);
    let res: Response;
    try {
      res = await this.fetchImpl(`${this.base}${path}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sessionID: this.sessionID, ...body }),
        signal: ctrl.signal,
      });
    } catch (e) {
      throw new RgsError((e as Error).name === 'AbortError' ? 'ERR_TIMEOUT' : 'ERR_NETWORK', String(e), true);
    } finally {
      clearTimeout(timer);
    }
    let data: unknown = null;
    try {
      data = await res.json();
    } catch {
      /* fallthrough */
    }
    if (!res.ok) {
      const code = ((data as { code?: string; error?: string })?.code ?? (data as { error?: string })?.error ?? (res.status >= 500 ? 'ERR_GEN' : 'ERR_VAL')) as RgsErrorCode;
      throw new RgsError(code, (data as { message?: string })?.message, res.status >= 500);
    }
    return data as T;
  }

  private normaliseRound(r: Record<string, unknown> | null | undefined): Round | null {
    if (!r) return null;
    const state = (r.state ?? r.events) as Round['state'];
    return validateRound({ ...r, state } as Round);
  }

  async authenticate(): Promise<AuthResult> {
    const d = await this.post<{ balance: Balance; config: AuthResult['config']; round?: Record<string, unknown> }>('/wallet/authenticate', {});
    return { balance: d.balance, config: d.config, round: d.round && (d.round as { active?: boolean }).active ? this.normaliseRound(d.round) : null };
  }

  async balance(): Promise<Balance> {
    return (await this.post<{ balance: Balance }>('/wallet/balance', {})).balance;
  }

  async play(amount: number, mode: string) {
    const d = await this.post<{ balance: Balance; round: Record<string, unknown> }>('/wallet/play', { amount, mode });
    const round = this.normaliseRound(d.round);
    if (!round) throw new RgsError('ERR_DATA', 'no round');
    return { balance: d.balance, round };
  }

  async endRound() {
    return this.post<{ balance: Balance }>('/wallet/end-round', {});
  }

  async event(event: string) {
    await this.post('/bet/event', { event });
  }
}
