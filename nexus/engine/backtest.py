"""Boucle de backtest : signaux → gestionnaire de risque → simulateur → journal.

Une seule position simultanée. Le capital utilisé pour dimensionner est le
capital réalisé courant (aucune position n'est ouverte au moment d'un signal).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from ..config import INITIAL_CAPITAL_EUR, RiskProfile
from ..instruments import InstrumentSpec
from .execution import ExecFrame, simulate
from .risk import RiskManager


class FxConverter:
    """Taux « unités de devise de cotation pour 1 EUR » à un instant donné.

    Toujours le dernier taux CONNU (horodatage de disponibilité <= instant), jamais futur.
    - USD  : EUR/USD (mid M1 Dukascopy, disponible à la clôture de la minute).
    - USDT : EUR/USDT Binance (clôture horaire, disponible à la fin de l'heure) —
             évite l'hypothèse 1 USDT = 1 USD.
    """

    def __init__(self, rates: dict | None = None, constant: float | None = None, max_age_days: float = 4.0):
        self.rates = rates or {}
        self.constant = constant
        self.max_age_ns = max_age_days * 86400e9

    @staticmethod
    def _series(df: pd.DataFrame, price_col, minutes: int):
        ts = (df["ts"] + pd.Timedelta(minutes=minutes)).dt.as_unit("ns").astype("int64").to_numpy()
        px = price_col(df) if callable(price_col) else df[price_col].to_numpy(float)
        return ts, np.asarray(px, float)

    @classmethod
    def build(cls, eurusd_m1: pd.DataFrame | None = None, eurusdt_h1: pd.DataFrame | None = None) -> "FxConverter":
        rates = {}
        if eurusd_m1 is not None:
            rates["USD"] = cls._series(eurusd_m1, lambda d: ((d["bid_c"] + d["ask_c"]) / 2).to_numpy(float), 1)
        if eurusdt_h1 is not None:
            rates["USDT"] = cls._series(eurusdt_h1, "c", 60)
        return cls(rates)

    def quote_per_eur(self, quote_ccy: str, t_ns: int) -> float:
        if quote_ccy == "EUR":
            return 1.0
        if self.constant is not None:
            return self.constant
        if quote_ccy not in self.rates:
            raise ValueError(f"conversion non disponible : {quote_ccy}")
        ts, px = self.rates[quote_ccy]
        i = int(np.searchsorted(ts, t_ns, side="right")) - 1
        if i < 0:
            raise ValueError("ANOMALIE : aucun taux de change disponible avant cet instant")
        if t_ns - ts[i] > self.max_age_ns:
            raise ValueError("ANOMALIE : taux de change périmé")
        return float(px[i])


@dataclass
class BacktestResult:
    trades: pd.DataFrame
    rejections: pd.DataFrame
    equity_daily: pd.Series
    final_equity: float
    halted: bool
    halt_reason: str


def fees_quote(spec: InstrumentSpec, qty: float, entry: float, exit_: float) -> float:
    m = spec.cost_multiplier
    return qty * (2 * spec.commission_per_unit_side * m) + spec.commission_rate_side * m * qty * (entry + exit_)


def run_backtest(signals: list, ex: ExecFrame, spec: InstrumentSpec, profile: RiskProfile,
                 fx: FxConverter, *, initial_equity: float = INITIAL_CAPITAL_EUR,
                 strategy: str = "", max_cost_frac: float = 0.33) -> BacktestResult:
    rm = RiskManager(profile, max_cost_frac_of_risk=max_cost_frac)
    equity = initial_equity
    rm.start(equity)
    busy_until = -1
    trades, rejections = [], []
    signals = sorted(signals, key=lambda s: s.avail)
    for s in signals:
        t_ns = int(s.avail.value)
        day = s.avail.tz_convert("UTC").date()
        rm.on_new_day(day, equity)
        if t_ns < busy_until:
            rejections.append({"avail": s.avail, "reason": "position déjà ouverte", **s.tags})
            continue
        if s.side == -1 and not spec.allow_short:
            rejections.append({"avail": s.avail, "reason": "vente à découvert impossible (spot)", **s.tags})
            continue
        try:
            q_per_eur = fx.quote_per_eur(spec.quote_ccy, t_ns)
        except ValueError as exc:
            rejections.append({"avail": s.avail, "reason": f"taux de change indisponible ({exc})", **s.tags})
            continue
        entry_est = s.entry_est if s.entry_est is not None else (s.limit_price or np.nan)
        dec = rm.size(spec, equity_eur=equity, quote_per_eur=q_per_eur, entry_est=entry_est, stop=s.stop)
        if not dec.accepted:
            rejections.append({"avail": s.avail, "reason": dec.reason, **s.tags})
            continue
        f = simulate(ex, spec, side=s.side, signal_avail=s.avail, stop=s.stop, target=s.target,
                     target_r=s.target_r, time_exit=s.time_exit, entry_type=s.entry_type,
                     limit_price=s.limit_price, expiry=s.expiry)
        if not f.filled:
            rejections.append({"avail": s.avail, "reason": "ordre non exécuté (expiré)", **s.tags})
            continue
        qty = dec.qty
        gross_q = s.side * (f.exit_price - f.entry_price) * qty
        fee_q = fees_quote(spec, qty, f.entry_price, f.exit_price)
        exit_ns = int(ex.ts[f.exit_idx])
        try:
            rate_exit = fx.quote_per_eur(spec.quote_ccy, exit_ns)
        except ValueError:
            rate_exit = q_per_eur   # taux de l'entrée (dernier connu), signalé
            s.tags = {**s.tags, "fx_fallback": True}
        pnl_eur = (gross_q - fee_q) / rate_exit
        fees_eur = fee_q / rate_exit
        risk_unit = abs(f.entry_price - s.stop)
        fee_unit = fee_q / qty
        r_net = (s.side * (f.exit_price - f.entry_price) - fee_unit) / risk_unit if risk_unit > 0 else np.nan
        r_gross = s.side * (f.exit_price - f.entry_price) / risk_unit if risk_unit > 0 else np.nan
        equity_before = equity
        equity += pnl_eur
        rm.on_trade_closed(pnl_eur, equity)
        busy_until = exit_ns + 1
        trades.append({
            "strategy": strategy, "symbol": spec.symbol, "signal_avail": s.avail,
            "entry_time": pd.Timestamp(int(ex.ts[f.entry_idx]), tz="UTC"),
            "exit_time": pd.Timestamp(exit_ns, tz="UTC"),
            "side": s.side, "qty": qty, "entry": f.entry_price, "exit": f.exit_price,
            "stop": s.stop, "exit_reason": f.reason, "ambiguous_bar": f.ambiguous_bar,
            "gap_during_trade": f.gap_during_trade,
            "r_net": r_net, "r_gross": r_gross, "pnl_eur": pnl_eur, "fees_eur": fees_eur,
            "risk_eur_planned": dec.risk_quote / q_per_eur, "equity_before": equity_before,
            "equity_after": equity, "cost_frac_est": dec.est_cost_frac_of_risk, **s.tags,
        })
        if rm.halted:
            # On journalise les signaux restants comme refusés (bot arrêté)
            pass
    tr = pd.DataFrame(trades)
    rj = pd.DataFrame(rejections)
    if len(tr):
        eq = tr.set_index("exit_time")["equity_after"]
        eq_daily = eq.groupby(eq.index.floor("D")).last()
        first = signals[0].avail.floor("D") if signals else eq_daily.index[0]
        idx = pd.date_range(min(first, eq_daily.index[0]), eq_daily.index[-1], freq="D")
        eq_daily = eq_daily.reindex(idx).ffill().fillna(initial_equity)
    else:
        eq_daily = pd.Series(dtype=float)
    return BacktestResult(tr, rj, eq_daily, equity, rm.halted, rm.halt_reason)
