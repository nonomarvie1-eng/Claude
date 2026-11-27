"""Spécifications d'instruments et de conditions d'exécution.

Chaque spécification décrit UN instrument tradé dans UN cadre d'exécution donné
(spot, CFD, future). On ne mélange jamais les données d'un instrument avec les
conditions d'exécution d'un autre.

Les valeurs marquées ASSUMPTION sont des hypothèses de travail raisonnables,
non vérifiées auprès d'un courtier précis ; elles sont toutes stressées
(coûts x1,5 et x2) dans les tests de robustesse.
"""
from __future__ import annotations

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class InstrumentSpec:
    symbol: str
    venue_kind: str            # "fx_cfd" | "crypto_spot" | "index_cfd" | "future"
    quote_ccy: str             # devise de cotation du P&L
    price_tick: float          # plus petit écart de prix
    qty_step: float            # pas de quantité (unités de l'actif de base)
    min_qty: float             # quantité minimale
    min_notional_quote: float  # notionnel minimal en devise de cotation
    commission_per_unit_side: float = 0.0   # en devise de cotation, par unité et par côté
    commission_rate_side: float = 0.0       # fraction du notionnel, par côté
    has_bid_ask: bool = True                 # données bid/ask réelles disponibles
    modeled_half_spread_frac: float = 0.0    # si pas de bid/ask : demi-spread modélisé (fraction du prix)
    slippage_market_frac: float = 0.0        # glissement ordres au marché (fraction du prix)
    slippage_stop_frac: float = 0.0          # glissement supplémentaire sur stop
    allow_short: bool = True
    max_leverage: float = 1.0
    volume_kind: str = "none"   # "tick" (nb de cotations, Forex) | "traded" (volume échangé réel)
    cost_multiplier: float = 1.0  # stress test des coûts (1, 1.5, 2)

    def stressed(self, mult: float) -> "InstrumentSpec":
        return replace(self, cost_multiplier=mult)


# EUR/USD en CFD/compte Forex de détail (UE).
# Données : Dukascopy bid/ask M1 (spread réel du flux Dukascopy).
EURUSD_CFD = InstrumentSpec(
    symbol="EURUSD",
    venue_kind="fx_cfd",
    quote_ccy="USD",
    price_tick=0.00001,
    qty_step=1_000.0,          # 0,01 lot
    min_qty=1_000.0,           # 0,01 lot = 1 000 EUR de nominal
    min_notional_quote=0.0,
    commission_per_unit_side=3.5 / 100_000,  # ASSUMPTION : 3,5 USD par lot standard et par côté (compte type ECN)
    has_bid_ask=True,
    slippage_market_frac=0.00001 / 1.1,      # ASSUMPTION : ~0,1 pip
    slippage_stop_frac=0.00002 / 1.1,        # ASSUMPTION : ~0,2 pip supplémentaire sur stop
    allow_short=True,
    max_leverage=30.0,         # plafond ESMA particuliers, paires majeures
    volume_kind="tick",        # le volume Dukascopy n'est PAS un volume échangé
)

# BTC/USDT au comptant (Binance spot), sans levier, sans vente à découvert.
BTCUSDT_SPOT = InstrumentSpec(
    symbol="BTCUSDT",
    venue_kind="crypto_spot",
    quote_ccy="USDT",
    price_tick=0.01,
    qty_step=0.00001,          # ASSUMPTION : filtre LOT_SIZE Binance (à revérifier via exchangeInfo)
    min_qty=0.00001,
    min_notional_quote=5.0,    # ASSUMPTION : filtre NOTIONAL Binance ~5 USDT
    commission_rate_side=0.001,  # 0,10 % par côté, tarif standard sans remise
    has_bid_ask=False,
    modeled_half_spread_frac=0.5e-4,   # ASSUMPTION : demi-spread 0,5 pb
    slippage_market_frac=1.0e-4,       # ASSUMPTION : 1 pb
    slippage_stop_frac=2.0e-4,         # ASSUMPTION : 2 pb supplémentaires sur stop
    allow_short=False,         # compte spot : pas de vente à découvert
    max_leverage=1.0,          # aucun levier pour les premiers tests crypto
    volume_kind="traded",
)

SPECS = {"EURUSD": EURUSD_CFD, "BTCUSDT": BTCUSDT_SPOT}
