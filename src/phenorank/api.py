"""Optional HTTP API. POST /rank returns a typed RankResponse. Not a diagnosis."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from phenorank import SAFETY_DISCLAIMER
from phenorank.rank import rank_text
from phenorank.schemas import MeasureName, RankResponse


def rank_from_payload(payload: dict[str, Any]) -> RankResponse:
    """Handle a JSON body. Every response states hypothesis generation."""

    text = payload.get("vignette") or payload.get("text")
    if not isinstance(text, str) or not text.strip():
        raise ValueError("JSON body must include a non-empty 'vignette' or 'text' field")
    measure = payload.get("measure", "phenomizer")
    if measure not in ("resnik", "phenomizer"):
        raise ValueError("measure must be 'resnik' or 'phenomizer'")
    polarity_aware = bool(payload.get("polarity_aware", True))
    chosen: MeasureName = "phenomizer" if measure == "phenomizer" else "resnik"
    result = rank_text(text, polarity_aware=polarity_aware, measure=chosen)
    result.disclaimer = SAFETY_DISCLAIMER
    return result


class RankHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:  # noqa: A003
        return

    def _write(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path.rstrip("/") in {"", "/health"}:
            self._write(
                200,
                {
                    "ok": True,
                    "disclaimer": SAFETY_DISCLAIMER,
                    "endpoints": ["POST /rank"],
                },
            )
            return
        self._write(404, {"error": "not found", "disclaimer": SAFETY_DISCLAIMER})

    def do_POST(self) -> None:  # noqa: N802
        if self.path.rstrip("/") != "/rank":
            self._write(404, {"error": "not found", "disclaimer": SAFETY_DISCLAIMER})
            return
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("JSON body must be an object")
            result = rank_from_payload(payload)
        except (ValueError, json.JSONDecodeError) as exc:
            self._write(400, {"error": str(exc), "disclaimer": SAFETY_DISCLAIMER})
            return
        dumped = result.model_dump()
        dumped["disclaimer"] = SAFETY_DISCLAIMER
        self._write(200, dumped)


def serve(host: str = "127.0.0.1", port: int = 8765) -> None:
    server = ThreadingHTTPServer((host, port), RankHandler)
    print(SAFETY_DISCLAIMER)
    print(f"POST /rank on http://{host}:{port}/rank  (research only, no credentials)")
    server.serve_forever()
