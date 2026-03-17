"""Vessel crew: stamina, fatigue, specialists, and quality modifiers."""
import logging

from logger_config import get_logger

logger = get_logger(__name__)

# Quality modifier applied to stamina drain and performance
_QUALITY_MODIFIERS: dict[str, float] = {
    "Elite":    1.25,
    "Standard": 1.00,
    "Poor":     0.75,
}


class Crew:
    """Manages crew stamina, fatigue drain, and specialist bonuses."""

    def __init__(self, quality: str = "Standard") -> None:
        self.stamina: float = 100.0
        self.quality: str = quality
        self.quality_modifier: float = _QUALITY_MODIFIERS.get(quality, 1.00)
        self.specialists: dict = {
            "Keleustes":  False,   # Drummer — reduces fatigue drain
            "Kybernetes": False,   # Helmsman — improves manoeuvring
            "Toxotai":    0,       # Archer count
        }

    def process_fatigue(self, mp_ratio: float) -> None:
        """Drain stamina based on MP usage this turn.

        Elite crews fatigue more slowly; Poor crews fatigue faster.
        Keleustes specialist reduces drain by 30%.
        """
        base_drain = 2.0 if mp_ratio > 0.8 else 0.5
        # Quality affects effective stamina pool; invert modifier for drain
        drain = base_drain / self.quality_modifier
        if self.specialists["Keleustes"]:
            drain *= 0.7  # Keleustes: paced rowing reduces fatigue
        self.stamina = max(0.0, self.stamina - drain)
        logger.debug("Crew fatigue: drain=%.2f stamina=%.1f", drain, self.stamina)

    def get_performance_penalty(self) -> float:
        """Return an MP multiplier based on current stamina and quality.

        Elite crews retain performance at lower stamina thresholds.
        """
        # Penalty threshold scales with quality: Elite degrade later
        threshold = 20.0 * (1.0 / self.quality_modifier)
        if self.stamina < threshold:
            return 0.5
        return 1.0

    def get_kybernetes_arc_bonus(self) -> float:
        """Return extra heading-change arc (degrees) if Kybernetes is aboard.

        Applied in calculate_new_pos() to allow wider turns for the same MP.
        Returns 0.0 if no Kybernetes specialist is present.
        """
        return 15.0 if self.specialists["Kybernetes"] else 0.0
