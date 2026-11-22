import unittest

from desk.analyst import score
from desk.broker import PaperBroker
from desk.config import Config
from desk.engine import Desk
from desk.filters import run_filter
from desk.models import Token
from desk.sources import DemoSource

NOW = 1_700_000_000.0


def good_token(**kw):
    base = dict(mint="M", symbol="GOOD", dex="pumpswap", created_at=NOW - 20 * 60,
                price_usd=0.001, liquidity_usd=150_000, volume_h1=200_000, price_change_h1=25,
                buys_h1=700, sells_h1=350, has_socials=True, mint_authority_revoked=True,
                freeze_authority_revoked=True, lp_locked=True, top10_pct=12, dev_pct=1,
                bundled_pct=2, enriched=True)
    base.update(kw)
    return Token(**base)


def nop(_):
    pass


class FilterTests(unittest.TestCase):
    def setUp(self):
        self.c = Config()

    def test_good_token_passes(self):
        self.assertIsNone(run_filter(good_token(), self.c, NOW, nop))

    def test_rules(self):
        cases = {
            "liq_vol": dict(liquidity_usd=10_000),
            "mint_freeze": dict(mint_authority_revoked=False),
            "lp": dict(lp_locked=False),
            "top10": dict(top10_pct=40),
            "dev_bundle": dict(bundled_pct=20),
            "late": dict(price_change_h1=150),
        }
        for rule, kw in cases.items():
            self.assertEqual(run_filter(good_token(**kw), self.c, NOW, nop)[0], rule, rule)

    def test_strict_rejects_unknown(self):
        t = good_token(lp_locked=None)
        self.assertEqual(run_filter(t, self.c, NOW, nop)[0], "lp")
        self.c.reject_unknown = False
        self.assertIsNone(run_filter(t, self.c, NOW, nop))

    def test_enrich_called_only_after_market_rules(self):
        calls = []
        run_filter(good_token(liquidity_usd=1, enriched=False), self.c, NOW, calls.append)
        self.assertEqual(calls, [])
        run_filter(good_token(enriched=False), self.c, NOW, calls.append)
        self.assertEqual(len(calls), 1)


class AnalystTests(unittest.TestCase):
    def test_range_and_order(self):
        hi, _ = score(good_token(), NOW)
        lo, _ = score(good_token(buys_h1=100, sells_h1=400, price_change_h1=-30,
                                 has_socials=False, top10_pct=24), NOW)
        self.assertTrue(0 <= lo < hi <= 100)
        self.assertGreaterEqual(hi, 70)


class BrokerTests(unittest.TestCase):
    def setUp(self):
        self.c = Config()
        self.b = PaperBroker(self.c)

    def test_sizing_and_costs(self):
        p = self.b.buy("M", "X", 1.0, 100_000, 80, NOW)
        self.assertAlmostEqual(p.size_eur, self.c.start_capital_eur * 0.08)
        self.assertGreater(p.entry_price, 1.0)              # slippage payé
        self.assertLess(self.b.equity(), self.c.start_capital_eur)  # frais immédiats

    def test_stop_gap_and_trail(self):
        p = self.b.buy("M", "X", 1.0, 100_000, 80, NOW)
        self.b.mark("M", p.entry_price * 0.80)
        self.assertEqual(self.b.exit_reason(p, NOW), "stop")
        rec = self.b.sell("M", "stop", NOW)
        self.assertLess(rec["pnl_pct"], -20)                 # le gap n'est pas masqué
        p = self.b.buy("N", "Y", 1.0, 100_000, 80, NOW)
        self.b.mark("N", p.entry_price * 1.5)
        self.assertIsNone(self.b.exit_reason(p, NOW))
        self.b.mark("N", p.entry_price * 1.5 * 0.84)
        self.assertEqual(self.b.exit_reason(p, NOW), "trail")

    def test_max_positions(self):
        for i in range(10):
            self.b.buy(str(i), "X", 1.0, 100_000, 80, NOW)
        self.assertEqual(len(self.b.positions), self.c.max_open_positions)


class EngineTests(unittest.TestCase):
    def test_demo_hour_is_consistent(self):
        d = Desk(Config(), DemoSource(seed=3), "demo")
        for _ in range(240):
            d.tick()
        s = d.state()
        c = s["counts"]
        self.assertEqual(c["scanned"], c["rejected"] + c["passed"])
        self.assertEqual(sum(k["n"] for k in s["kills"]), c["rejected"])
        self.assertAlmostEqual(s["equity"], d.broker.cash + sum(p["value_eur"] for p in s["positions"]))
        self.assertTrue(s["paper"])


if __name__ == "__main__":
    unittest.main()
