"""Tests for SeasonalManager: check_storm_loss and apply_season.

Covers: S1-07 (check_storm_loss implemented), S3-05 (apply_season integration).
"""
import pytest
from unittest.mock import MagicMock


def _make_mock_engine(vessel_count=2, base_mp=6):
    """Return a minimal mock engine object with a vessel list."""
    from vessel_base import Vessel
    from vessel_crew import Crew
    vessels = []
    for i in range(vessel_count):
        v = Vessel(v_id=i+1, side="Greece", v_type="Trireme", pos=[i*5, 0], heading=0)
        v.crew = Crew()
        vessels.append(v)
    engine = MagicMock()
    engine.vessels = vessels
    return engine


class TestCheckStormLoss:
    def test_zero_probability_returns_empty(self):
        from seasonal_engine import SeasonalManager
        sm = SeasonalManager()
        result = sm.check_storm_loss(0.0, vessels=[])
        assert result == []

    def test_negative_probability_returns_empty(self):
        from seasonal_engine import SeasonalManager
        sm = SeasonalManager()
        result = sm.check_storm_loss(-0.5, vessels=[])
        assert result == []

    def test_full_probability_affects_all_vessels(self):
        from seasonal_engine import SeasonalManager
        from vessel_base import Vessel
        from vessel_crew import Crew
        sm = SeasonalManager()
        vessels = [
            Vessel(v_id=1, side="Rome", v_type="Trireme", pos=[0, 0], heading=0),
            Vessel(v_id=2, side="Rome", v_type="Trireme", pos=[5, 0], heading=0),
        ]
        for v in vessels:
            v.crew = Crew()
        affected = sm.check_storm_loss(1.0, vessels=vessels)
        assert len(affected) == 2

    def test_partial_probability_returns_empty_list(self):
        """Partial storm probability below threshold returns no hits (deterministic baseline)."""
        from seasonal_engine import SeasonalManager
        from vessel_base import Vessel
        sm = SeasonalManager()
        vessels = [Vessel(v_id=1, side="Rome", v_type="Trireme", pos=[0, 0], heading=0)]
        affected = sm.check_storm_loss(0.5, vessels=vessels)
        assert affected == []

    def test_none_vessels_defaults_to_empty(self):
        from seasonal_engine import SeasonalManager
        sm = SeasonalManager()
        result = sm.check_storm_loss(1.0, vessels=None)
        assert result == []


class TestApplySeason:
    def test_summer_increases_mp(self):
        from seasonal_engine import SeasonalManager
        sm = SeasonalManager()
        engine = _make_mock_engine()
        sm.apply_season("SUMMER", engine)
        for v in engine.vessels:
            # Summer modifier 1.2 * base_mp=6 = 7
            assert v.current_mp >= v.base_mp

    def test_winter_reduces_mp(self):
        from seasonal_engine import SeasonalManager
        sm = SeasonalManager()
        engine = _make_mock_engine()
        sm.apply_season("WINTER", engine)
        for v in engine.vessels:
            assert v.current_mp < v.base_mp

    def test_unknown_season_uses_summer_default(self):
        from seasonal_engine import SeasonalManager
        sm = SeasonalManager()
        engine = _make_mock_engine()
        sm.apply_season("MONSOON", engine)   # Not in MODIFIERS — should default
        # Should not raise; vessels get summer modifier
        for v in engine.vessels:
            assert v.current_mp >= 1

    def test_all_four_seasons_present(self):
        from seasonal_engine import SeasonalManager
        assert set(SeasonalManager.MODIFIERS.keys()) == {"WINTER", "SPRING", "SUMMER", "AUTUMN"}
