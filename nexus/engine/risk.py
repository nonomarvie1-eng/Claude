"""Gestionnaire de risque indépendant.

Il a le dernier mot sur chaque intention de trade. Il n'augmente JAMAIS le risque
après une perte (taille = fonction du seul capital courant et de la distance du
stop), ne renforce jamais une position et n'autorise qu'une position à la fois.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from ..config import RiskProfile
from ..instruments import InstrumentSpec


@dataclass
class SizingDecision:
    accepted: bool
    qty: float = 0.0
    risk_quote: float = 0.0          # perte estimée au stop, frais inclus, devise de cotation
    reason: str = ""
    est_cost_frac_of_risk: float = 0.0


def round_down(x: float, step: float) -> float:
    return math.floor(x / step + 1e-9) * step


def est_cost_per_unit(spec: InstrumentSpec, entry: float, stop: float) -> float:
    """Coût aller-retour estimé par unité (commissions + glissements), hors spread
    (le spread est déjà dans le prix d'entrée estimé au ask/bid)."""
    m = spec.cost_multiplier
    comm = 2 * spec.commission_per_unit_side * m + spec.commission_rate_side * m * (entry + stop)
    slip = spec.slippage_market_frac * m * entry + (spec.slippage_market_frac + spec.slippage_stop_frac) * m * stop
    if not spec.has_bid_ask:
        slip += spec.modeled_half_spread_frac * m * stop  # demi-spread payé en sortie
    return comm + slip


@dataclass
class RiskManager:
    profile: RiskProfile
    max_cost_frac_of_risk: float = 0.33   # refus si les coûts estimés dépassent 33 % du risque
    halted: bool = False
    halt_reason: str = ""
    peak_equity: float = 0.0
    day: object = None
    day_start_equity: float = 0.0
    day_pnl: float = 0.0
    log: list = field(default_factory=list)

    def start(self, equity: float) -> None:
        self.peak_equity = equity
        self.day_start_equity = equity

    def on_new_day(self, day, equity: float) -> None:
        if day != self.day:
            self.day = day
            self.day_start_equity = equity
            self.day_pnl = 0.0

    def on_trade_closed(self, pnl_eur: float, equity: float) -> None:
        self.day_pnl += pnl_eur
        self.peak_equity = max(self.peak_equity, equity)
        if equity <= self.peak_equity * (1 - self.profile.max_drawdown_halt):
            self.halted = True
            self.halt_reason = (f"drawdown {1 - equity / self.peak_equity:.2%} >= seuil "
                                f"{self.profile.max_drawdown_halt:.0%}")

    def emergency_stop(self, reason: str) -> None:
        self.halted = True
        self.halt_reason = f"arrêt d'urgence : {reason}"

    def size(self, spec: InstrumentSpec, *, equity_eur: float, quote_per_eur: float,
             entry_est: float, stop: float) -> SizingDecision:
        if self.halted:
            return SizingDecision(False, reason=f"bot arrêté ({self.halt_reason})")
        if not (equity_eur > 0 and quote_per_eur > 0):
            return SizingDecision(False, reason="ANOMALIE : capital ou taux de change invalide")
        limit = self.profile.daily_loss_limit * self.day_start_equity
        risk_eur = self.profile.risk_per_trade * equity_eur
        if -self.day_pnl + risk_eur > limit + 1e-9:
            return SizingDecision(False, reason="limite de perte journalière")
        dist = abs(entry_est - stop)
        if dist <= 0:
            return SizingDecision(False, reason="stop invalide")
        cost_u = est_cost_per_unit(spec, entry_est, stop)
        loss_per_unit = dist + cost_u
        budget_quote = risk_eur * quote_per_eur
        qty = round_down(budget_quote / loss_per_unit, spec.qty_step)
        # Plafond de levier (et 1:1 en spot)
        max_qty_lev = round_down(equity_eur * quote_per_eur * spec.max_leverage / entry_est, spec.qty_step)
        qty = min(qty, max_qty_lev)
        cost_frac = cost_u / dist
        if cost_frac > self.max_cost_frac_of_risk:
            return SizingDecision(False, reason=f"coûts estimés > {self.max_cost_frac_of_risk:.0%} du risque",
                                  est_cost_frac_of_risk=cost_frac)
        if qty < spec.min_qty - 1e-12:
            return SizingDecision(False, reason="taille inférieure au minimum de l'instrument",
                                  est_cost_frac_of_risk=cost_frac)
        if qty * entry_est < spec.min_notional_quote:
            return SizingDecision(False, reason="notionnel inférieur au minimum", est_cost_frac_of_risk=cost_frac)
        return SizingDecision(True, qty=qty, risk_quote=qty * loss_per_unit, est_cost_frac_of_risk=cost_frac)
