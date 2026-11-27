"""Exécution du lot pré-enregistré 3-01 (études événementielles Liquidity Intelligence).

    python -m nexus.research.nli_runner experiments/preregistration/batch_3_01_events.toml [SYMBOL]
"""
from __future__ import annotations

import json
import sys
import time
import tomllib
from pathlib import Path

import numpy as np
import pandas as pd

from ..config import PERIODS, RESULTS_DIR
from ..data.store import load_bars
from ..features.core import last_confirmed_level, signal_frame, swings
from ..liquidity.events import delta_test, run_levels, summarize
from ..liquidity.levels import (NY, Market, fpfvg_split, fvg_levels, fvg_records, ifvg_levels, ny, pd_levels, pw_levels,
                                session_levels, swing_levels, unicorn_levels)
from ..stats.inference import benjamini_hochberg
from .lab import data_hash
from .registry import Registry, code_version

SB_WIN, SB_CTRL = (3, 10, 14), (5, 12, 16)


def race(mk: Market, t: pd.Timestamp, price: float, direction: int, a: float, hours=24.0) -> str:
    """Course de barrières depuis `price` : 'cont' si +1 ATR dans `direction` d'abord, 'rev' sinon ;
    même minute → 'rev' (défavorable à la continuation)."""
    k = mk.idx(t)
    kend = mk.idx(t + pd.Timedelta(hours=hours))
    hh, ll = mk.h[k:kend], mk.l[k:kend]
    up, dn = price + a, price - a
    a_hit = np.flatnonzero(hh >= up) if direction == 1 else np.flatnonzero(ll <= dn)
    b_hit = np.flatnonzero(ll <= dn) if direction == 1 else np.flatnonzero(hh >= up)
    ia = a_hit[0] if len(a_hit) else None
    ib = b_hit[0] if len(b_hit) else None
    if ia is None and ib is None:
        return "timeout"
    if ib is not None and (ia is None or ib <= ia):
        return "rev"
    return "cont"


def orb_events(mk: Market, or_start: str, or_end: str, win_end: str) -> pd.DataFrame:
    rows = []
    m5c, m5h, m5l = mk.m5["c"].to_numpy(), mk.m5["h"].to_numpy(), mk.m5["l"].to_numpy()
    for d in mk.ny_days:
        a, b, e = ny(d, or_start), ny(d, or_end), ny(d, win_end)
        hl = mk.window_hl(a, b)
        if hl is None:
            continue
        hi, lo = hl
        j0 = int(np.searchsorted(mk.m5_avail, b.value, side="right"))
        j1 = int(np.searchsorted(mk.m5_avail, e.value, side="right"))
        for j in range(j0, j1):
            dirn = 1 if m5c[j] > hi else (-1 if m5c[j] < lo else 0)
            if dirn == 0:
                continue
            t = mk.m5["avail"].iat[j]
            A = mk.atr_h1_at(t)
            if not np.isfinite(A):
                break
            r = race(mk, t, float(m5c[j]), dirn, A)
            edge = hi if dirn == 1 else lo
            nxt = slice(j + 1, j + 7)
            retest = bool((m5l[nxt] <= edge).any()) if dirn == 1 else bool((m5h[nxt] >= edge).any())
            rows.append({"status": "ok", "touched": True, "avail": t, "race": r, "dir": dirn, "retest": retest,
                         "break_size_atr": abs(m5c[j] - edge) / A})
            break
    return pd.DataFrame(rows)


def smt_events(btc: Market, eth: Market, left=2, right=2) -> pd.DataFrame:
    b, e = btc.h1.set_index("ts"), eth.h1.set_index("ts")
    j = b.join(e, lsuffix="_b", rsuffix="_e", how="inner").reset_index()
    out = []
    for side in (+1, -1):           # +1 : balayage d'un swing high (signal baissier) ; −1 : swing low (haussier)
        hb = j["h_b" if side == 1 else "l_b"].to_numpy(); lb_other = j["l_b" if side == 1 else "h_b"].to_numpy()
        he = j["h_e" if side == 1 else "l_e"].to_numpy()
        cb = j["c_b"].to_numpy()
        Hb, Lb = j["h_b"].to_numpy(), j["l_b"].to_numpy()
        He, Le = j["h_e"].to_numpy(), j["l_e"].to_numpy()
        shb, slb = swings(Hb, Lb, left, right)
        she, sle = swings(He, Le, left, right)
        lvl_b = last_confirmed_level(len(j), shb if side == 1 else slb, Hb if side == 1 else Lb, right)
        lvl_e = last_confirmed_level(len(j), she if side == 1 else sle, He if side == 1 else Le, right)
        used = set()
        for t in range(3, len(j)):
            L0 = lvl_b[t - 1]
            if not np.isfinite(L0) or L0 in used:
                continue
            swept = (hb[t] > L0 and cb[t] < L0) if side == 1 else (hb[t] < L0 and cb[t] > L0)
            if not swept:
                continue
            used.add(L0)
            E0 = lvl_e[t - 1]
            if not np.isfinite(E0):
                continue
            eth_ext = he[t - 2:t + 1].max() if side == 1 else he[t - 2:t + 1].min()
            smt = bool(eth_ext <= E0) if side == 1 else bool(eth_ext >= E0)
            tav = j["avail_b"].iat[t] if "avail_b" in j else j["ts"].iat[t] + pd.Timedelta(hours=1)
            A = btc.atr_h1_at(tav)
            if not np.isfinite(A):
                continue
            r = race(btc, tav, float(cb[t]), -side, A)   # retournement attendu = sens opposé au balayage
            out.append({"status": "ok", "touched": True, "avail": tav, "smt": smt,
                        "race": "rev" if r == "cont" else ("cont" if r == "rev" else "timeout")})
    return pd.DataFrame(out)


def run(toml_path: str, symbol: str = "BTCUSDT", only: list[str] | None = None) -> dict:
    spec = tomllib.loads(Path(toml_path).read_text())
    common = spec["common"]
    p0, p1 = PERIODS["dev"]
    reg = Registry()
    for fam, b in spec.get("budget", {}).items():
        if reg.con.execute("SELECT 1 FROM budgets WHERE family=?", (fam,)).fetchone() is None:
            reg.set_budget(fam, int(b["max_trials"]), b["justification"])
    for t in spec["test"]:
        reg.register_hypothesis({"key": t["key"], "family": "NLI-EV", "statement": t["level"], "rationale": t["claim"],
                                 "params": {"primary": t["primary"], "doc": t["doc"]},
                                 "data": {"period": "dev", "symbols": common["symbols"]},
                                 "metrics": common["metrics"], "rejection": {"text": common["rejection"]}})
    t_start = time.time()
    mk = Market(signal_frame(load_bars(symbol, p0, p1)))
    dh = data_hash([symbol], range(p0.year, p1.year + 1))
    print(f"[{symbol}] données prêtes ({time.time() - t_start:.0f} s)", flush=True)
    sw = swing_levels(mk, 2, 2)
    recs = fvg_records(mk)
    fvg_lv = fvg_levels(mk, recs)
    results = {}

    def standard(key, levels, primary, race_h=24.0, seed=0, secondary=True):
        # Amendement 3-01a : contrôles décalés pour le contact, contrôles de distance pour la réaction
        nc = common["n_controls"]
        real_d, ctrl_d = run_levels(mk, levels, n_controls=nc, seed=seed, race_h=race_h, control_mode="distance")
        if primary == "M_target" or secondary:
            real_t, ctrl_t = run_levels(mk, levels, n_controls=nc, seed=seed, race_h=race_h, control_mode="timeshift")
        if primary == "M_target":
            d = delta_test(real_t, ctrl_t, "touch", n_boot=common["n_boot"], seed=seed)
            d2 = delta_test(real_d, ctrl_d, "reversal", n_boot=2000, seed=seed)
            ctrl_sum = summarize(ctrl_t)
        else:
            d = delta_test(real_d, ctrl_d, "reversal", n_boot=common["n_boot"], seed=seed)
            d2 = delta_test(real_t, ctrl_t, "touch", n_boot=2000, seed=seed) if secondary else {"note": "non calculé (amendement 3-01a)"}
            ctrl_sum = summarize(ctrl_d)
        return {"primary": primary, "real": summarize(real_d), "ctrl": ctrl_sum, "delta": d, "delta_secondary": d2}

    plan = {
        "EV-01-PDHL": lambda: standard("EV-01", pd_levels(mk), "M_target"),
        "EV-02-PWHL": lambda: standard("EV-02", pw_levels(mk), "M_target", race_h=48),
        "EV-03-LONDON": lambda: standard("EV-03", session_levels(mk, "02:00", "05:00", "LONDON", 0, "05:00", "16:00"), "M_reaction"),
        "EV-04-PMRANGE": lambda: standard("EV-04", session_levels(mk, "13:30", "16:00", "PM", 1, "09:30", "16:00"), "M_reaction"),
        "EV-05-SWING": lambda: standard("EV-05", sw["swing"], "M_reaction", race_h=48),
        "EV-06-EQHL": lambda: standard("EV-06", sw["eq"], "M_target", race_h=48),
        "EV-08-FVG": lambda: standard("EV-08", fvg_lv, "M_reaction", secondary=False),
        "EV-09-IFVG": lambda: standard("EV-09", ifvg_levels(mk, recs), "M_reaction", secondary=False),
        "EV-11-UNICORN": lambda: standard("EV-11", unicorn_levels(mk, recs), "M_reaction"),
    }
    for t in spec["test"]:
        key = t["key"]
        if only and key not in only:
            continue
        tid = reg.start_trial(key, {"symbol": symbol}, symbol, "dev", 1.0, data_hash=dh, seed=0, purpose="selection")
        t1 = time.time()
        if key in plan:
            res = plan[key]()
        elif key == "EV-07-LRL":
            res = standard(key, sw["lrl"], "M_target", race_h=48)
            rl, _ = run_levels(mk, sw["lrl"], with_controls=False)
            rh, _ = run_levels(mk, sw["hrl"], with_controls=False)
            # LRL et HRL n'ont pas la même distribution de distances : comparaison brute, descriptive
            res["lrl_vs_hrl_touch"] = delta_test(rl, rh, "touch", n_boot=2000)
            res["hrl"] = summarize(rh)
        elif key == "EV-10-FPFVG":
            first, ctrl = fpfvg_split(mk, recs)
            rf, _ = run_levels(mk, first, with_controls=False)
            rc, _ = run_levels(mk, ctrl, with_controls=False)
            res = {"primary": "M_reaction", "real": summarize(rf), "ctrl": summarize(rc),
                   "delta": delta_test(rf, rc, "reversal", n_boot=common["n_boot"]),
                   "delta_secondary": delta_test(rf, rc, "touch", n_boot=2000)}
        elif key == "EV-12-ORB":
            real, ctrl = orb_events(mk, "09:30", "10:00", "12:00"), orb_events(mk, "03:30", "04:00", "06:00")
            res = {"primary": "M_continuation", "delta": delta_test(real, ctrl, "continuation", n_boot=common["n_boot"]),
                   "n_real": len(real), "n_ctrl": len(ctrl)}
            rr = real[real["race"].isin(["rev", "cont"])]
            res["p_cont_with_retest"] = float((rr[rr["retest"]]["race"] == "cont").mean()) if rr["retest"].any() else None
            res["p_cont_without_retest"] = float((rr[~rr["retest"]]["race"] == "cont").mean()) if (~rr["retest"]).any() else None
            res["n_with_retest"], res["n_without_retest"] = int(rr["retest"].sum()), int((~rr["retest"]).sum())
            res["retest_selection"] = delta_test(rr[~rr["retest"]], rr[rr["retest"]], "continuation", n_boot=2000)
            big = rr["break_size_atr"] >= rr["break_size_atr"].median()
            res["p_cont_big_break"] = float((rr[big]["race"] == "cont").mean())
            res["p_cont_small_break"] = float((rr[~big]["race"] == "cont").mean())
        elif key == "EV-13-SILVERBULLET":
            real_all, _ = run_levels(mk, fvg_lv, with_controls=False)
            real_all = real_all.rename(columns={"x_form_hour_ny": "form_hour"})
            sb = real_all[real_all["form_hour"].isin(SB_WIN)]
            ct = real_all[real_all["form_hour"].isin(SB_CTRL)]
            res = {"primary": "M_reaction", "real": summarize(sb), "ctrl": summarize(ct),
                   "delta": delta_test(sb, ct, "reversal", n_boot=common["n_boot"]),
                   "by_window": {str(hh): summarize(real_all[real_all["form_hour"] == hh]) for hh in SB_WIN + SB_CTRL}}
        elif key == "EV-14-SMT":
            eth = Market(signal_frame(load_bars("ETHUSDT", p0, p1)))
            ev = smt_events(mk, eth)
            a, b = ev[ev["smt"]], ev[~ev["smt"]]
            res = {"primary": "M_reaction", "n_smt": int(len(a)), "n_no_smt": int(len(b)),
                   "p_rev_smt": float((a["race"] == "rev").mean()) if len(a) else None,
                   "p_rev_no_smt": float((b["race"] == "rev").mean()) if len(b) else None,
                   "delta": delta_test(a, b, "reversal", n_boot=common["n_boot"])}
        else:
            raise KeyError(key)
        d = res["delta"]
        reg.finish_trial(tid, status="done", n_trades=int(d.get("n_real", 0)), mean_r=d.get("delta"), p_value=d.get("p"),
                         result={"delta": d.get("delta"), "p": d.get("p")})
        res["trial_id"] = tid
        results[key] = res
        print(f"  {key:20s} Δ={d.get('delta', np.nan):+.4f} IC95={d.get('ci95')} p={d.get('p', np.nan):.4f} "
              f"n={d.get('n_real')}/{d.get('n_ctrl')} ({time.time() - t1:.0f} s)", flush=True)
    keys = [k for k in results if np.isfinite(results[k]["delta"].get("p", np.nan))]
    padj = benjamini_hochberg([results[k]["delta"]["p"] for k in keys]) if keys else []
    for k, pa in zip(keys, padj):
        r = results[k]
        r["p_bh"] = float(pa)
        info = pa < 0.05 and r["delta"]["delta"] >= 0.05
        r["information"] = bool(info)
        if r["primary"] == "M_reaction" and "real" in r:
            pr, pb = r["real"].get("p_reversal"), r["real"].get("p_breakeven_reversal")
            r["exploitable"] = bool(info and pr is not None and pb is not None and pr > pb)
        else:
            r["exploitable"] = None
    out = {"symbol": symbol, "code_version": code_version(), "registry_trials_total": reg.n_trials(), "results": results}
    d = RESULTS_DIR / "batch_3_01_events"; d.mkdir(parents=True, exist_ok=True)
    (d / f"events_{symbol}.json").write_text(json.dumps(out, indent=2, default=str, ensure_ascii=False))
    return out


if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "BTCUSDT")
