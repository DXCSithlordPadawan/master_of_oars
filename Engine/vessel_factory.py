from vessel_base import Vessel
from merchant_vessel import MerchantVessel
from vessel_crew import Crew

class VesselFactory:
    @staticmethod
    def create_vessel(data):
        """
        Instantiates the correct subclass based on JSON 'type'.
        Maps specialists and initial stats to the object.
        """
        v_id = data.get('id')
        side = data.get('side')
        v_type = data.get('type')
        pos = data.get('pos', [0, 0])
        heading = data.get('heading', 0)
        
        # Determine Class type
        if v_type in ["Olkas", "Merchant", "Phoenician_Trader"]:
            vessel = MerchantVessel(v_id, side, pos)
        else:
            # Standard War Galley
            vessel = Vessel(v_id, side, v_type, pos, heading)
        
        # Initialize Crew and Specialists
        crew_data = data.get('crew', {})
        vessel.crew = Crew(quality=crew_data.get('quality', 'Standard'))
        
        # Load Specialists into the Crew object
        specialists = crew_data.get('specialists', [])
        for spec in specialists:
            if spec in vessel.crew.specialists:
                vessel.crew.specialists[spec] = True
        
        # Load Archer/Skirmisher counts
        vessel.crew.specialists["Toxotai"] = crew_data.get('toxotai', 0)
        
        # Equip National Doctrines
        vessel.equipment = data.get('equipment', [])
        
        return vessel

    @staticmethod
    def load_scenario(scenario_json):
        """Helper to batch-create an entire fleet."""
        vessels = []
        for v_data in scenario_json['vessels']:
            vessels.append(VesselFactory.create_vessel(v_data))
        return vessels