"""Tests for CombatResolver: ram, oar rake, and national doctrines.

Covers: S3-03 (apply_damage use), S3-06 (Corvus, Carthage boost, Ballista).
"""
import pytest
from unittest.mock import MagicMock


def _make_vessel(v_id=1, heading=0, speed=6.0, mass=50.0, equipment=None):
    """Create a minimal mock vessel for combat tests."""
    from vessel_base import Vessel
    from vessel_crew import Crew
    v = Vessel(v_id=v_id, side="Greece", v_type="Trireme", pos=[0, 0], heading=heading)
    v.current_speed = speed
    v.mass = mass
    v.equipment = equipment or []
    v.crew = Crew()
    return v


class TestResolveRam:
    def test_broadside_returns_critical(self):
        from combat_resolver import CombatResolver
        attacker = _make_vessel(heading=0, speed=6.0)
        defender = _make_vessel(heading=90)   # 90° difference = broadside
        result = CombatResolver.resolve_ram(attacker, defender)
        assert result == "Critical Hull Breach"

    def test_broadside_deals_more_damage_than_glancing(self):
        from combat_resolver import CombatResolver
        attacker = _make_vessel(heading=0, speed=6.0)
        defender_broadside = _make_vessel(heading=90)
        defender_glancing  = _make_vessel(heading=10)
        CombatResolver.resolve_ram(attacker, defender_broadside)
        CombatResolver.resolve_ram(attacker, defender_glancing)
        assert defender_broadside.hull_integrity < defender_glancing.hull_integrity

    def test_ram_uses_apply_damage_not_direct_assignment(self):
        """Damage must flow through apply_damage so sunk flag is set correctly."""
        from combat_resolver import CombatResolver
        attacker = _make_vessel(heading=0, speed=100.0, mass=500.0)
        defender = _make_vessel(heading=90)
        CombatResolver.resolve_ram(attacker, defender)
        # With mass=500 speed=100 broadside: damage = 500*10000*1.5 >> 100 HP
        assert defender.is_sunk is True

    def test_glancing_returns_glancing_blow(self):
        from combat_resolver import CombatResolver
        attacker = _make_vessel(heading=0, speed=3.0)
        defender = _make_vessel(heading=5)
        result = CombatResolver.resolve_ram(attacker, defender)
        assert result == "Glancing Blow"


class TestResolveOarRake:
    def test_fast_attacker_shears_oars(self):
        from combat_resolver import CombatResolver
        attacker = _make_vessel(speed=6.0)
        defender = _make_vessel()
        result = CombatResolver.resolve_oar_rake(attacker, defender)
        assert result == "Oars Sheared"
        assert defender.oars_intact == pytest.approx(0.6)

    def test_slow_attacker_cannot_rake(self):
        from combat_resolver import CombatResolver
        attacker = _make_vessel(speed=3.0)
        defender = _make_vessel()
        result = CombatResolver.resolve_oar_rake(attacker, defender)
        assert result == "Insufficient Speed"
        assert defender.oars_intact == pytest.approx(1.0)

    def test_rake_reduces_base_mp(self):
        from combat_resolver import CombatResolver
        attacker = _make_vessel(speed=8.0)
        defender = _make_vessel()
        original_mp = defender.base_mp
        CombatResolver.resolve_oar_rake(attacker, defender)
        assert defender.base_mp < original_mp


class TestNationalDoctrines:
    def test_corvus_requires_equipment(self):
        from combat_resolver import CombatResolver
        attacker = _make_vessel(equipment=[])
        defender = _make_vessel()
        result = CombatResolver.resolve_corvus_boarding(attacker, defender)
        assert result == "No Corvus equipped"

    def test_corvus_reduces_defender_mp(self):
        from combat_resolver import CombatResolver
        attacker = _make_vessel(equipment=["Corvus"])
        defender = _make_vessel()
        original_mp = defender.base_mp
        CombatResolver.resolve_corvus_boarding(attacker, defender)
        assert defender.base_mp < original_mp

    def test_carthage_boost_at_full_stamina(self):
        from combat_resolver import CombatResolver
        vessel = _make_vessel()
        vessel.crew.stamina = 100.0
        CombatResolver.apply_carthage_mp_boost(vessel)
        assert vessel.current_mp == vessel.base_mp + 2

    def test_carthage_no_boost_when_fatigued(self):
        from combat_resolver import CombatResolver
        vessel = _make_vessel()
        vessel.crew.stamina = 50.0
        original_mp = vessel.current_mp
        CombatResolver.apply_carthage_mp_boost(vessel)
        assert vessel.current_mp == original_mp

    def test_ballista_requires_equipment(self):
        from combat_resolver import CombatResolver
        attacker = _make_vessel(equipment=[])
        defender = _make_vessel()
        result = CombatResolver.resolve_ballista_fire(attacker, defender, range_val=3.0)
        assert result == "No Ballista equipped"

    def test_ballista_out_of_range_rejected(self):
        from combat_resolver import CombatResolver
        attacker = _make_vessel(equipment=["Ballista"])
        defender = _make_vessel()
        result = CombatResolver.resolve_ballista_fire(attacker, defender, range_val=9.0)
        assert result == "Target out of Ballista range"

    def test_ballista_damages_defender(self):
        from combat_resolver import CombatResolver
        attacker = _make_vessel(equipment=["Ballista"])
        defender = _make_vessel()
        CombatResolver.resolve_ballista_fire(attacker, defender, range_val=2.0)
        assert defender.hull_integrity < 100.0
