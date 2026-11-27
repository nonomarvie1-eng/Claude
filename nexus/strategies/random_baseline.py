"""Entrées aléatoires comparables (modèle nul).

Pour une stratégie ayant produit N trades, chaque réplication tire N trades :
- jour tiré uniformément parmi TOUS les jours éligibles (range valide), et non
  parmi les jours tradés (ce qui conditionnerait sur l'issue de la journée) ;
- instant uniforme dans la fenêtre d'entrée de ce jour ;
- sens aléatoire si la vente est possible, achat sinon (spot) ;
- distance de stop (relative au prix) tirée dans la distribution des trades réels ;
- même règle d'objectif (multiple de R) et même sortie horaire.
Coûts et exécution identiques. Ce modèle nul mesure la valeur du choix du jour,
de l'instant et du sens par la stratégie, à géométrie de risque égale.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..engine.backtest import fees_quote
from ..engine.execution import ExecFrame, simulate
from ..instruments import InstrumentSpec


def matched_random_r(trades: pd.DataFrame, target_r_list: list, ex: ExecFrame, spec: InstrumentSpec,
                     windows: dict, *, n_rep: int = 200, seed: int = 0) -> np.ndarray:
    """windows : {jour: (debut_utc, fin_utc, sortie_utc)} des jours éligibles.
    target_r_list : objectif en R de chaque trade réel (None = sortie horaire seule)."""
    rng = np.random.default_rng(seed)
    days = list(windows)
    rel = (np.abs(trades["entry"] - trades["stop"]) / trades["entry"]).to_numpy()
    n = len(trades)
    means = np.full(n_rep, np.nan)
    for r in range(n_rep):
        out = []
        for _ in range(n):
            w0, w1, xt = windows[days[int(rng.integers(len(days)))]]
            i0, i1 = ex.index_at_or_after(int(w0.value)), ex.index_at_or_after(int(w1.value))
            if i1 - i0 < 2:
                continue
            k = int(rng.integers(i0, i1 - 1))
            side = int(rng.choice([-1, 1])) if spec.allow_short else 1
            j = int(rng.integers(n))
            mid = (ex.bid_c[k] + ex.ask_c[k]) / 2
            stop = mid * (1 - side * rel[j])
            f = simulate(ex, spec, side=side, signal_avail=pd.Timestamp(int(ex.ts[k + 1]), tz="UTC"),
                         stop=stop, target=None, target_r=target_r_list[j], time_exit=xt)
            if not f.filled:
                continue
            ru = abs(f.entry_price - stop)
            if ru <= 0:
                continue
            fee_u = fees_quote(spec, 1.0, f.entry_price, f.exit_price)
            out.append((side * (f.exit_price - f.entry_price) - fee_u) / ru)
        means[r] = np.mean(out) if out else np.nan
    return means


def exposure_matched_random(trades: pd.DataFrame, ex: ExecFrame, spec: InstrumentSpec, start, end,
                            *, n_rep: int = 200, seed: int = 0) -> dict:
    """Entrées aléatoires à EXPOSITION COMPARABLE : même nombre de trades, même durée
    de détention (trade par trade), même distance de stop relative, même sens
    (achat en spot) ; instant d'entrée uniforme sur toute la période. Capte la dérive
    du marché (ex. hausse générale de BTC) à exposition égale.
    Renvoie les moyennes de R net et de rendement par trade de chaque réplication."""
    rng = np.random.default_rng(seed)
    dur_ns = ((trades["exit_time"] - trades["entry_time"]).dt.total_seconds().to_numpy() * 1e9).astype(np.int64)
    rel = (np.abs(trades["entry"] - trades["stop"]) / trades["entry"]).to_numpy()
    sides = trades["side"].to_numpy()
    s_ns, e_ns = int(pd.Timestamp(start).value), int(pd.Timestamp(end).value)
    i_lo = ex.index_at_or_after(s_ns)
    r_means, ret_means, top5 = np.full(n_rep, np.nan), np.full(n_rep, np.nan), np.full(n_rep, np.nan)
    for r in range(n_rep):
        rs, rets = [], []
        for j in range(len(trades)):
            last_start = e_ns - dur_ns[j]
            i_hi = ex.index_at_or_after(last_start)
            if i_hi - i_lo < 2:
                continue
            k = int(rng.integers(i_lo, i_hi - 1))
            side = int(sides[j]) if spec.allow_short else 1
            mid = (ex.bid_c[k] + ex.ask_c[k]) / 2
            stop = mid * (1 - side * rel[j])
            t0 = int(ex.ts[k + 1])
            f = simulate(ex, spec, side=side, signal_avail=pd.Timestamp(t0, tz="UTC"), stop=stop, target=None,
                         time_exit=pd.Timestamp(t0 + dur_ns[j], tz="UTC"))
            if not f.filled:
                continue
            ru = abs(f.entry_price - stop)
            fee_u = fees_quote(spec, 1.0, f.entry_price, f.exit_price)
            pnl_u = side * (f.exit_price - f.entry_price) - fee_u
            rs.append(pnl_u / ru); rets.append(pnl_u / f.entry_price)
        r_means[r] = np.mean(rs) if rs else np.nan
        ret_means[r] = np.mean(rets) if rets else np.nan
        pos = np.array([x for x in rets if x > 0])
        top5[r] = np.sort(pos)[-5:].sum() / pos.sum() * 100 if pos.sum() > 0 else np.nan
    return {"r_means": r_means, "ret_means": ret_means, "top5_share": top5}
