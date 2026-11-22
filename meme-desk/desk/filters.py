"""Agent Filter : règles d'élimination. Chaque règle renvoie un motif de rejet ou None."""
from __future__ import annotations

from typing import Callable

from .config import Config
from .models import Token

# Libellés affichés dans le panneau « Killed by rule »
RULE_LABELS = {
    "liq_vol": "Liq < 40 k · vol < 50 k",
    "mint_freeze": "Mint/freeze non révoqué",
    "lp": "LP non brûlée/lockée",
    "top10": "Top 10 holders > 25 %",
    "dev_bundle": "Dev > 3 % · bundle > 10 %",
    "late": "Déjà +80 % en 1 h",
    "score": "Score < 70",
}


def _fmt_k(x: float) -> str:
    return f"{x / 1000:.0f} k"


def market_rules(t: Token, c: Config, now: float) -> tuple[str, str] | None:
    """Règles qui ne demandent que les données de marché (pas d'appel RPC)."""
    if t.liquidity_usd < c.min_liquidity_usd:
        return "liq_vol", f"liq {_fmt_k(t.liquidity_usd)} < {_fmt_k(c.min_liquidity_usd)}"
    if t.volume_h1 < c.min_volume_h1_usd:
        return "liq_vol", f"vol 1h {_fmt_k(t.volume_h1)} < {_fmt_k(c.min_volume_h1_usd)}"
    if t.price_change_h1 > c.max_pump_h1_pct:
        return "late", f"déjà +{t.price_change_h1:.0f} % en 1 h"
    if t.created_at and (now - t.created_at) / 60 > c.max_age_min:
        return "liq_vol", "paire trop ancienne"
    return None


def onchain_rules(t: Token, c: Config) -> tuple[str, str] | None:
    """Règles de sécurité on-chain. En strict RM, une donnée inconnue = rejet."""
    def unknown(rule: str, what: str):
        return (rule, f"{what} non vérifiable") if c.reject_unknown else None

    if c.require_mint_revoked:
        if t.mint_authority_revoked is None:
            r = unknown("mint_freeze", "mint authority")
            if r:
                return r
        elif not t.mint_authority_revoked:
            return "mint_freeze", "mint non révoqué"
    if c.require_freeze_revoked:
        if t.freeze_authority_revoked is None:
            r = unknown("mint_freeze", "freeze authority")
            if r:
                return r
        elif not t.freeze_authority_revoked:
            return "mint_freeze", "freeze non révoqué"
    if c.require_lp_locked:
        if t.lp_locked is None:
            r = unknown("lp", "LP")
            if r:
                return r
        elif not t.lp_locked:
            return "lp", "LP non brûlée"
    if t.top10_pct is None:
        r = unknown("top10", "top 10 holders")
        if r:
            return r
    elif t.top10_pct > c.max_top10_pct:
        return "top10", f"top 10 holders {t.top10_pct:.0f} %"
    # dev / bundle : rarement disponibles gratuitement → ignorés si inconnus
    if t.dev_pct is not None and t.dev_pct > c.max_dev_pct:
        return "dev_bundle", f"dev détient {t.dev_pct:.0f} %"
    if t.bundled_pct is not None and t.bundled_pct > c.max_bundled_pct:
        return "dev_bundle", f"bundled launch {t.bundled_pct:.0f} %"
    return None


def run_filter(t: Token, c: Config, now: float,
               enrich: Callable[[Token], None]) -> tuple[str, str] | None:
    r = market_rules(t, c, now)
    if r:
        return r
    if not t.enriched:
        enrich(t)
    return onchain_rules(t, c)
