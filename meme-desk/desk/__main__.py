"""python -m desk --demo   |   python -m desk --live"""
from __future__ import annotations

import argparse
import json
import threading
import time

from .config import Config
from .engine import Desk
from .server import serve
from .sources import DemoSource, LiveSource

BANNER = "PAPER TRADING — aucun ordre réel, aucune clé privée. Ce n'est pas un conseil financier."


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(prog="desk", description="Meme Desk — scanner Solana en simulation.")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--demo", action="store_true", help="marché synthétique (hors ligne)")
    g.add_argument("--live", action="store_true", help="vraies données DexScreener + RPC Solana, trades fictifs")
    ap.add_argument("--config", help="fichier JSON qui surcharge les paramètres")
    ap.add_argument("--seed", type=int, help="graine du marché démo (reproductible)")
    ap.add_argument("--speed", type=float, default=4.0,
                    help="démo : ticks de 15 s simulés par seconde réelle (0 = max)")
    ap.add_argument("--duration-min", type=float, default=60.0, help="démo : durée simulée")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--no-server", action="store_true", help="pas de tableau de bord, résumé à la fin")
    ap.add_argument("--state-out", help="écrit aussi l'état final en JSON ici")
    a = ap.parse_args(argv)

    cfg = Config.load(a.config)
    if a.demo:
        src, mode = DemoSource(seed=a.seed), "demo"
    else:
        src, mode = LiveSource(cfg.rpc_url, cfg.exclude_largest_holders), "live"
    desk = Desk(cfg, src, mode)
    lock = threading.Lock()

    def get_state():
        with lock:
            return desk.state()

    print(BANNER)
    if not a.no_server:
        serve(get_state, a.host, a.port)
        print(f"Tableau de bord : http://{a.host}:{a.port}   (Ctrl+C pour arrêter)")

    end_sim = desk.started_at + a.duration_min * 60
    try:
        while True:
            if a.demo and src.now() >= end_sim:
                break
            t0 = time.time()
            with lock:
                desk.tick()
            if a.live:
                time.sleep(max(0.0, cfg.poll_seconds - (time.time() - t0)))
            elif a.speed > 0:
                time.sleep(max(0.0, 1 / a.speed - (time.time() - t0)))
        if not a.no_server:
            print("Session démo terminée — le tableau de bord reste affiché. Ctrl+C pour quitter.")
            while True:
                time.sleep(3600)
    except KeyboardInterrupt:
        pass
    finally:
        s = get_state()
        print(f"\nEquity {s['equity']:.2f} € ({s['pnl_pct']:+.1f} %) · "
              f"{s['counts']['scanned']} scannés · {s['counts']['traded']} trades · "
              f"win rate {s['stats']['win_rate'] or 0:.0f} %")
        if a.state_out:
            with open(a.state_out, "w", encoding="utf-8") as f:
                json.dump(s, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
