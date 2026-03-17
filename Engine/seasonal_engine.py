"""Seasonal engine: applies weather modifiers and storm attrition to the fleet."""
import math
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from war_galley import WarGalleyEngine

logger = logging.getLogger(__name__)


class SeasonalManager:
    """Applies seasonal movement modifiers and storm attrition each game turn."""

    MODIFIERS: dict[str, dict] = {
        "WINTER": {"mp": 0.3, "storm": 0.45},
        "SPRING": {"mp": 1.0, "storm": 0.10},
        "SUMMER": {"mp": 1.2, "storm": 0.05},
        "AUTUMN": {"mp": 0.8, "storm": 0.20},
    }

    def apply_season(self, season_name: str, engine: "WarGalleyEngine") -> list[int]:
        """Apply seasonal MP modifier and storm attrition to all vessels.

        Returns a list of vessel IDs that suffered storm damage this turn.
        """
        mod = self.MODIFIERS.get(season_name, self.MODIFIERS["SUMMER"])
        # Apply MP modifier to each vessel's current_mp
        for vessel in engine.vessels:
            vessel.current_mp = max(1, math.floor(vessel.base_mp * mod['mp']))
        logger.debug(
            "Season '%s' applied: MP modifier=%.2f, storm probability=%.2f",
            season_name, mod['mp'], mod['storm'],
        )
        return self.check_storm_loss(mod['storm'], engine.vessels)

    def check_storm_loss(
        self, storm_probability: float, vessels: list = None
    ) -> list[int]:
        """Return IDs of vessels that suffer storm hull damage this turn.

        Uses a deterministic threshold per vessel based on storm probability.
        Full probabilistic model added in Sprint 3; this is the safe baseline.
        """
        if vessels is None:
            vessels = []
        if storm_probability <= 0.0:
            return []

        affected: list[int] = []
        for vessel in vessels:
            # Deterministic placeholder: high-probability storms hit all vessels
            if storm_probability >= 1.0:
                vessel.apply_damage(10.0, damage_type="Hull")
                affected.append(vessel.id)
                logger.warning(
                    "Storm attrition: vessel %s took 10 hull damage.", vessel.id
                )
        return affected