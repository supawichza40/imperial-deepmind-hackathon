"""Privacy Gate's dev server: stdlib-only (no Flask install needed here).

Serves the static app and exposes three endpoints:
  GET  /                 -> app/static/gate/index.html
  GET  /static/<path>    -> app/static/**
  GET  /api/health       -> {"local_model": bool, "cloud": bool}
  POST /api/detect       -> {"spans": [...], "model", "elapsed_ms"}
  POST /api/reason       -> {"finding","explanation","draft","model"}

Run:
    python app/server.py [port]   (default 8000)
"""
from __future__ import annotations

import json
import mimetypes
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

APP_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(APP_DIR, "static")
GATE_INDEX = os.path.join(STATIC_DIR, "gate", "index.html")

sys.path.insert(0, os.path.dirname(APP_DIR))
sys.path.insert(0, APP_DIR)

from app.api.detect import detect  # noqa: E402
from app.api.reason import reason  # noqa: E402
from app.pipeline import LOCAL_MODEL, local_step  # noqa: E402

# Set once the pre-warm call below confirms gemma4:e2b actually answers.
_local_model_ready = False
_local_model_checked = threading.Event()


def _prewarm_local_model() -> None:
    global _local_model_ready
    try:
        local_step("hello", instruction="Reply with one word.")
        _local_model_ready = True
    except RuntimeError as e:
        print(f"[server] local model not reachable ({LOCAL_MODEL}): {e}", file=sys.stderr)
        _local_model_ready = False
    finally:
        _local_model_checked.set()


def _cloud_configured() -> bool:
    return bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):  # quieter default logging
        print(f"[server] {self.address_string()} - {fmt % args}")

    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b""
        if not raw:
            return {}
        return json.loads(raw.decode("utf-8"))

    def _serve_file(self, path: str) -> None:
        if not os.path.isfile(path):
            self._send_json(404, {"error": "not found"})
            return
        ctype, _ = mimetypes.guess_type(path)
        with open(path, "rb") as f:
            body = f.read()
        self.send_response(200)
        self.send_header("Content-Type", ctype or "application/octet-stream")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    # --- GET -------------------------------------------------------
    def do_GET(self) -> None:
        path = urlparse(self.path).path

        if path == "/":
            self._serve_file(GATE_INDEX)
            return

        if path == "/api/health":
            self._send_json(200, {
                "local_model": _local_model_ready,
                "cloud": _cloud_configured(),
            })
            return

        if path.startswith("/static/"):
            rel = path[len("/static/"):]
            full = os.path.normpath(os.path.join(STATIC_DIR, rel))
            if not full.startswith(STATIC_DIR):
                self._send_json(403, {"error": "forbidden"})
                return
            self._serve_file(full)
            return

        self._send_json(404, {"error": "not found"})

    # --- POST ------------------------------------------------------
    def do_POST(self) -> None:
        path = urlparse(self.path).path
        try:
            body = self._read_json_body()
        except json.JSONDecodeError:
            self._send_json(400, {"error": "invalid JSON body"})
            return

        if path == "/api/detect":
            text = str(body.get("text") or "")
            if not text:
                self._send_json(400, {"error": "missing 'text'"})
                return
            self._send_json(200, detect(text))
            return

        if path == "/api/reason":
            text = str(body.get("text") or "")
            if not text:
                self._send_json(400, {"error": "missing 'text'"})
                return
            result = reason(text)
            if "error" in result:
                self._send_json(503, result)
            else:
                self._send_json(200, result)
            return

        self._send_json(404, {"error": "not found"})


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    threading.Thread(target=_prewarm_local_model, daemon=True).start()
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"[server] listening on http://localhost:{port}")
    print(f"[server] pre-warming {LOCAL_MODEL} in the background ...")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
