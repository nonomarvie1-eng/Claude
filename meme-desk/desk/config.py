"""Paramètres du desk. Tout est surchargeable via un fichier JSON (--config)."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, fields


@dataclass
class Config:
    # --- Capital (paper uniquement) ---
    start_capital_eur: float = 107.30
    eur_usd: float = 1.08              # conversion pour comparer taille de position et liquidité USD

    # --- Filter : règles d'élimination ---
    min_liquidity_usd: float = 40_000
    min_volume_h1_usd: float = 50_000
    max_top10_pct: float = 25.0        # % de l'offre détenu par les 10 plus gros portefeuilles
    exclude_largest_holders: int = 1   # le plus gros compte est souvent le vault de la pool
    max_dev_pct: float = 3.0
    max_bundled_pct: float = 10.0
    max_pump_h1_pct: float = 80.0      # « déjà +80 % en 1 h » → trop tard
    max_age_min: float = 360.0         # on ne regarde que les paires récentes
    require_mint_revoked: bool = True
    require_freeze_revoked: bool = True
    require_lp_locked: bool = True
    reject_unknown: bool = True        # strict RM : une donnée on-chain inconnue = rejet

    # --- Analyst ---
    min_score: int = 70

    # --- Executor / Risk ---
    max_position_pct: float = 8.0      # % de l'equity par position
    min_position_eur: float = 2.0
    max_open_positions: int = 4
    stop_loss_pct: float = 6.0
    trail_activate_pct: float = 30.0   # le trailing stop s'arme à +30 %
    trail_pct: float = 15.0            # puis vend si -15 % depuis le plus haut
    max_hold_min: float = 45.0
    fee_pct: float = 1.0               # frais swap + priority fee, par côté
    base_slippage_pct: float = 0.5

    # --- Boucle ---
    poll_seconds: float = 10.0         # live
    rpc_url: str = "https://api.mainnet-beta.solana.com"

    @classmethod
    def load(cls, path: str | None) -> "Config":
        cfg = cls()
        if path:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            known = {f.name for f in fields(cls)}
            unknown = set(data) - known
            if unknown:
                raise ValueError(f"Clés inconnues dans {path}: {sorted(unknown)}")
            for k, v in data.items():
                setattr(cfg, k, v)
        return cfg

    def to_dict(self) -> dict:
        return asdict(self)
