"""Synthetic app: messy Prometheus metrics + JSON logs for Alloy pipeline demos."""

from __future__ import annotations

import json
import random
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

LOG_PATH = Path("/logs/app.log")
ROUTES_REAL = ["/api/orders/1001", "/api/orders/1002", "/api/users/55", "/checkout"]
HEALTH = ["/health", "/ready"]

counters: dict[tuple[str, ...], int] = {}
lock = threading.Lock()


def bump(method: str, route: str, status: str, request_id: str, user_id: str) -> None:
    key = (method, route, status, request_id, user_id)
    with lock:
        counters[key] = counters.get(key, 0) + 1


def emit_log(level: str, method: str, path: str, status: int, request_id: str, msg: str) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(
        {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "level": level,
            "method": method,
            "path": path,
            "status": status,
            "request_id": request_id,
            "msg": msg,
            "service": "checkout",
        }
    )
    with LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def traffic_loop() -> None:
    while True:
        request_id = f"req-{random.randint(100000, 999999)}"
        user_id = f"u-{random.randint(1, 5000)}"
        roll = random.random()
        if roll < 0.25:
            path = random.choice(HEALTH)
            emit_log("info", "GET", path, 200, request_id, "ok")
            bump("GET", path, "200", request_id, user_id)
        elif roll < 0.40:
            path = random.choice(ROUTES_REAL)
            emit_log("debug", "GET", path, 200, request_id, "cache lookup")
            bump("GET", path, "200", request_id, user_id)
        elif roll < 0.90:
            path = random.choice(ROUTES_REAL)
            method = random.choice(["GET", "POST"])
            status = 200 if random.random() > 0.1 else 500
            level = "error" if status >= 500 else "info"
            emit_log(level, method, path, status, request_id, "handled")
            bump(method, path, str(status), request_id, user_id)
        else:
            bump("GET", "/metrics", "200", request_id, user_id)
        time.sleep(2)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        return

    def do_GET(self) -> None:
        if self.path != "/metrics":
            self.send_error(404)
            return
        with lock:
            snapshot = dict(counters)
        lines = [
            "# HELP http_requests_total Synthetic HTTP requests (intentionally high cardinality).",
            "# TYPE http_requests_total counter",
        ]
        for (method, route, status, request_id, user_id), value in snapshot.items():
            lines.append(
                "http_requests_total{"
                f'method="{method}",route="{route}",status="{status}",'
                f'request_id="{request_id}",user_id="{user_id}"'
                f"}} {value}"
            )
        lines.extend(
            [
                "# HELP noisy_debug_total Dropped entirely by prometheus.relabel.",
                "# TYPE noisy_debug_total counter",
                "noisy_debug_total 1",
                "# HELP app_up Generator heartbeat.",
                "# TYPE app_up gauge",
                "app_up 1",
            ]
        )
        body = ("\n".join(lines) + "\n").encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    threading.Thread(target=traffic_loop, daemon=True).start()
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
