import numpy as np

class Vessel:
    def __init__(self, v_id, side, v_type, pos, heading):
        self.id = v_id
        self.side = side # 'Rome', 'Carthage', 'Egypt', etc.
        self.type = v_type
        
        # Transform Data
        self.pos = np.array(pos, dtype=float) # [x, y]
        self.heading = heading # Degrees (0-359)
        self.current_speed = 0.0
        
        # Health & Hardware
        self.hull_integrity = 100.0
        self.oars_intact = 1.0 # 0.0 to 1.0 (Percentage)
        self.is_sunk = False
        self.is_autonomous = False # Controlled by AI if True
        
        # Physics
        self.mass: float = 50.0       # Tonnes; default Trireme displacement
        self.base_mp: int = 6          # Base movement points per turn
        self.current_mp: int = self.base_mp

        # Command
        self.is_flagship: bool = False

        # Crew & Equipment
        self.crew = None  # Initialised by vessel_crew.py
        self.equipment: list = []  # e.g. ["Corvus", "Harpax"]

    def get_forward_vector(self):
        """Calculates the vector based on current heading."""
        rad = np.radians(self.heading)
        return np.array([np.cos(rad), np.sin(rad)])

    def update_stamina(self, mp_used: int) -> None:
        """Delegate fatigue drain to the crew object based on MP used this turn."""
        if self.crew is not None:
            ratio = mp_used / max(self.base_mp, 1)
            self.crew.process_fatigue(ratio)

    def apply_damage(self, amount: float, damage_type: str = "Hull") -> None:
        """Centralized damage handler for audit logging."""
        if damage_type == "Hull":
            self.hull_integrity -= amount
            if self.hull_integrity <= 0:
                self.is_sunk = True
        elif damage_type == "Oars":
            self.oars_intact = max(0, self.oars_intact - amount)

    def to_dict(self):
        """Serializes vessel state for the Unity TCP Bridge."""
        return {
            "id": self.id,
            "pos": self.pos.tolist(),
            "heading": self.heading,
            "hull": self.hull_integrity,
            "oars": self.oars_intact,
            "is_sunk": self.is_sunk,
            "is_autonomous": self.is_autonomous
        }