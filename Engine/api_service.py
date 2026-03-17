"""Admin API service: telemetry endpoint with Bearer token authentication.

OWASP A07 — Authentication enforced on all routes via Bearer token.
OWASP A05 — Security headers injected on every response.
Reads live state from engine_state.json written by main.py each tick.
"""
import hmac
import json
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, request, Response

from logger_config import get_logger

load_dotenv()

logger = get_logger(__name__)

app = Flask(__name__)

# Path written by main.py after every tick (shared volume mount)
_ENGINE_STATE_PATH = Path(os.getenv("LOG_PATH", "./Engine/logs/security.log")).parent / "engine_state.json"

_ADMIN_KEY: str = os.getenv("ADMIN_API_KEY", "")


# ---------------------------------------------------------------------------
# Security helpers
# ---------------------------------------------------------------------------

def _check_auth(req) -> bool:
    """Validate Bearer token using constant-time comparison (timing-attack safe)."""
    if not _ADMIN_KEY:
        logger.critical("ADMIN_API_KEY is not set. All API requests will be rejected.")
        return False
    auth_header: str = req.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return False
    provided_token = auth_header[len("Bearer "):]
    return hmac.compare_digest(provided_token.encode(), _ADMIN_KEY.encode())


@app.after_request
def add_security_headers(response: Response) -> Response:
    """Inject OWASP-required HTTP security headers on every response."""
    response.headers["Content-Security-Policy"] = "default-src 'none'"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    return response


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/api/v1/telemetry", methods=["GET"])
def get_telemetry():
    """Return live engine telemetry. Requires Bearer token authentication."""
    if not _check_auth(request):
        logger.warning("Rejected unauthenticated telemetry request from %s", request.remote_addr)
        return Response(status=401)

    # Read live state written by main.py; fall back to safe defaults
    state: dict = _read_engine_state()
    logger.info("Telemetry served to %s", request.remote_addr)
    return jsonify(state)


def _read_engine_state() -> dict:
    """Read engine_state.json if present; return safe defaults if absent."""
    default = {
        "engine_running": False,
        "active_vessels": 0,
        "security_violations": 0,
        "current_turn": 0,
        "recent_logs": [],
    }
    try:
        if _ENGINE_STATE_PATH.exists():
            content = _ENGINE_STATE_PATH.read_text(encoding="utf-8")
            return json.loads(content)
    except (json.JSONDecodeError, OSError) as exc:
        logger.error("Failed to read engine_state.json: %s", exc)
    return default


if __name__ == "__main__":  # pragma: no cover
    app.run(host="127.0.0.1", port=8080, debug=False)
