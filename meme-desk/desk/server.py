"""Petit serveur HTTP : sert le tableau de bord et /api/state."""
from __future__ import annotations

import json
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

DASHBOARD = Path(__file__).resolve().parent.parent / "dashboard"


class _Handler(SimpleHTTPRequestHandler):
    get_state = None  # injecté

    def do_GET(self):
        if self.path.split("?")[0] == "/api/state":
            body = json.dumps(self.get_state()).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def log_message(self, *args):
        pass


def serve(get_state, host: str, port: int) -> ThreadingHTTPServer:
    handler = type("H", (_Handler,), {"get_state": staticmethod(get_state)})
    httpd = ThreadingHTTPServer((host, port), partial(handler, directory=str(DASHBOARD)))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd
