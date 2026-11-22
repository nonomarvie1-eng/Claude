"""Le desk : 6 agents qui tournent à chaque tick.

Scout → Filter → Analyst → Executor → Risk → Logger
"""
from __future__ import annotations

import time
from collections import Counter, deque

from .analyst import score
from .broker import PaperBroker
from .config import Config
from .filters import RULE_LABELS, run_filter

AGENTS = [
    ("scout", "Scout", "nouvelles paires"),
    ("filter", "Filter", "règles d'élimination"),
    ("analyst", "Analyst", "score 0-100"),
    ("executor", "Executor", "% max par position"),
    ("risk", "Risk", "stop · trailing"),
    ("logger", "Logger", "une raison pour tout"),
]


class Desk:
    def __init__(self, cfg: Config, source, mode: str):
        self.cfg, self.src, self.mode = cfg, source, mode
        self.broker = PaperBroker(cfg)
        self.started_at = source.now()
        self.now = self.started_at
        self.counts = Counter(scanned=0, rejected=0, passed=0, traded=0, stops=0, logged=0)
        self.kills: Counter = Counter({k: 0 for k in RULE_LABELS})
        self.agents = {k: {"name": n, "sub": s, "last": "—", "stat": ""} for k, n, s in AGENTS}
        self.log: deque = deque(maxlen=80)
        self.history: list[tuple[float, float]] = [(self.now, cfg.start_capital_eur)]

    # ----------------------------------------------------------- helpers
    def _log(self, agent: str, msg: str) -> None:
        self.log.appendleft({"t": self.now - self.started_at, "agent": agent, "msg": msg})
        self.counts["logged"] += 1
        self.agents["logger"]["last"] = f"{agent.lower()} · {msg}"[:60]

    # ----------------------------------------------------------- tick
    def tick(self) -> None:
        c, src = self.cfg, self.src
        src.advance()
        self.now = src.now()

        # 1. Scout
        new = src.new_tokens()
        self.counts["scanned"] += len(new)
        self.agents["scout"]["last"] = f"{len(new)} nouvelles paires"

        # 2-3. Filter + Analyst
        candidates = []
        for t in new:
            kill = run_filter(t, c, self.now, src.enrich)
            if kill:
                rule, why = kill
                self.counts["rejected"] += 1
                self.kills[rule] += 1
                self.agents["filter"]["last"] = f"× ${t.symbol} {why}"
                self._log("FILTER", f"killed ${t.symbol} · {why}")
                continue
            s, _ = score(t, self.now)
            if s < c.min_score:
                self.counts["rejected"] += 1
                self.kills["score"] += 1
                self.agents["analyst"]["last"] = f"${t.symbol} score {s} < {c.min_score}"
                self._log("ANALYST", f"killed ${t.symbol} · score {s} < {c.min_score}")
                continue
            self.counts["passed"] += 1
            self.agents["analyst"]["last"] = f"${t.symbol} score {s} ≥ {c.min_score}"
            self._log("ANALYST", f"passed ${t.symbol} · score {s}")
            candidates.append((s, t))

        # 4. Executor (meilleurs scores d'abord)
        for s, t in sorted(candidates, key=lambda x: -x[0]):
            if not self.broker.can_open():
                self._log("EXECUTOR", f"skip ${t.symbol} · {c.max_open_positions} positions max")
                continue
            pos = self.broker.buy(t.mint, t.symbol, t.price_usd, t.liquidity_usd, s, self.now)
            if pos:
                self.counts["traded"] += 1
                self.agents["executor"]["last"] = f"bought ${t.symbol} {pos.size_eur:.2f} €"
                self._log("EXECUTOR", f"bought ${t.symbol} {pos.size_eur:.2f} € · score {s}")

        # 5. Risk
        open_mints = list(self.broker.positions)
        for m, (price, liq) in src.quotes(open_mints).items():
            self.broker.mark(m, price, liq)
        for m in open_mints:
            p = self.broker.positions[m]
            reason = self.broker.exit_reason(p, self.now)
            if reason:
                rec = self.broker.sell(m, reason, self.now)
                if reason == "stop":
                    self.counts["stops"] += 1
                label = {"stop": "stop", "trail": "trail", "time": "temps", "rug": "rug"}[reason]
                msg = f"{label} · sold ${rec['symbol']} {rec['pnl_eur']:+.2f} € ({rec['pnl_pct']:+.1f} %)"
                self.agents["risk"]["last"] = msg
                self._log("RISK", msg)

        self.history.append((self.now, self.broker.equity()))
        if len(self.history) > 1500:                       # garde le début, compresse le milieu
            self.history = self.history[:1] + self.history[1:-500:2] + self.history[-500:]

    # ----------------------------------------------------------- state
    def state(self) -> dict:
        c, b = self.cfg, self.broker
        eq = b.equity()
        closed = b.closed
        wins = [r for r in closed if r["pnl_eur"] > 0]
        a = self.agents
        a["scout"]["stat"] = f"{self.counts['scanned']} scannés"
        a["filter"]["stat"] = f"{self.counts['rejected'] - self.kills['score']} rejetés"
        a["analyst"]["stat"] = f"{self.counts['passed']} ≥ {c.min_score}"
        a["executor"]["stat"] = f"{self.counts['traded']} ouverts"
        a["risk"]["stat"] = f"{self.counts['stops']} stops"
        a["logger"]["stat"] = f"{self.counts['logged']} lignes"
        a["executor"]["sub"] = f"{c.max_position_pct:g} % max / position"
        a["risk"]["sub"] = f"−{c.stop_loss_pct:g} % stop · trailing"
        return {
            "mode": self.mode,
            "paper": True,
            "elapsed": self.now - self.started_at,
            "start_capital": c.start_capital_eur,
            "equity": eq,
            "cash": b.cash,
            "pnl": eq - c.start_capital_eur,
            "pnl_pct": (eq / c.start_capital_eur - 1) * 100,
            "multiple": eq / c.start_capital_eur,
            "peak_equity": max(e for _, e in self.history),
            "history": [[round(t - self.started_at, 1), round(e, 4)] for t, e in self.history],
            "counts": dict(self.counts),
            "agents": [dict(a[k], key=k) for k, *_ in AGENTS],
            "log": list(self.log)[:12],
            "kills": [{"rule": k, "label": RULE_LABELS[k], "n": n} for k, n in self.kills.items()],
            "positions": [{
                "symbol": p.symbol, "size_eur": p.size_eur, "value_eur": p.value_eur(c),
                "pnl_pct": p.pnl_pct(c), "score": p.score, "age": self.now - p.opened_at,
            } for p in b.positions.values()],
            "closed": [{k: r[k] for k in ("symbol", "pnl_eur", "pnl_pct", "reason")}
                       for r in closed[-8:][::-1]],
            "stats": {
                "trades": len(closed),
                "win_rate": 100 * len(wins) / len(closed) if closed else None,
                "best": max((r["pnl_eur"] for r in closed), default=None),
                "worst": min((r["pnl_eur"] for r in closed), default=None),
                "source_errors": getattr(self.src, "errors", 0),
            },
            "config": {"stop": c.stop_loss_pct, "size": c.max_position_pct,
                       "min_score": c.min_score, "max_open": c.max_open_positions},
            "server_time": time.time(),
        }
