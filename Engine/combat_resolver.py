"""Combat resolver: RAM, OAR_RAKE, and national doctrine mechanics.

National doctrines (FR-04):
  Rome    — Corvus boarding bridge (grapple + boarding penalty)
  Carthage — Speed boost when at full crew stamina
  Egypt   — Ballista long-range fire
"""
import logging

from logger_config import get_logger

logger = get_logger(__name__)


class CombatResolver:
    """Static methods for all combat resolution. No instance state."""

    # ------------------------------------------------------------------
    # Core combat actions
    # ------------------------------------------------------------------

    @staticmethod
    def resolve_ram(attacker, defender) -> str:
        """Calculate kinetic impact damage and apply via apply_damage().

        Ramming Damage = (Mass * Velocity²) scaled by angle of impact.
        Broadside hits are most damaging; glancing blows are minor.
        """
        angle_diff = abs(attacker.heading - defender.heading)
        impact_force = attacker.mass * (attacker.current_speed ** 2)

        if 80 <= angle_diff <= 100:  # Broadside — maximum damage
            damage = impact_force * 1.5
            result = "Critical Hull Breach"
        else:
            damage = impact_force * 0.4
            result = "Glancing Blow"

        defender.apply_damage(damage, damage_type="Hull")
        logger.info(
            "RAM: vessel %s → %s  damage=%.1f  result=%s",
            attacker.id, defender.id, damage, result,
        )
        return result

    @staticmethod
    def resolve_oar_rake(attacker, defender) -> str:
        """Shear the defender's oar banks, reducing mobility."""
        if attacker.current_speed > 5.0:
            defender.oars_intact *= 0.6
            defender.base_mp = max(1, int(defender.base_mp * 0.7))
            logger.info(
                "OAR_RAKE: vessel %s → %s  oars=%.2f  base_mp=%d",
                attacker.id, defender.id, defender.oars_intact, defender.base_mp,
            )
            return "Oars Sheared"
        logger.info("OAR_RAKE: vessel %s too slow to rake (speed=%.1f).", attacker.id, attacker.current_speed)
        return "Insufficient Speed"

    # ------------------------------------------------------------------
    # National doctrine: Rome — Corvus boarding bridge (FR-04)
    # ------------------------------------------------------------------

    @staticmethod
    def resolve_corvus_boarding(attacker, defender) -> str:
        """Rome: drop the Corvus spike to lock ships together and board.

        Requires 'Corvus' in attacker.equipment. Defender suffers crew
        attrition and reduced mp for the duration of boarding.
        """
        if "Corvus" not in attacker.equipment:
            return "No Corvus equipped"

        # Boarding: defender loses MP and takes light hull damage from spike
        defender.apply_damage(5.0, damage_type="Hull")
        defender.base_mp = max(1, int(defender.base_mp * 0.5))
        logger.info(
            "CORVUS BOARDING: vessel %s → %s  defender base_mp reduced to %d",
            attacker.id, defender.id, defender.base_mp,
        )
        return "Corvus Locked — Boarding Action"

    # ------------------------------------------------------------------
    # National doctrine: Carthage — speed burst (FR-04)
    # ------------------------------------------------------------------

    @staticmethod
    def apply_carthage_mp_boost(vessel) -> None:
        """Carthage: elite crews at full stamina get +2 MP this turn.

        Applied during turn resolution when crew stamina is ≥ 80.
        """
        if vessel.crew is None:
            return
        if vessel.crew.stamina >= 80.0:
            vessel.current_mp = vessel.base_mp + 2
            logger.debug("CARTHAGE BOOST: vessel %s current_mp=%d", vessel.id, vessel.current_mp)

    # ------------------------------------------------------------------
    # National doctrine: Egypt — Ballista ranged fire (FR-04)
    # ------------------------------------------------------------------

    @staticmethod
    def resolve_ballista_fire(attacker, defender, range_val: float) -> str:
        """Egypt: Ballista bolt fired at range. Effective up to 8 hexes.

        Requires 'Ballista' in attacker.equipment. Damage falls off with range.
        """
        if "Ballista" not in attacker.equipment:
            return "No Ballista equipped"
        if range_val > 8.0:
            return "Target out of Ballista range"

        # Damage is inverse of range (closer = more damage)
        base_damage = 15.0
        damage = max(2.0, base_damage - (range_val * 1.5))
        defender.apply_damage(damage, damage_type="Hull")
        logger.info(
            "BALLISTA: vessel %s → %s  range=%.1f  damage=%.1f",
            attacker.id, defender.id, range_val, damage,
        )
        return f"Ballista Hit — {damage:.1f} hull damage"
