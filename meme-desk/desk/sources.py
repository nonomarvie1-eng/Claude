"""Sources de données.

- DemoSource : marché synthétique (pour tester sans réseau). Beaucoup de rugs,
  des pumps qui retombent, peu de vrais runners — comme le vrai marché.
- LiveSource : DexScreener (API publique) + RPC Solana. Lecture seule, aucune clé privée.
"""
from __future__ import annotations

import json
import math
import random
import time
import urllib.error
import urllib.request

from .models import Token

UA = "meme-desk/0.1 (paper-trading research)"


# ---------------------------------------------------------------- démo
class _SimToken:
    __slots__ = ("t", "fate", "phase_end", "rug_at", "alive", "drift_up", "drift_down", "vol")


class DemoSource:
    STEP_SECONDS = 15.0

    def __init__(self, seed: int | None = None, rate: float = 11.0):
        self.rng = random.Random(seed)
        self.rate = rate                    # nouveaux tokens par pas de 15 s
        self.clock = time.time()
        self.sims: dict[str, _SimToken] = {}

    def now(self) -> float:
        return self.clock

    def advance(self) -> None:
        self.clock += self.STEP_SECONDS
        for s in self.sims.values():
            self._step(s)
        # oublie les vieux tokens
        cutoff = self.clock - 3 * 3600
        for m in [m for m, s in self.sims.items() if s.t.created_at < cutoff]:
            del self.sims[m]

    def _poisson(self, lam: float) -> int:
        l, k, p = math.exp(-lam), 0, 1.0
        while True:
            p *= self.rng.random()
            if p <= l:
                return k
            k += 1

    def _symbol(self) -> str:
        syl = ["JAS", "TOR", "TEL", "MAN", "SOR", "VIN", "REN", "DAL", "QUO", "RIL", "PIN",
               "DOR", "ZIL", "KA", "BOL", "SUN", "CRE", "VAN", "WEX", "LAN", "HAR", "VEL",
               "YEL", "ZOR", "TEL", "MO", "PEP", "BON", "NEK", "FLO", "GRU", "BIX"]
        return "".join(self.rng.choice(syl) for _ in range(self.rng.choice((2, 2, 3))))[:7]

    def new_tokens(self) -> list[Token]:
        r = self.rng
        out = []
        for _ in range(self._poisson(self.rate)):
            mint = "".join(r.choice("123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz")
                           for _ in range(44))
            liq = r.lognormvariate(math.log(18_000), 1.0)
            mint_ok = r.random() < 0.75
            freeze_ok = r.random() < 0.82
            lp_ok = r.random() < 0.7
            top10 = min(95.0, r.lognormvariate(math.log(26), 0.45))
            dev = r.lognormvariate(math.log(2.5), 0.8)
            bundled = r.lognormvariate(math.log(5), 0.9)
            safe = mint_ok and freeze_ok and lp_ok and top10 < 25 and dev < 3 and bundled < 10
            rug_p = 0.15 if safe else 0.5
            u = r.random()
            fate = "rug" if u < rug_p else "runner" if u < rug_p + 0.07 else \
                "pump" if u < rug_p + 0.5 else "bleed"
            good = fate in ("runner", "pump")
            buys = r.randint(80, 900)
            share = min(0.85, max(0.3, r.gauss(0.6 if good else 0.5, 0.08)))
            sells = int(buys * (1 - share) / share)
            t = Token(
                mint=mint, symbol=self._symbol(), dex=r.choice(["pumpswap", "raydium"]),
                created_at=self.clock - r.uniform(60, 120 * 60),
                price_usd=r.lognormvariate(math.log(0.0004), 1.2),
                liquidity_usd=liq, volume_h1=liq * r.lognormvariate(math.log(1.6), 0.7),
                price_change_h1=r.gauss(25 if good else 5, 35), buys_h1=buys, sells_h1=sells,
                has_socials=r.random() < (0.7 if good else 0.4),
                mint_authority_revoked=mint_ok, freeze_authority_revoked=freeze_ok,
                lp_locked=lp_ok, top10_pct=top10, dev_pct=dev, bundled_pct=bundled,
                enriched=True,
            )
            t.market_cap = t.price_usd * 1e9
            s = _SimToken()
            s.t, s.fate, s.alive = t, fate, True
            s.phase_end = self.clock + r.uniform(4, 25 if fate != "runner" else 70) * 60
            s.rug_at = self.clock + r.uniform(2, 40) * 60 if fate == "rug" else math.inf
            s.drift_up = {"runner": 0.014, "pump": 0.006, "rug": 0.004, "bleed": -0.002}[fate]
            s.drift_down = {"runner": -0.004, "pump": -0.009, "rug": -0.006, "bleed": -0.005}[fate]
            s.vol = r.uniform(0.03, 0.06)
            self.sims[mint] = s
            out.append(t)
        return out

    def _step(self, s: _SimToken) -> None:
        t = s.t
        if not s.alive:
            return
        if self.clock >= s.rug_at:
            t.price_usd *= self.rng.uniform(0.01, 0.06)
            t.liquidity_usd *= 0.02
            s.alive = False
            return
        drift = s.drift_up if self.clock < s.phase_end else s.drift_down
        ret = drift + self.rng.gauss(0, s.vol)
        if self.rng.random() < 0.01:          # mèche violente occasionnelle
            ret += self.rng.choice((-1, 1)) * self.rng.uniform(0.1, 0.3)
        t.price_usd *= math.exp(ret)
        t.liquidity_usd *= math.exp(ret / 2)  # x*y=k : la liquidité suit sqrt(prix)

    def enrich(self, t: Token) -> None:
        t.enriched = True

    def quotes(self, mints: list[str]) -> dict[str, tuple[float, float]]:
        return {m: (self.sims[m].t.price_usd, self.sims[m].t.liquidity_usd)
                for m in mints if m in self.sims}


# ---------------------------------------------------------------- live
def _http_json(url: str, payload: dict | None = None, retries: int = 3):
    data = json.dumps(payload).encode() if payload is not None else None
    headers = {"User-Agent": UA, "Accept": "application/json"}
    if data:
        headers["Content-Type"] = "application/json"
    for i in range(retries):
        try:
            req = urllib.request.Request(url, data=data, headers=headers)
            with urllib.request.urlopen(req, timeout=12) as r:
                return json.loads(r.read())
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            if i == retries - 1:
                raise
            time.sleep(1.5 * (i + 1))


class LiveSource:
    DEX = "https://api.dexscreener.com"
    LP_BURNED_DEXES = {"pumpswap", "pumpfun"}   # pump.fun brûle la LP à la migration

    def __init__(self, rpc_url: str, exclude_largest: int = 1):
        self.rpc_url = rpc_url
        self.exclude_largest = exclude_largest
        self.seen: set[str] = set()
        self.errors = 0

    def now(self) -> float:
        return time.time()

    def advance(self) -> None:
        pass

    def _pairs(self, mints: list[str]) -> dict[str, dict]:
        """Meilleure paire (liquidité max) par mint, où le mint est le base token."""
        best: dict[str, dict] = {}
        for i in range(0, len(mints), 30):
            chunk = mints[i:i + 30]
            pairs = _http_json(f"{self.DEX}/tokens/v1/solana/{','.join(chunk)}") or []
            for p in pairs:
                m = (p.get("baseToken") or {}).get("address")
                if m not in chunk:
                    continue
                liq = float((p.get("liquidity") or {}).get("usd") or 0)
                if m not in best or liq > float((best[m].get("liquidity") or {}).get("usd") or 0):
                    best[m] = p
        return best

    def new_tokens(self) -> list[Token]:
        fresh: list[str] = []
        for path in ("/token-profiles/latest/v1", "/token-boosts/latest/v1"):
            try:
                items = _http_json(self.DEX + path) or []
            except Exception:
                self.errors += 1
                continue
            for it in items:
                m = it.get("tokenAddress")
                if it.get("chainId") == "solana" and m and m not in self.seen:
                    self.seen.add(m)
                    fresh.append(m)
        if not fresh:
            return []
        try:
            pairs = self._pairs(fresh)
        except Exception:
            self.errors += 1
            return []
        out = []
        for m, p in pairs.items():
            info = p.get("info") or {}
            txh1 = (p.get("txns") or {}).get("h1") or {}
            out.append(Token(
                mint=m, symbol=(p.get("baseToken") or {}).get("symbol", "?")[:10],
                dex=p.get("dexId", ""), pair=p.get("pairAddress", ""),
                created_at=(p.get("pairCreatedAt") or 0) / 1000,
                price_usd=float(p.get("priceUsd") or 0),
                liquidity_usd=float((p.get("liquidity") or {}).get("usd") or 0),
                volume_h1=float((p.get("volume") or {}).get("h1") or 0),
                price_change_h1=float((p.get("priceChange") or {}).get("h1") or 0),
                buys_h1=int(txh1.get("buys") or 0), sells_h1=int(txh1.get("sells") or 0),
                market_cap=float(p.get("marketCap") or p.get("fdv") or 0),
                has_socials=bool(info.get("socials") or info.get("websites")),
            ))
        return out

    def _rpc(self, method: str, params: list):
        r = _http_json(self.rpc_url, {"jsonrpc": "2.0", "id": 1, "method": method, "params": params})
        if "error" in r:
            raise RuntimeError(r["error"])
        return r["result"]

    def enrich(self, t: Token) -> None:
        """Lecture on-chain : autorités mint/freeze et concentration des holders."""
        t.enriched = True
        t.lp_locked = True if t.dex in self.LP_BURNED_DEXES else None
        try:
            acc = self._rpc("getAccountInfo", [t.mint, {"encoding": "jsonParsed"}])
            info = acc["value"]["data"]["parsed"]["info"]
            t.mint_authority_revoked = info.get("mintAuthority") is None
            t.freeze_authority_revoked = info.get("freezeAuthority") is None
            supply = int(info["supply"])
            largest = self._rpc("getTokenLargestAccounts", [t.mint])["value"]
            amounts = sorted((int(a["amount"]) for a in largest), reverse=True)
            holders = amounts[self.exclude_largest:self.exclude_largest + 10]
            t.top10_pct = 100 * sum(holders) / supply if supply else None
        except Exception as e:      # données inconnues → la règle stricte rejettera
            self.errors += 1
            t.extra["enrich_error"] = str(e)[:120]

    def quotes(self, mints: list[str]) -> dict[str, tuple[float, float]]:
        if not mints:
            return {}
        try:
            pairs = self._pairs(mints)
        except Exception:
            self.errors += 1
            return {}
        return {m: (float(p.get("priceUsd") or 0),
                    float((p.get("liquidity") or {}).get("usd") or 0)) for m, p in pairs.items()}
