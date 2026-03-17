"""Security utilities: HMAC-SHA256 signing and scenario signature management."""
import argparse
import hmac
import hashlib
import json
import logging
import os
import tempfile
from pathlib import Path
from dotenv import load_dotenv, set_key

load_dotenv()

logger = logging.getLogger(__name__)

MIN_KEY_LENGTH: int = 32


class SecurityManager:
    """Manages HMAC-SHA256 signing and verification for FIPS 140-2 compliance."""

    def __init__(self) -> None:
        raw_key = os.getenv("HMAC_KEY")
        if not raw_key:
            raise EnvironmentError(
                "HMAC_KEY is not set. Copy .env.example to .env and set a "
                f"{MIN_KEY_LENGTH}-character key."
            )
        if len(raw_key) < MIN_KEY_LENGTH:
            raise ValueError(
                f"HMAC_KEY must be at least {MIN_KEY_LENGTH} characters. "
                f"Got {len(raw_key)}."
            )
        self._key: bytes = raw_key.encode()

    def generate_signature(self, data_string: str) -> str:
        """Generates HMAC-SHA256 signature for NIST compliance."""
        return hmac.new(self._key, data_string.encode(), hashlib.sha256).hexdigest()

    def verify_scenario(self, data: object, signature: str) -> bool:
        """Validates JSON integrity before execution."""
        expected = self.generate_signature(str(data))
        return hmac.compare_digest(expected, signature)

    def rotate_keys(self, new_key: str) -> None:
        """Rotate the HMAC key: validate, update .env, re-sign all scenarios.

        The old key value is never logged. Only the rotation event is recorded.
        """
        if len(new_key) < MIN_KEY_LENGTH:
            raise ValueError(
                f"New HMAC_KEY must be at least {MIN_KEY_LENGTH} characters."
            )
        env_path = Path(".env")
        if not env_path.exists():
            raise FileNotFoundError(".env file not found. Cannot rotate key.")
        set_key(str(env_path), "HMAC_KEY", new_key)
        # Reload env so subsequent operations use the new key
        load_dotenv(override=True)
        self._key = new_key.encode()
        logger.info("HMAC key rotation completed. Re-signing all scenarios.")
        _sign_all_scenarios(self)


SCENARIOS_DIR: Path = Path("Scenarios")
SIGNATURES_DB: Path = SCENARIOS_DIR / "signatures.db"


def _sign_all_scenarios(sm: SecurityManager) -> None:
    """Sign every JSON scenario file and write results to signatures.db."""
    signatures: dict[str, str] = {}
    for scenario_file in SCENARIOS_DIR.glob("*.json"):
        content = scenario_file.read_text(encoding="utf-8")
        sig = sm.generate_signature(content)
        signatures[scenario_file.name] = sig
        logger.info("Signed scenario: %s", scenario_file.name)

    # Atomic write: write to temp then rename
    tmp_fd, tmp_path = tempfile.mkstemp(
        dir=SCENARIOS_DIR, prefix=".signatures_", suffix=".tmp"
    )
    try:
        with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
            json.dump(signatures, f, indent=2)
        os.replace(tmp_path, SIGNATURES_DB)
        # Restrict to owner read/write only (FIPS requirement)
        os.chmod(SIGNATURES_DB, 0o600)
    except Exception:
        os.unlink(tmp_path)
        raise
    logger.info("signatures.db written with %d entries.", len(signatures))


if __name__ == "__main__":  # pragma: no cover
    parser = argparse.ArgumentParser(
        description="War Galley security utility CLI."
    )
    parser.add_argument(
        "--sign-all",
        action="store_true",
        help="Sign all scenario JSON files and write signatures.db.",
    )
    args = parser.parse_args()

    if args.sign_all:
        sm = SecurityManager()
        _sign_all_scenarios(sm)
        print(f"[+] Signed all scenarios. DB written to {SIGNATURES_DB}")