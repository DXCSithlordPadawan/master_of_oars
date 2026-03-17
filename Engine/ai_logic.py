class NavalAI:
    def generate_influence_map(self, grid, vessels):
        """Creates a heat map of danger/opportunity zones."""
        # AI prioritizes Merchant targets over warships
        # unless flagship is threatened.
        pass

    def get_autonomous_action(self, vessel):
        """Logic for ships outside the Signal Radius."""
        if vessel.hull_integrity < 30:
            return "RETREAT"
        return "ATTACK_NEAREST"