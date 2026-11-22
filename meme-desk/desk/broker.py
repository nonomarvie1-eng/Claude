"""Broker papier : exécute des ordres fictifs avec frais, slippage et impact de prix.

Aucun ordre réel n'est jamais envoyé. Les stops sont exécutés au prix observé
(si le prix a sauté sous le stop, la perte est plus grosse que -6 % : c'est réaliste).
"""
from __future__ import annotations

from dataclasses import asdict, dataclass

from .config import Config


@dataclass
class Position:
    mint: str
    symbol: str
    opened_at: float
    size_eur: float          # capital engagé (frais inclus)
    qty: float               # tokens reçus
    entry_price: float       # prix d'exécution USD
    peak_price: float
    last_price: float
    liquidity_usd: float
    score: int

    def value_eur(self, c: Config) -> float:
        gross_usd = self.qty * self.last_price
        impact = _impact(gross_usd, self.liquidity_usd)
        net_usd = gross_usd * (1 - impact - c.base_slippage_pct / 100) * (1 - c.fee_pct / 100)
        return max(0.0, net_usd / c.eur_usd)

    def pnl_pct(self, c: Config) -> float:
        return (self.value_eur(c) / self.size_eur - 1) * 100 if self.size_eur else 0.0


def _impact(usd: float, liquidity_usd: float) -> float:
    """Impact approx. d'une pool à produit constant : x / réserve côté quote (≈ liq/2)."""
    if liquidity_usd <= 0:
        return 1.0
    q = liquidity_usd / 2
    return min(0.99, usd / (q + usd))


class PaperBroker:
    def __init__(self, c: Config):
        self.c = c
        self.cash = c.start_capital_eur
        self.positions: dict[str, Position] = {}
        self.closed: list[dict] = []

    # --- lecture ---
    def equity(self) -> float:
        return self.cash + sum(p.value_eur(self.c) for p in self.positions.values())

    def can_open(self) -> bool:
        return len(self.positions) < self.c.max_open_positions

    # --- ordres ---
    def buy(self, mint: str, symbol: str, price_usd: float, liquidity_usd: float,
            score: int, now: float) -> Position | None:
        c = self.c
        if mint in self.positions or not self.can_open() or price_usd <= 0:
            return None
        size = min(self.equity() * c.max_position_pct / 100, self.cash)
        if size < c.min_position_eur:
            return None
        usd_in = size * (1 - c.fee_pct / 100) * c.eur_usd
        slip = _impact(usd_in, liquidity_usd) + c.base_slippage_pct / 100
        fill = price_usd * (1 + slip)
        pos = Position(mint, symbol, now, size, usd_in / fill, fill, price_usd,
                       price_usd, liquidity_usd, score)
        self.cash -= size
        self.positions[mint] = pos
        return pos

    def mark(self, mint: str, price_usd: float, liquidity_usd: float | None = None) -> None:
        p = self.positions.get(mint)
        if not p:
            return
        p.last_price = max(0.0, price_usd)
        p.peak_price = max(p.peak_price, p.last_price)
        if liquidity_usd is not None:
            p.liquidity_usd = liquidity_usd

    def exit_reason(self, p: Position, now: float) -> str | None:
        """Agent Risk : décide si on sort."""
        c = self.c
        ret = p.last_price / p.entry_price - 1
        if ret <= -c.stop_loss_pct / 100:
            return "stop"
        if p.peak_price >= p.entry_price * (1 + c.trail_activate_pct / 100) and \
                p.last_price <= p.peak_price * (1 - c.trail_pct / 100):
            return "trail"
        if (now - p.opened_at) / 60 >= c.max_hold_min:
            return "time"
        if p.liquidity_usd < 1_000:
            return "rug"
        return None

    def sell(self, mint: str, reason: str, now: float) -> dict | None:
        p = self.positions.pop(mint, None)
        if not p:
            return None
        proceeds = p.value_eur(self.c)
        self.cash += proceeds
        rec = asdict(p) | {
            "closed_at": now, "reason": reason, "proceeds_eur": proceeds,
            "pnl_eur": proceeds - p.size_eur,
            "pnl_pct": (proceeds / p.size_eur - 1) * 100 if p.size_eur else 0.0,
        }
        self.closed.append(rec)
        return rec
