"""Agent Analyst : note 0-100. Heuristique simple, volontairement lisible — pas une promesse de rendement."""
from __future__ import annotations

from .models import Token


def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def score(t: Token, now: float) -> tuple[int, dict]:
    parts: dict[str, float] = {}
    # Liquidité : 40 k → 0, 200 k+ → plein
    parts["liquidité"] = 20 * _clamp((t.liquidity_usd - 40_000) / 160_000)
    # Activité : volume 1h / liquidité, idéal entre 1 et 4
    ratio = t.volume_h1 / t.liquidity_usd if t.liquidity_usd else 0
    parts["activité"] = 20 * (_clamp(ratio / 1.0) if ratio <= 4 else _clamp(1 - (ratio - 4) / 6))
    # Pression acheteuse
    tx = t.buys_h1 + t.sells_h1
    buy_share = t.buys_h1 / tx if tx else 0.5
    parts["acheteurs"] = 20 * _clamp((buy_share - 0.45) / 0.2)
    # Distribution des holders
    if t.top10_pct is not None:
        parts["distribution"] = 15 * _clamp((25 - t.top10_pct) / 15)
    # Momentum sain : positif mais pas parabolique
    ch = t.price_change_h1
    parts["momentum"] = 15 * (_clamp(ch / 30) if ch <= 40 else _clamp(1 - (ch - 40) / 40))
    # Fraîcheur : 5-90 min idéal
    age_min = (now - t.created_at) / 60 if t.created_at else 999
    parts["âge"] = 5 * (_clamp(age_min / 5) if age_min < 5 else _clamp(1 - (age_min - 90) / 270))
    parts["socials"] = 5.0 if t.has_socials else 0.0
    total = int(round(sum(parts.values())))
    return max(0, min(100, total)), parts
