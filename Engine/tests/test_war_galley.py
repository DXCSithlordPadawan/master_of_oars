"""Tests for WarGalleyEngine: find_vessel, check_command_link, calculate_new_pos.

Covers: S1-06 (three missing methods), S3-07 (resolve_turn return value).
These are the original tests migrated from Engine/test_war_galley.py plus new coverage.
"""
import pytest
import numpy as np
from unittest.mock import MagicMock, patch


@pytest.fixture(autouse=True)
def valid_env(monkeypatch):
    monkeypatch.setenv("HMAC_KEY", "TestKey_ExactlyThirtyTwoChars!!")
    monkeypatch.setenv("DEFAULT_SEASON", "SUMMER")


def _make_engine_with_vessels(vessel_count=2):
    """Build a WarGalleyEngine with pre-created Vessel objects (bypasses HMAC)."""
    from vessel_base import Vessel
    from vessel_crew import Crew
    from war_galley import WarGalleyEngine
    from security_utils import SecurityManager

    vessels = []
    for i in range(vessel_count):
        v = Vessel(v_id=i + 1, side="Greece", v_type="Trireme",
                   pos=[float(i * 10), 0.0], heading=0)
        v.crew = Crew(quality="Standard")
        vessels.append(v)

    # Build engine bypassing signature check
    sm = SecurityManager()
    scenario = {
        "scenario_id": "TEST",
        "vessels": [],
        "vessel_objects": vessels,
    }
    sig = sm.generate_signature(str(scenario))
    with patch.object(sm.__class__, 'verify_scenario', return_value=True):
        engine = WarGalleyEngine.__new__(WarGalleyEngine)
        engine.sm = sm
        engine.vessels = vessels
        engine.wind = (5.0, 90)
        engine.current_turn = 0
        engine.command_radius = 15.0
        from ai_logic import NavalAI
        from seasonal_engine import SeasonalManager
        engine._ai = NavalAI()
        engine._seasonal = SeasonalManager()
        engine._season = "SUMMER"
    return engine


class TestFindVessel:
    def test_finds_existing_vessel(self):
        engine = _make_engine_with_vessels(2)
        v = engine.find_vessel(1)
        assert v is not None
        assert v.id == 1

    def test_returns_none_for_missing_vessel(self):
        engine = _make_engine_with_vessels(2)
        assert engine.find_vessel(999) is None


class TestCheckCommandLink:
    def test_no_flagship_always_true(self):
        engine = _make_engine_with_vessels(2)
        for v in engine.vessels:
            assert engine.check_command_link(v) is True

    def test_inside_radius_returns_true(self):
        engine = _make_engine_with_vessels(2)
        engine.vessels[0].is_flagship = True
        engine.vessels[0].pos = np.array([0.0, 0.0])
        engine.vessels[1].pos = np.array([5.0, 0.0])  # 5 units — within 15
        assert engine.check_command_link(engine.vessels[1]) is True

    def test_outside_radius_returns_false(self):
        engine = _make_engine_with_vessels(2)
        engine.vessels[0].is_flagship = True
        engine.vessels[0].pos = np.array([0.0, 0.0])
        engine.vessels[1].pos = np.array([50.0, 0.0])  # 50 units — outside 15
        assert engine.check_command_link(engine.vessels[1]) is False


class TestCalculateNewPos:
    def test_moves_vessel_by_vector(self):
        engine = _make_engine_with_vessels(1)
        vessel = engine.vessels[0]
        vessel.pos = np.array([0.0, 0.0])
        new_pos = engine.calculate_new_pos(vessel, [3.0, 4.0])  # magnitude = 5
        assert new_pos[0] == pytest.approx(3.0)
        assert new_pos[1] == pytest.approx(4.0)

    def test_clamps_vector_to_max_mp(self):
        engine = _make_engine_with_vessels(1)
        vessel = engine.vessels[0]
        vessel.pos = np.array([0.0, 0.0])
        vessel.base_mp = 6
        # Vector with magnitude 100 — must be clamped to base_mp=6
        new_pos = engine.calculate_new_pos(vessel, [100.0, 0.0])
        distance = float(np.linalg.norm(new_pos - vessel.pos))
        assert distance == pytest.approx(6.0, abs=0.01)


class TestResolveTurn:
    def test_returns_list_of_dicts(self):
        engine = _make_engine_with_vessels(1)
        commands = [{"id": 1, "mp_used": 3, "vector": [1.0, 0.0]}]
        result = engine.resolve_turn(commands)
        assert isinstance(result, list)
        assert len(result) == 1
        assert "id" in result[0]

    def test_turn_counter_increments(self):
        engine = _make_engine_with_vessels(1)
        engine.resolve_turn([])
        assert engine.current_turn == 1

    def test_sunk_vessel_skipped(self):
        engine = _make_engine_with_vessels(1)
        engine.vessels[0].is_sunk = True
        engine.vessels[0].pos = np.array([0.0, 0.0])
        commands = [{"id": 1, "mp_used": 6, "vector": [10.0, 0.0]}]
        engine.resolve_turn(commands)
        # Sunk vessel should not move
        assert engine.vessels[0].pos[0] == pytest.approx(0.0)
