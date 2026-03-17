"""Tests for Vessel base class: attributes, damage, stamina delegation.

Covers: S1-05 (mass, base_mp, update_stamina).
"""
import pytest
import numpy as np


@pytest.fixture
def basic_vessel():
    from vessel_base import Vessel
    from vessel_crew import Crew
    v = Vessel(v_id=1, side="Greece", v_type="Trireme", pos=[0, 0], heading=90)
    v.crew = Crew(quality="Standard")
    return v


class TestVesselAttributes:
    def test_has_mass(self, basic_vessel):
        assert basic_vessel.mass == 50.0

    def test_has_base_mp(self, basic_vessel):
        assert basic_vessel.base_mp == 6

    def test_current_mp_equals_base_mp_at_init(self, basic_vessel):
        assert basic_vessel.current_mp == basic_vessel.base_mp

    def test_is_flagship_defaults_false(self, basic_vessel):
        assert basic_vessel.is_flagship is False

    def test_equipment_defaults_empty_list(self, basic_vessel):
        assert basic_vessel.equipment == []


class TestUpdateStamina:
    def test_stamina_decreases_after_full_mp_move(self, basic_vessel):
        before = basic_vessel.crew.stamina
        basic_vessel.update_stamina(mp_used=6)  # full MP used
        assert basic_vessel.crew.stamina < before

    def test_stamina_decreases_less_for_partial_mp(self, basic_vessel):
        from vessel_base import Vessel
        from vessel_crew import Crew
        v2 = Vessel(v_id=2, side="Rome", v_type="Trireme", pos=[0, 0], heading=0)
        v2.crew = Crew(quality="Standard")
        before_full = basic_vessel.crew.stamina
        before_partial = v2.crew.stamina
        basic_vessel.update_stamina(mp_used=6)
        v2.update_stamina(mp_used=1)
        assert (before_full - basic_vessel.crew.stamina) > (before_partial - v2.crew.stamina)

    def test_update_stamina_no_crew_does_not_crash(self):
        from vessel_base import Vessel
        v = Vessel(v_id=3, side="Egypt", v_type="Bireme", pos=[5, 5], heading=0)
        # crew is None — must not raise
        v.update_stamina(mp_used=3)


class TestApplyDamage:
    def test_hull_damage_reduces_integrity(self, basic_vessel):
        basic_vessel.apply_damage(20.0, damage_type="Hull")
        assert basic_vessel.hull_integrity == 80.0

    def test_sunk_when_hull_zero(self, basic_vessel):
        basic_vessel.apply_damage(100.0, damage_type="Hull")
        assert basic_vessel.is_sunk is True

    def test_oar_damage_reduces_intact(self, basic_vessel):
        basic_vessel.apply_damage(0.4, damage_type="Oars")
        assert basic_vessel.oars_intact == pytest.approx(0.6)

    def test_oar_intact_floored_at_zero(self, basic_vessel):
        basic_vessel.apply_damage(5.0, damage_type="Oars")
        assert basic_vessel.oars_intact == 0.0


class TestToDict:
    def test_to_dict_contains_required_keys(self, basic_vessel):
        d = basic_vessel.to_dict()
        for key in ("id", "pos", "heading", "hull", "oars", "is_sunk", "is_autonomous"):
            assert key in d

    def test_pos_is_list(self, basic_vessel):
        d = basic_vessel.to_dict()
        assert isinstance(d["pos"], list)
