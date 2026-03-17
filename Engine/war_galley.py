"""War Galley authoritative engine: turn resolution, movement, and AI."""
import logging
import os
from typing import Optional

import numpy as np
from dotenv import load_dotenv

from ai_logic import NavalAI
from seasonal_engine import SeasonalManager
from security_utils import SecurityManager
from vessel_base import Vessel

load_dotenv()
logger = logging.getLogger(__name__)


class WarGalleyEngine:
    """Authoritative simulation engine: validates scenario, resolves turns."""

    def __init__(self, scenario_data: dict, signature: str) -> None:
        self.sm = SecurityManager()
        if not self.sm.verify_scenario(scenario_data, signature):
            raise PermissionError("FIPS 140-2 Violation: Scenario Signature Mismatch")

        # Populated by VesselFactory.load_scenario() in main.py before passing here
        self.vessels: list[Vessel] = scenario_data.get('vessel_objects', [])
        self.wind: tuple = tuple(scenario_data.get('wind', (5.0, 90)))  # (speed, direction)
        self.current_turn: int = 0
        self.command_radius: float = float(
            scenario_data.get('command_radius', 15.0)
        )
        self._ai = NavalAI()
        self._seasonal = SeasonalManager()
        self._season: str = os.getenv("DEFAULT_SEASON", "SUMMER")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def resolve_turn(self, player_commands: list) -> list[dict]:
        """Process one full game tick: seasonal modifiers, movement, and AI.

        Returns a list of serialised vessel state dicts for the Unity client.
        """
        # Apply seasonal modifiers once per turn
        self._seasonal.apply_season(self._season, self)

        for cmd in player_commands:
            vessel = self.find_vessel(cmd['id'])
            if vessel is None or vessel.is_sunk:
                continue

            # 1. Update fatigue based on MP used
            mp_used = cmd.get('mp_used', 0)
            vessel.update_stamina(mp_used)

            # 2. Command radius check — fall back to NavalAI if out of range
            if not self.check_command_link(vessel):
                action = self._ai.get_autonomous_action(vessel)
                vessel.is_autonomous = True
                logger.info(
                    "Vessel %s out of command radius — autonomous action: %s",
                    vessel.id, action
                )
                continue

            vessel.is_autonomous = False

            # 3. Apply movement
            movement_vector = cmd.get('vector', [0, 0])
            vessel.pos = self.calculate_new_pos(vessel, movement_vector)

        self.current_turn += 1
        return [v.to_dict() for v in self.vessels]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def find_vessel(self, vessel_id: int) -> Optional[Vessel]:
        """Return a Vessel by ID, or None if not found."""
        return next((v for v in self.vessels if v.id == vessel_id), None)

    def check_command_link(self, vessel: Vessel) -> bool:
        """Return True if vessel is within flagship signal radius.

        If no flagship is defined all vessels retain player control.
        """
        flagship = next((v for v in self.vessels if v.is_flagship), None)
        if flagship is None:
            return True
        distance = float(np.linalg.norm(vessel.pos - flagship.pos))
        return distance <= self.command_radius

    def calculate_new_pos(
        self, vessel: Vessel, vector: list
    ) -> np.ndarray:
        """Apply a movement vector clamped to the vessel's available MP."""
        delta = np.array(vector, dtype=float)
        magnitude = float(np.linalg.norm(delta))
        performance = (
            vessel.crew.get_performance_penalty()
            if vessel.crew is not None
            else 1.0
        )
        max_move = vessel.base_mp * performance
        if magnitude > max_move and magnitude > 0:
            delta = delta / magnitude * max_move
        return vessel.pos + delta