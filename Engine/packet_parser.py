"""Packet parsing and formatting for the War Galley TCP bridge.

Validates incoming packets against JSON Schema before processing.
Uses HMAC-SHA256 for integrity verification (FIPS 140-2).
"""
import json
import logging
from pathlib import Path

import jsonschema

from logger_config import get_logger
from security_utils import SecurityManager

logger = get_logger(__name__)

# Load schemas once at import time
_SCHEMA_DIR = Path(__file__).parent / "schemas"

def _load_schema(filename: str) -> dict:
    """Load a JSON schema file from the schemas directory."""
    schema_path = _SCHEMA_DIR / filename
    return json.loads(schema_path.read_text(encoding="utf-8"))

_SCENARIO_SCHEMA: dict = _load_schema("scenario_schema.json")
_ACTION_SCHEMA: dict = _load_schema("action_schema.json")

_SCHEMAS: dict[str, dict] = {
    "INIT_SCENARIO": _SCENARIO_SCHEMA,
    "PLAYER_ACTION": _ACTION_SCHEMA,
}


class PacketParser:
    """Parses and formats signed JSON packets exchanged with Unity clients."""

    def __init__(self) -> None:
        self.security = SecurityManager()

    def parse_client_message(self, raw_data: bytes) -> dict | None:
        """Decode raw bytes, validate schema, verify HMAC, return payload.

        Returns the verified data payload dict, or None on any failure.
        Failures are logged; no exception propagates to the caller.
        """
        try:
            message_str = raw_data.decode("utf-8")
            packet = json.loads(message_str)

            packet_type: str = packet.get("type", "")
            schema = _SCHEMAS.get(packet_type)
            if schema is None:
                logger.error("Unknown packet type received: '%s'. Dropping.", packet_type)
                return None

            # Schema validation (OWASP Input Validation)
            try:
                jsonschema.validate(instance=packet, schema=schema)
            except jsonschema.ValidationError as exc:
                logger.error("Schema validation failed for '%s': %s", packet_type, exc.message)
                return None

            payload = packet.get("data")
            received_sig = packet.get("signature")

            # HMAC integrity check (FIPS 140-2)
            if not self.security.verify_scenario(payload, received_sig):
                logger.warning(
                    "SECURITY ALERT: Invalid HMAC signature for packet type '%s'. Dropping.",
                    packet_type,
                )
                return None

            logger.info("Packet '%s' validated successfully.", packet_type)
            return packet  # Return full packet so caller can branch on type

        except json.JSONDecodeError:
            logger.error("Failed to decode JSON from client.")
        except Exception as exc:
            logger.error("Unexpected error in packet parsing: %s", exc)

        return None

    def format_server_update(self, game_state: list | dict) -> bytes:
        """Sign and encode an outgoing game state for the Unity client."""
        payload_str = json.dumps(game_state)
        signature = self.security.generate_signature(payload_str)
        packet = {"data": game_state, "signature": signature}
        return (json.dumps(packet) + "\n").encode("utf-8")
