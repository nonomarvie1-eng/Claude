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
