"""NEXUS G — Allocation dynamique BTC / liquidités (simulation journalière, EUR).

Famille indépendante : elle ne modifie pas les règles de risque des familles A à F.
Pas de levier, pas de vente à découvert, pas de stop individuel : le risque est GLOBAL.

Calendrier causal : le poids cible est calculé avec les clôtures jusqu'au jour t (UTC)
et exécuté à l'ouverture du jour t+1. La valorisation se fait à la clôture (côté bid).

Coûts, identiques pour les stratégies et les références :
- conversion EUR ↔ USDT : 0,10 % (barème standard, hypothèse) ;
- achat/vente BTC/USDT : 0,10 % taker ;
- demi-spread et glissement du modèle d'instrument ;
- quantité arrondie au pas de 0,00001 BTC ; ordre ignoré sous 5 USDT de notionnel.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import pandas as pd

from ..instruments import BTCUSDT_SPOT, InstrumentSpec


@dataclass
class Costs:
    btc_fee: float = 0.001
    conv_fee: float = 0.001
    half_spread: float = BTCUSDT_SPOT.modeled_half_spread_frac
    slippage: float = BTCUSDT_SPOT.slippage_market_frac
    qty_step: float = BTCUSDT_SPOT.qty_step
    min_notional: float = BTCUSDT_SPOT.min_notional_quote

    def scaled(self, m: float) -> "Costs":
        return Costs(self.btc_fee * m, self.conv_fee * m, self.half_spread * m, self.slippage * m,
                     self.qty_step, self.min_notional)


def daily_frame(sig_m1: pd.DataFrame, eurusdt_h1: pd.DataFrame) -> pd.DataFrame:
    """Prix journaliers UTC (ouverture = 1re minute, clôture = dernière, plus bas) et taux EUR/USDT
    connus à l'ouverture et à la clôture (dernier H1 CLOS)."""
    s = sig_m1.set_index("ts")
    d = pd.DataFrame({"open": s["o"].resample("1D").first(), "high": s["h"].resample("1D").max(),
                      "low": s["l"].resample("1D").min(), "close": s["c"].resample("1D").last()}).dropna()
    r = eurusdt_h1.copy()
    r["avail"] = r["ts"] + pd.Timedelta(hours=1)
    r = r.set_index("avail")["c"].sort_index()
    d["fx_open"] = r.reindex(d.index, method="ffill").to_numpy()
    d["fx_close"] = r.reindex(d.index + pd.Timedelta(days=1), method="ffill").to_numpy()
    return d.dropna()


# ---------------------------------------------------------------------------
# Règles de poids (causales : n'utilisent que les clôtures <= t)
# ---------------------------------------------------------------------------
def _vol30(c: pd.Series) -> pd.Series:
    return np.log(c).diff().rolling(30).std() * math.sqrt(365)


def weights(d: pd.DataFrame, rule: str, w_max: float, vol_ref: float = 0.80) -> pd.Series:
    c = d["close"]
    if rule == "G_MA":
        w = (c > c.rolling(100).mean()).astype(float) * w_max
        w[c.rolling(100).mean().isna()] = np.nan
    elif rule == "G_TSMOM":
        r90 = c / c.shift(90) - 1
        w = (r90 > 0).astype(float) * w_max
        w[r90.isna()] = np.nan
    elif rule == "G_VOL":
        w = (w_max * vol_ref / _vol30(c)).clip(upper=w_max)
    elif rule == "G_PROG":
        sma = c.rolling(100).mean()
        conds = pd.concat([c > sma, c / c.shift(30) > 1, c / c.shift(90) > 1], axis=1).astype(float)
        w = conds.mean(axis=1) * w_max
        w[sma.isna() | c.shift(90).isna()] = np.nan
    elif rule == "G_TSMOM_VOL":
        r90 = c / c.shift(90) - 1
        w = (r90 > 0).astype(float) * (w_max * vol_ref / _vol30(c)).clip(upper=w_max)
        w[r90.isna()] = np.nan
    elif rule == "CONST":
        w = pd.Series(w_max, index=d.index)
    else:
        raise KeyError(rule)
    return w


# ---------------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------------
@dataclass
class PortfolioResult:
    values: pd.Series          # valeur à la clôture (EUR)
    low_values: pd.Series      # valeur au plus bas de séance (EUR)
    exposure: pd.Series        # part de BTC dans la valeur à la clôture
    traded_eur: float
    fees_eur: float
    n_trades: int
    halted_on: object = None


def simulate(d: pd.DataFrame, target: pd.Series, start, end, *, initial: float = 1000.0, costs: Costs = Costs(),
             band_frac_of_max: float = 0.2, w_max: float | None = None, rebalance: str = "daily",
             global_halt: float | None = None) -> PortfolioResult:
    """target[t] : poids décidé à la clôture de t, exécuté à l'ouverture de t+1.
    rebalance : "daily" (avec zone neutre) | "monthly" (1er jour du mois) | "never" (achat initial seulement)."""
    dd = d[(d.index >= pd.Timestamp(start)) & (d.index < pd.Timestamp(end))]
    tgt = target.shift(1).reindex(dd.index)          # cible applicable à l'ouverture du jour
    cash, units = initial, 0.0
    band = band_frac_of_max * (w_max if w_max else 1.0)
    vals, lows, expo = [], [], []
    traded = fees = 0.0
    n_tr = 0
    peak, halted_on, halted = initial, None, False
    bought_once = False
    for i, (t, row) in enumerate(dd.iterrows()):
        w = tgt.iloc[i]
        if halted:
            w = 0.0
        if np.isfinite(w) if w is not None else False:
            bid_o = row["open"] * (1 - costs.half_spread - costs.slippage)
            ask_o = row["open"] * (1 + costs.half_spread + costs.slippage)
            v_open = cash + units * bid_o / row["fx_open"]
            cur_w = units * bid_o / row["fx_open"] / v_open if v_open > 0 else 0.0
            do = False
            if rebalance == "daily":
                do = abs(w - cur_w) >= band or (w == 0 and units > 0)
            elif rebalance == "monthly":
                do = (t.day == 1) or not bought_once or (w == 0 and units > 0)
            elif rebalance == "never":
                do = not bought_once
            if do:
                delta_eur = w * v_open - units * bid_o / row["fx_open"]
                if delta_eur > 0:
                    usdt = delta_eur * row["fx_open"] * (1 - costs.conv_fee)
                    q = math.floor(usdt * (1 - costs.btc_fee) / ask_o / costs.qty_step) * costs.qty_step
                    if q * ask_o >= costs.min_notional:
                        spent_usdt = q * ask_o / (1 - costs.btc_fee)
                        spent_eur = spent_usdt / row["fx_open"] / (1 - costs.conv_fee)
                        cash -= spent_eur; units += q
                        traded += spent_eur; n_tr += 1
                        fees += spent_eur - q * row["open"] / row["fx_open"]
                        bought_once = True
                elif delta_eur < 0:
                    q = units if w == 0 else min(units, math.floor(-delta_eur * row["fx_open"] / bid_o / costs.qty_step) * costs.qty_step)
                    if q > 0 and q * bid_o >= costs.min_notional or (w == 0 and q > 0):
                        usdt = q * bid_o * (1 - costs.btc_fee)
                        eur = usdt / row["fx_open"] * (1 - costs.conv_fee)
                        cash += eur; units -= q
                        traded += eur; n_tr += 1
                        fees += q * row["open"] / row["fx_open"] - eur
                if units < costs.qty_step / 2:
                    units = 0.0
        bid_c = row["close"] * (1 - costs.half_spread)
        v = cash + units * bid_c / row["fx_close"]
        vals.append(v)
        lows.append(cash + units * row["low"] * (1 - costs.half_spread) / row["fx_close"])
        expo.append(units * bid_c / row["fx_close"] / v if v > 0 else 0.0)
        peak = max(peak, v)
        if global_halt is not None and not halted and v <= peak * (1 - global_halt):
            halted, halted_on = True, t
    idx = dd.index
    return PortfolioResult(pd.Series(vals, idx), pd.Series(lows, idx), pd.Series(expo, idx), traded, fees, n_tr, halted_on)


def metrics(res: PortfolioResult, initial: float = 1000.0) -> dict:
    v = res.values
    r = v.pct_change().dropna()
    years = len(v) / 365.25
    dd = v / v.cummax() - 1
    low_dd = (res.low_values / v.cummax().shift(1).fillna(initial)).min() - 1
    under = (dd < 0).astype(int)
    longest = int(under.groupby((under == 0).cumsum()).sum().max()) if len(under) else 0
    downside = r[r < 0]
    dstd = math.sqrt((downside ** 2).sum() / len(r)) if len(r) else np.nan
    cagr = (v.iloc[-1] / initial) ** (1 / years) - 1 if years > 0 else np.nan
    max_dd = float(-dd.min())
    q05 = r.quantile(0.05)
    return {
        "final_eur": float(v.iloc[-1]), "net_return_pct": float((v.iloc[-1] / initial - 1) * 100), "cagr_pct": float(cagr * 100),
        "ann_vol_pct": float(r.std() * math.sqrt(365) * 100),
        "sharpe": float(r.mean() / r.std() * math.sqrt(365)) if r.std() > 0 else np.nan,
        "sortino": float(r.mean() / dstd * math.sqrt(365)) if dstd and dstd > 0 else np.nan,
        "max_dd_pct": max_dd * 100, "calmar": float(cagr / max_dd) if max_dd > 0 else np.nan,
        "intraday_worst_dd_pct": float(-low_dd * 100), "longest_underwater_days": longest,
        "worst_day_pct": float(r.min() * 100), "worst_week_pct": float((v.resample("W").last().pct_change().min()) * 100),
        "cvar5_daily_pct": float(r[r <= q05].mean() * 100),
        "time_in_market_pct": float((res.exposure > 0.001).mean() * 100), "avg_exposure_pct": float(res.exposure.mean() * 100),
        "turnover_per_year": float(res.traded_eur / v.mean() / years), "fees_eur": float(res.fees_eur), "n_trades": res.n_trades,
        "halted_on": str(res.halted_on) if res.halted_on is not None else None,
    }


def episode_returns(res: PortfolioResult, episodes: dict) -> dict:
    out = {}
    for name, (a, b) in episodes.items():
        s = res.values[(res.values.index >= pd.Timestamp(a, tz="UTC")) & (res.values.index <= pd.Timestamp(b, tz="UTC"))]
        out[name] = float((s.iloc[-1] / s.iloc[0] - 1) * 100) if len(s) > 1 else None
    return out


def diff_test(a: pd.Series, b: pd.Series, *, block: int = 20, n_boot: int = 5000, seed: int = 0) -> dict:
    """Différence de rendement quotidien moyen (a − b), annualisée, IC95 et p unilatéral
    (H0 : différence <= 0), bootstrap par blocs mobiles."""
    ra, rb = a.pct_change().dropna(), b.pct_change().dropna()
    x = (ra - rb.reindex(ra.index)).dropna().to_numpy()
    n = len(x); nb = int(np.ceil(n / block))
    rng = np.random.default_rng(seed)
    means = np.empty(n_boot)
    for k in range(n_boot):
        st = rng.integers(0, n - block + 1, nb)
        means[k] = x[np.concatenate([np.arange(s, s + block) for s in st])[:n]].mean()
    m = x.mean()
    p = float((np.sum(means - m >= m) + 1) / (n_boot + 1))
    lo, hi = np.percentile(means, [2.5, 97.5])
    return {"diff_ann_pct": float(m * 365 * 100), "ci95_ann_pct": [float(lo * 365 * 100), float(hi * 365 * 100)], "p": p}
