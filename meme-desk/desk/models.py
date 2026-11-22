from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Token:
    """Un token candidat. None = donnée inconnue / non vérifiée."""
    mint: str
    symbol: str
    dex: str = ""
    pair: str = ""
    created_at: float = 0.0            # epoch secondes
    price_usd: float = 0.0
    liquidity_usd: float = 0.0
    volume_h1: float = 0.0
    price_change_h1: float = 0.0
    buys_h1: int = 0
    sells_h1: int = 0
    market_cap: float = 0.0
    has_socials: bool = False
    # On-chain (rempli par enrich)
    mint_authority_revoked: bool | None = None
    freeze_authority_revoked: bool | None = None
    lp_locked: bool | None = None
    top10_pct: float | None = None
    dev_pct: float | None = None
    bundled_pct: float | None = None
    enriched: bool = False
    extra: dict = field(default_factory=dict)
