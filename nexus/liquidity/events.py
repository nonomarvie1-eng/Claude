"""Études événementielles sur des niveaux de prix (aucune stratégie, aucun ordre).

Pour un niveau disponible à t_avail :
- le niveau doit être « devant » le prix à la première minute de la fenêtre de contact
  (sinon il est déjà franchi : exclu, statut « déjà atteint ») ;
- contact = première minute dont le plus bas (support) / plus haut (résistance) atteint le niveau ;
- course de barrières à ±k·ATR_H1 depuis le niveau : retournement (dans le sens attendu)
  ou franchissement ; si les deux sont touchés dans la même minute → franchissement
  (hypothèse défavorable au retournement) ;
- franchissement en clôture M5 dans les 6 bougies, réintégration ensuite dans les 6 bougies,
  délai de contact, MFE / MAE sur l'horizon, en ATR.
Niveaux de contrôle : même côté, distance réelle × U(0,5 ; 1,5), à plus de 0,25 ATR du niveau
réel, même instant de disponibilité et même fenêtre de contact.
"""
from __future__ import annotations

from dataclasses import replace

import numpy as np
import pandas as pd

from .levels import Level, Market

COST_FRAC = 2 * 0.001 + 2 * 0.5e-4 + 1e-4 + 2e-4   # aller-retour spot : frais + demi-spreads + glissements


def evaluate(mk: Market, lv: Level, k_atr: float = 1.0, race_h: float = 24.0) -> dict | None:
    a = mk.atr_h1_at(lv.avail)
    if not np.isfinite(a) or a <= 0:
        return None
    i0, i1 = mk.idx(lv.touch_from), mk.idx(lv.touch_to)
    if i0 >= len(mk.ts) or i1 <= i0:
        return None
    p, e = lv.price, lv.expect
    first_open = mk.o[i0]
    if (e == +1 and first_open <= p) or (e == -1 and first_open >= p):
        return {"status": "deja_atteint"}
    hit = np.flatnonzero(mk.l[i0:i1] <= p) if e == +1 else np.flatnonzero(mk.h[i0:i1] >= p)
    out = {"status": "ok", "atr": a, "dist_atr": abs(first_open - p) / a, "cost_atr": COST_FRAC * p / a,
           "touched": bool(len(hit)), "avail": lv.avail, "kind": lv.kind}
    if not len(hit):
        return out
    k = i0 + int(hit[0])
    out["time_to_touch_h"] = (mk.ts[k] - mk.ts[i0]) / 3.6e12
    kend = mk.idx(pd.Timestamp(int(mk.ts[k]), tz="UTC") + pd.Timedelta(hours=race_h))
    hh, ll = mk.h[k:kend], mk.l[k:kend]
    up, dn = p + k_atr * a, p - k_atr * a
    if e == +1:
        rev, cont = np.flatnonzero(hh >= up), np.flatnonzero(ll <= dn)
        mfe, mae = (hh.max() - p) / a, (p - ll.min()) / a
    else:
        rev, cont = np.flatnonzero(ll <= dn), np.flatnonzero(hh >= up)
        mfe, mae = (p - ll.min()) / a, (hh.max() - p) / a
    ir = rev[0] if len(rev) else None
    ic = cont[0] if len(cont) else None
    if ir is None and ic is None:
        out["race"] = "timeout"
    elif ic is not None and (ir is None or ic <= ir):
        out["race"] = "cont"
    else:
        out["race"] = "rev"
    out["mfe_atr"], out["mae_atr"] = float(mfe), float(mae)
    # franchissement / réintégration en clôture M5
    j = int(np.searchsorted(mk.m5_avail, mk.ts[k], side="right"))
    closes = mk.m5["c"].to_numpy()[j:j + 12]
    beyond = (closes < p) if e == +1 else (closes > p)
    out["cross"] = bool(beyond[:6].any())
    if out["cross"]:
        f = int(np.argmax(beyond[:6]))
        back = (closes[f + 1:f + 7] > p) if e == +1 else (closes[f + 1:f + 7] < p)
        out["reintegration"] = bool(back.any())
    return out


def controls_timeshift(mk: Market, lv: Level, n: int, rng, max_days: int = 30) -> list[Level]:
    """Contrôles pour la métrique de CONTACT (amendement 3-01a) : même distance normalisée
    (distance / ATR_H1), même heure NY, autre jour tiré dans ±max_days. La calibration sous
    H0 a montré que des contrôles à distance × U(0,5 ; 1,5) biaisent P(contact)."""
    a = mk.atr_h1_at(lv.avail)
    i0 = mk.idx(lv.touch_from)
    if not np.isfinite(a) or a <= 0 or i0 >= len(mk.ts):
        return []
    d_atr = abs(mk.o[i0] - lv.price) / a
    out = []
    for _ in range(n * 10):
        if len(out) >= n:
            break
        k = int(rng.integers(1, max_days + 1)) * (1 if rng.random() < 0.5 else -1)
        sh = pd.Timedelta(days=k)
        j = mk.idx(lv.touch_from + sh)
        if j >= len(mk.ts) or j <= 0 or mk.idx(lv.touch_to + sh) >= len(mk.ts):
            continue
        a2 = mk.atr_h1_at(lv.avail + sh)
        if not np.isfinite(a2) or a2 <= 0:
            continue
        pc = mk.o[j] - lv.expect * d_atr * a2
        out.append(replace(lv, price=float(pc), kind="CTRL_" + lv.kind, origin="contrôle décalé", created=lv.created + sh,
                           avail=lv.avail + sh, touch_from=lv.touch_from + sh, touch_to=lv.touch_to + sh))
    return out


def controls_for(mk: Market, lv: Level, n: int, rng, min_sep_atr: float = 0.25) -> list[Level]:
    a = mk.atr_h1_at(lv.avail)
    i0 = mk.idx(lv.touch_from)
    if not np.isfinite(a) or i0 >= len(mk.ts):
        return []
    ref = mk.o[i0]
    d = abs(ref - lv.price)
    out = []
    for _ in range(n * 20):
        if len(out) >= n:
            break
        dc = d * rng.uniform(0.5, 1.5)
        pc = ref - dc if lv.expect == +1 else ref + dc
        if abs(pc - lv.price) >= min_sep_atr * a and dc > 0:
            out.append(replace(lv, price=float(pc), kind="CTRL_" + lv.kind, origin="contrôle"))
    return out


def run_levels(mk: Market, levels: list[Level], *, n_controls: int = 3, seed: int = 0, k_atr: float = 1.0,
               race_h: float = 24.0, with_controls: bool = True, control_mode: str = "distance"):
    rng = np.random.default_rng(seed)
    real, ctrl = [], []
    for lv in levels:
        r = evaluate(mk, lv, k_atr, race_h)
        if r is not None:
            r = {**r, **{f"x_{k}": v for k, v in lv.extra.items()}, "avail": lv.avail}
        if r is None or r["status"] != "ok":
            if r is not None:
                real.append(r)
            continue
        real.append(r)
        if with_controls:
            gen = controls_timeshift if control_mode == "timeshift" else controls_for
            for cl in gen(mk, lv, n_controls, rng):
                rc = evaluate(mk, cl, k_atr, race_h)
                if rc is not None and rc["status"] == "ok":
                    ctrl.append(rc)
    return pd.DataFrame(real), pd.DataFrame(ctrl)


def summarize(df: pd.DataFrame) -> dict:
    if len(df) == 0:
        return {"n": 0}
    ok = df[df["status"] == "ok"] if "status" in df else df
    t = ok[ok["touched"]] if "touched" in ok else ok
    races = t[t["race"].isin(["rev", "cont"])] if "race" in t else t
    s = {"n_levels": int(len(df)), "n_deja_atteint": int((df.get("status") == "deja_atteint").sum()) if "status" in df else 0,
         "n_eligible": int(len(ok)), "p_touch": float(ok["touched"].mean()) if len(ok) else np.nan,
         "n_touched": int(len(t)), "n_race": int(len(races)),
         "p_reversal": float((races["race"] == "rev").mean()) if len(races) else np.nan,
         "p_timeout": float((t["race"] == "timeout").mean()) if len(t) else np.nan,
         "p_cross_close": float(t["cross"].mean()) if len(t) and "cross" in t else np.nan,
         "median_time_to_touch_h": float(t["time_to_touch_h"].median()) if len(t) else np.nan,
         "median_mfe_atr": float(t["mfe_atr"].median()) if len(t) else np.nan,
         "median_mae_atr": float(t["mae_atr"].median()) if len(t) else np.nan,
         "median_dist_atr": float(ok["dist_atr"].median()) if len(ok) else np.nan,
         "mean_cost_atr": float(ok["cost_atr"].mean()) if len(ok) else np.nan}
    if "reintegration" in t:
        cr = t[t["cross"]]
        s["p_reintegration_given_cross"] = float(cr["reintegration"].mean()) if len(cr) else np.nan
    s["p_breakeven_reversal"] = float((1 + s["mean_cost_atr"]) / 2) if np.isfinite(s.get("mean_cost_atr", np.nan)) else np.nan
    return s


def _weeks(ts: pd.Series) -> np.ndarray:
    t = pd.DatetimeIndex(ts).tz_convert("UTC")
    iso = t.isocalendar()
    return (iso["year"].astype(int) * 100 + iso["week"].astype(int)).to_numpy()


def delta_test(real: pd.DataFrame, ctrl: pd.DataFrame, metric: str, *, n_boot: int = 5000, seed: int = 0) -> dict:
    """Δ = métrique(réel) − métrique(contrôle), bootstrap par blocs de semaines communes."""
    def prep(df):
        ok = df[df["status"] == "ok"].copy() if len(df) else df
        if metric == "touch":
            ok["y"] = ok["touched"].astype(float)
        else:
            ok = ok[ok["touched"]] if len(ok) else ok
            ok = ok[ok["race"].isin(["rev", "cont"])]
            target = "rev" if metric == "reversal" else "cont"
            ok["y"] = (ok["race"] == target).astype(float)
        return ok
    a, b = prep(real), prep(ctrl)
    if len(a) < 20 or len(b) < 20:
        return {"n_real": int(len(a)), "n_ctrl": int(len(b)), "delta": np.nan, "p": np.nan, "ci95": [np.nan, np.nan]}
    wa, wb = _weeks(a["avail"]), _weeks(b["avail"])
    weeks = np.union1d(wa, wb)
    sa = pd.Series(a["y"].to_numpy()).groupby(wa).agg(["sum", "count"]).reindex(weeks, fill_value=0)
    sb = pd.Series(b["y"].to_numpy()).groupby(wb).agg(["sum", "count"]).reindex(weeks, fill_value=0)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(weeks), (n_boot, len(weeks)))
    ma = sa["sum"].to_numpy()[idx].sum(1) / np.maximum(sa["count"].to_numpy()[idx].sum(1), 1)
    mb = sb["sum"].to_numpy()[idx].sum(1) / np.maximum(sb["count"].to_numpy()[idx].sum(1), 1)
    d = ma - mb
    obs = float(a["y"].mean() - b["y"].mean())
    p = float((np.sum(d - obs >= obs) + 1) / (n_boot + 1))
    return {"n_real": int(len(a)), "n_ctrl": int(len(b)), "real": float(a["y"].mean()), "ctrl": float(b["y"].mean()),
            "delta": obs, "ci95": [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))], "p": p}
