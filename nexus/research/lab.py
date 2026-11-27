"""Laboratoire de recherche : outils transverses.

- empreinte des données utilisées (reproductibilité) ;
- walk-forward du PROCESSUS DE SÉLECTION au sein d'une famille (aucun optimiseur
  de profit : on choisit, à chaque pli, la variante dont la borne basse de l'IC
  sur le passé est la plus haute, puis on mesure son résultat sur le pli suivant) ;
- sensibilité des paramètres (dispersion des résultats entre variantes voisines) ;
- indicateurs d'alerte de surajustement.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd

from ..config import BARS_DIR


def data_hash(symbols: list[str], years: range) -> str:
    h = hashlib.sha256()
    for s in symbols:
        for y in years:
            p = BARS_DIR / s / f"{y}.parquet"
            if p.exists():
                h.update(s.encode()); h.update(str(y).encode()); h.update(p.read_bytes())
    return h.hexdigest()[:16]


def walk_forward_selection(trades_by_variant: dict, start, end, *, fold_months: int = 6, min_trades: int = 10) -> dict:
    """trades_by_variant : {nom: DataFrame avec exit_time, r_net}. Plis d'ancrage croissants.
    Critère de choix (sur le passé uniquement) : moyenne − 1,96 × erreur type."""
    s0, s1 = pd.Timestamp(start), pd.Timestamp(end)
    s0 = s0 if s0.tzinfo else s0.tz_localize("UTC")
    s1 = s1 if s1.tzinfo else s1.tz_localize("UTC")
    edges = pd.date_range(s0, s1, freq=f"{fold_months}MS")
    chosen, oos = [], []
    for a, b in zip(edges[1:-1], edges[2:]):
        best, best_score = None, -np.inf
        for name, tr in trades_by_variant.items():
            past = tr[tr["exit_time"] < a]["r_net"]
            if len(past) < min_trades:
                continue
            score = past.mean() - 1.96 * past.std(ddof=1) / np.sqrt(len(past))
            if score > best_score:
                best, best_score = name, score
        if best is None:
            chosen.append({"fold": f"{a.date()}..{b.date()}", "choice": None}); continue
        tr = trades_by_variant[best]
        nxt = tr[(tr["entry_time"] >= a) & (tr["exit_time"] < b)]["r_net"]
        oos.append(nxt)
        chosen.append({"fold": f"{a.date()}..{b.date()}", "choice": best, "n": int(len(nxt)),
                       "mean_r": float(nxt.mean()) if len(nxt) else None})
    allr = pd.concat(oos) if oos else pd.Series(dtype=float)
    return {"folds": chosen, "oos_n": int(len(allr)), "oos_mean_r": float(allr.mean()) if len(allr) else None}


def overfit_flags(row: dict) -> list[str]:
    """Alertes simples (n'excluent rien automatiquement)."""
    flags = []
    if row.get("n_trades", 0) < 30:
        flags.append("échantillon < 30 trades : IC très large")
    if row.get("top5_share", 0) and row["top5_share"] > 50:
        flags.append("> 50 % du profit brut sur 5 trades")
    folds = [f.get("mean_r") for f in (row.get("folds") or {}).values() if f.get("mean_r") is not None]
    if folds and sum(1 for x in folds if x > 0) < len(folds) / 2:
        flags.append("positif sur moins de la moitié des semestres")
    if row.get("mean_r_x2") is not None and row.get("mean_r", 0) > 0 and row["mean_r_x2"] <= 0:
        flags.append("ne résiste pas au doublement des coûts")
    if row.get("beta") is not None and row.get("alpha_lo") is not None and row["alpha_lo"] <= 0 < row.get("mean_r", 0):
        flags.append("alpha non distinguable de zéro : performance expliquée par l'exposition au marché")
    return flags
