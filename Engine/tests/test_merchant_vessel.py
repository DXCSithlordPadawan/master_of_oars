"""Tests for MerchantVessel: correct inheritance and Vessel substitutability.

Covers: S1-04 (LSP compliance, to_dict, VesselFactory integration).
"""
import pytest


class TestMerchantVesselInheritance:
    def test_is_vessel_subclass(self):
        from merchant_vessel import MerchantVessel
        from vessel_base import Vessel
        assert issubclass(MerchantVessel, Vessel)

    def test_instantiates_with_factory_args(self):
        from merchant_vessel import MerchantVessel
        mv = MerchantVessel(v_id=99, side="Carthage", pos=[5.0, 10.0])
        assert mv.id == 99
        assert mv.side == "Carthage"

    def test_has_cargo_value(self):
        from merchant_vessel import MerchantVessel
        mv = MerchantVessel(v_id=1, side="Greece", pos=[0, 0])
        assert mv.cargo_value == 5000

    def test_is_sail_driven(self):
        from merchant_vessel import MerchantVessel
        mv = MerchantVessel(v_id=1, side="Greece", pos=[0, 0])
        assert mv.is_sail_driven is True

    def test_has_to_dict(self):
        from merchant_vessel import MerchantVessel
        mv = MerchantVessel(v_id=1, side="Greece", pos=[0, 0])
        d = mv.to_dict()
        assert "id" in d and "hull" in d

    def test_calculate_movement_returns_float(self):
        from merchant_vessel import MerchantVessel
        mv = MerchantVessel(v_id=1, side="Greece", pos=[0, 0])
        result = mv.calculate_movement(wind=(6.0, 180))
        assert isinstance(result, float)
        assert result == pytest.approx(3.0)


class TestVesselFactoryMerchant:
    def test_factory_creates_merchant_for_phoenician_trader(self):
        from vessel_factory import VesselFactory
        from merchant_vessel import MerchantVessel
        data = {"id": 201, "type": "Phoenician_Trader", "side": "Persia", "pos": [50, 25]}
        vessel = VesselFactory.create_vessel(data)
        assert isinstance(vessel, MerchantVessel)

    def test_factory_creates_merchant_for_olkas(self):
        from vessel_factory import VesselFactory
        from merchant_vessel import MerchantVessel
        data = {"id": 202, "type": "Olkas", "side": "Carthage", "pos": [10, 10]}
        vessel = VesselFactory.create_vessel(data)
        assert isinstance(vessel, MerchantVessel)

    def test_factory_creates_base_vessel_for_trireme(self):
        from vessel_factory import VesselFactory
        from vessel_base import Vessel
        from merchant_vessel import MerchantVessel
        data = {"id": 101, "type": "Trireme", "side": "Greece", "pos": [0, 0]}
        vessel = VesselFactory.create_vessel(data)
        assert isinstance(vessel, Vessel)
        assert not isinstance(vessel, MerchantVessel)
