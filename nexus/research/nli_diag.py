"""Diagnostics hors sélection (famille NLI-DIAG) — période de développement uniquement.

1. Cointégration BTC/ETH : régression log(BTC) = α + β log(ETH) estimée sur des fenêtres
   PASSÉES de 180 jours (pas mensuel), test d'Engle–Granger, stabilité de β, test CUSUM
   de rupture sur toute la période (descriptif).
2. Faisabilité OFI : déséquilibre du volume taker par minute (volume acheteur agresseur réel
   des archives Binance, jamais reconstruit à partir des bougies) ; corrélation de rang avec
   le rendement des 1 et 5 minutes suivantes ; comparaison avec les coûts.

    python -m nexus.research.nli_diag
"""
from __future__ import annotations

import io
import json
import zipfile

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.diagnostic import breaks_cusumolsresid
from statsmodels.tsa.stattools import coint

from ..config import PERIODS, RESULTS_DIR
from ..data import binance
from ..data.store import load_bars
from .registry import Registry


def cointegration(reg: Registry) -> dict:
    p0, p1 = PERIODS["dev"]
    tid = reg.start_trial("NLI-DIAG-COINT", {"pair": "BTC/ETH"}, "BTCUSDT+ETHUSDT", "dev", 1.0, purpose="diagnostic")
    b = load_bars("BTCUSDT", p0, p1).set_index("ts")["c"].resample("1D").last()
    e = load_bars("ETHUSDT", p0, p1).set_index("ts")["c"].resample("1D").last()
    df = np.log(pd.concat([b, e], axis=1, keys=["btc", "eth"]).dropna())
    rows = []
    for end in pd.date_range(df.index[0] + pd.Timedelta(days=180), df.index[-1], freq="MS"):
        w = df[(df.index < end) & (df.index >= end - pd.Timedelta(days=180))]
        beta, alpha = np.polyfit(w["eth"], w["btc"], 1)
        t, p, _ = coint(w["btc"], w["eth"])
        rows.append({"end": str(end.date()), "beta": float(beta), "alpha": float(alpha), "eg_p": float(p)})
    r = pd.DataFrame(rows)
    beta_full, alpha_full = np.polyfit(df["eth"], df["btc"], 1)
    resid = df["btc"] - (alpha_full + beta_full * df["eth"])
    cus = breaks_cusumolsresid(resid.to_numpy())
    out = {"windows": rows, "share_windows_cointegrated_5pct": float((r["eg_p"] < 0.05).mean()),
           "beta_min": float(r["beta"].min()), "beta_max": float(r["beta"].max()), "beta_std": float(r["beta"].std()),
           "corr_daily_returns": float(df.diff().dropna().corr().iloc[0, 1]),
           "cusum_full_period_p": float(cus[1]),
           "note": "β et α estimés sur le passé uniquement ; vente à découvert impossible en spot : un spread neutre n'est pas exécutable."}
    reg.finish_trial(tid, status="done", n_trades=len(rows), result={"share": out["share_windows_cointegrated_5pct"]})
    return out


def ofi(reg: Registry) -> dict:
    p0, p1 = PERIODS["dev"]
    tid = reg.start_trial("NLI-DIAG-OFI", {"bar": "1min"}, "BTCUSDT", "dev", 1.0, purpose="diagnostic")
    frames = []
    for y, m in binance.months("2020-01", "2023-07"):
        with zipfile.ZipFile(binance.raw_path("BTCUSDT", y, m)) as z:
            d = pd.read_csv(io.BytesIO(z.read(z.namelist()[0])), header=None, names=binance.COLS,
                            usecols=["open_time", "c", "v", "taker_base"])
        frames.append(d)
    d = pd.concat(frames, ignore_index=True)
    d = d[d["v"] > 0]
    imb = (2 * d["taker_base"] - d["v"]) / d["v"]                    # ∈ [−1, 1], volume taker réel
    lc = np.log(d["c"].to_numpy())
    res = {}
    for h in (1, 5):
        fwd = np.concatenate([lc[h:] - lc[:-h], np.full(h, np.nan)])
        ok = np.isfinite(fwd)
        rho = stats.spearmanr(imb.to_numpy()[ok][::h], fwd[ok][::h])[0]    # échantillon sans chevauchement
        q = pd.qcut(imb[ok], 10, labels=False, duplicates="drop")
        dec = pd.Series(fwd[ok]).groupby(q.to_numpy()).mean() * 1e4
        res[f"h{h}"] = {"spearman_nonoverlap": float(rho), "fwd_ret_bp_top_decile": float(dec.iloc[-1]),
                        "fwd_ret_bp_bottom_decile": float(dec.iloc[0]), "spread_top_bottom_bp": float(dec.iloc[-1] - dec.iloc[0])}
    res["round_trip_cost_bp"] = 2 * 10 + 2 * 0.5 + 1 + 2
    res["note"] = ("Faisabilité seulement. L'écart entre déciles extrêmes est à comparer au coût aller-retour ; "
                   "aucune stratégie à haute fréquence n'est développée. Le carnet L2 historique spot n'est pas disponible.")
    reg.finish_trial(tid, status="done", result={"h1": res["h1"]["spearman_nonoverlap"]})
    return res


def main():
    reg = Registry()
    for key, st in (("NLI-DIAG-COINT", "Cointégration roulante BTC/ETH (Engle–Granger, fenêtres passées de 180 j)"),
                    ("NLI-DIAG-OFI", "Faisabilité du déséquilibre de volume taker (OFI minute)")):
        reg.register_hypothesis({"key": key, "family": "NLI-DIAG", "statement": st, "rationale": "Diagnostic hors sélection (lot 3-01).",
                                 "params": {}, "data": {"period": "dev"}, "metrics": ["voir module"], "rejection": {"text": "diagnostic"}})
    out = {"cointegration": cointegration(reg), "ofi": ofi(reg)}
    d = RESULTS_DIR / "batch_3_01_events"; d.mkdir(parents=True, exist_ok=True)
    (d / "diagnostics.json").write_text(json.dumps(out, indent=2, default=str, ensure_ascii=False))
    c = out["cointegration"]
    print({k: v for k, v in c.items() if k != "windows"})
    print(out["ofi"])


if __name__ == "__main__":
    main()
