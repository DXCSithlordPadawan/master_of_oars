"""War Galley authoritative server: TCP socket listener and request dispatcher.

Integrates PacketParser, VesselFactory, WarGalleyEngine, and CombatResolver
into a single threaded server loop. Writes engine_state.json after each tick
for the admin dashboard (IPC via shared volume).
"""
import json
import os
import socket
import tempfile
import threading
from pathlib import Path

from dotenv import load_dotenv

from combat_resolver import CombatResolver
from logger_config import get_logger
from packet_parser import PacketParser
from vessel_factory import VesselFactory
from war_galley import WarGalleyEngine

load_dotenv()

logger = get_logger(__name__)

# Path of the IPC state file read by api_service.py
_STATE_PATH = Path(os.getenv("LOG_PATH", "./Engine/logs/security.log")).parent / "engine_state.json"


class WarGalleyServer:
    """TCP server: accepts Unity client connections and dispatches game ticks."""

    def __init__(self) -> None:
        self.host: str = os.getenv("SERVER_IP", "127.0.0.1")
        self.port: int = int(os.getenv("SERVER_PORT", 5555))
        self.max_connections: int = int(os.getenv("MAX_CONNECTIONS", 5))
        self.engine: WarGalleyEngine | None = None
        self.is_running: bool = True
        self._engine_lock = threading.Lock()
        self._parser = PacketParser()
        self._semaphore = threading.Semaphore(self.max_connections)

    # ------------------------------------------------------------------
    # Server lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Bind socket and accept connections in a loop. Each connection
        is handled on a daemon thread so the process exits cleanly."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
            srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            srv.bind((self.host, self.port))
            srv.listen()
            logger.info("Authoritative Engine listening on %s:%s", self.host, self.port)

            while self.is_running:
                try:
                    conn, addr = srv.accept()
                except OSError:
                    break  # Socket closed — clean shutdown

                if not self._semaphore.acquire(blocking=False):
                    logger.warning("Max connections reached (%s). Rejecting %s.", self.max_connections, addr)
                    conn.close()
                    continue

                thread = threading.Thread(
                    target=self._handle_connection,
                    args=(conn, addr),
                    daemon=True,
                )
                thread.start()

    # ------------------------------------------------------------------
    # Connection handler (runs on dedicated thread)
    # ------------------------------------------------------------------

    def _handle_connection(self, conn: socket.socket, addr: tuple) -> None:
        """Receive one request, process it, send response, release semaphore."""
        try:
            with conn:
                logger.info("Connection from %s", addr)
                raw = conn.recv(1024 * 8)
                if not raw:
                    return
                response = self._process_request(raw)
                conn.sendall(json.dumps(response).encode("utf-8"))
        except Exception as exc:
            logger.error("Error handling connection from %s: %s", addr, exc)
        finally:
            self._semaphore.release()

    # ------------------------------------------------------------------
    # Request dispatcher
    # ------------------------------------------------------------------

    def _process_request(self, raw_data: bytes) -> dict:
        """Validate, parse, and dispatch an incoming packet."""
        packet = self._parser.parse_client_message(raw_data)
        if packet is None:
            return {"status": "ERROR", "msg": "Invalid or malformed packet."}

        packet_type: str = packet.get("type", "")

        try:
            if packet_type == "INIT_SCENARIO":
                return self._handle_init(packet)
            if packet_type == "PLAYER_ACTION":
                return self._handle_action(packet)
            return {"status": "ERROR", "msg": f"Unknown packet type: {packet_type}"}
        except Exception as exc:
            logger.error("Unhandled error processing '%s': %s", packet_type, exc)
            return {"status": "CRASH", "msg": str(exc)}

    def _handle_init(self, packet: dict) -> dict:
        """Load scenario: build Vessel objects via VesselFactory, start engine."""
        scenario_data: dict = packet["data"]
        signature: str = packet["signature"]

        vessel_objects = VesselFactory.load_scenario(scenario_data)
        # Inject the Vessel list into the scenario dict for WarGalleyEngine
        scenario_data["vessel_objects"] = vessel_objects

        with self._engine_lock:
            self.engine = WarGalleyEngine(scenario_data, signature)

        logger.info(
            "Scenario '%s' loaded: %d vessels.",
            scenario_data.get("scenario_id", "unknown"),
            len(vessel_objects),
        )
        self._write_state({"engine_running": True, "active_vessels": len(vessel_objects),
                           "security_violations": 0, "current_turn": 0, "recent_logs": []})
        return {"status": "READY", "msg": "Scenario Loaded"}

    def _handle_action(self, packet: dict) -> dict:
        """Process one game tick: movement + combat commands."""
        with self._engine_lock:
            if self.engine is None:
                return {"status": "ERROR", "msg": "Engine not initialised. Send INIT_SCENARIO first."}

            commands: list = packet["data"].get("commands", [])

            # Combat phase: resolve RAM and OAR_RAKE before movement
            for cmd in commands:
                action = cmd.get("action")
                if action in ("RAM", "OAR_RAKE"):
                    attacker = self.engine.find_vessel(cmd["id"])
                    target_id = cmd.get("target_id")
                    defender = self.engine.find_vessel(target_id) if target_id else None
                    if attacker and defender:
                        if action == "RAM":
                            result = CombatResolver.resolve_ram(attacker, defender)
                        else:
                            result = CombatResolver.resolve_oar_rake(attacker, defender)
                        logger.info("Combat %s vessel %s → %s: %s", action, attacker.id, defender.id, result)

            vessel_states: list[dict] = self.engine.resolve_turn(commands)

        self._write_state({
            "engine_running": True,
            "active_vessels": sum(1 for v in vessel_states if not v.get("is_sunk")),
            "security_violations": 0,
            "current_turn": self.engine.current_turn,
            "recent_logs": [],
        })
        return {"status": "SUCCESS", "results": vessel_states}

    # ------------------------------------------------------------------
    # IPC state file (S4-03)
    # ------------------------------------------------------------------

    def _write_state(self, state: dict) -> None:
        """Atomically write engine state to JSON for the dashboard to read."""
        try:
            _STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
            tmp_fd, tmp_path = tempfile.mkstemp(
                dir=_STATE_PATH.parent, prefix=".state_", suffix=".tmp"
            )
            with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
                json.dump(state, f)
            os.replace(tmp_path, _STATE_PATH)
        except OSError as exc:
            logger.error("Failed to write engine_state.json: %s", exc)


if __name__ == "__main__":  # pragma: no cover
    server = WarGalleyServer()
    server.start()
