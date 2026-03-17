"""Merchant vessel: sail-driven, cargo-carrying, non-combat class."""
from vessel_base import Vessel


class MerchantVessel(Vessel):
    """Sail-driven cargo vessel. Cannot row against the wind (no oar banks).

    Historical reference: Casson, L. — Ships and Seamanship in the Ancient World (1971).
    """

    def __init__(self, v_id: int, side: str, pos: list) -> None:
        super().__init__(v_id, side, "Merchant", pos, heading=0)
        self.cargo_value: int = 5000
        self.is_sail_driven: bool = True

    def calculate_movement(self, wind: tuple) -> float:
        """Returns effective MP based on wind speed. Merchants cannot row against wind."""
        speed, _direction = wind
        # Placeholder: full vector math integrated in Sprint 3
        return speed * 0.5