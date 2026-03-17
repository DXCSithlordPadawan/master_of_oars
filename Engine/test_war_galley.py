import unittest
from security_utils import SecurityManager
from vessel_factory import VesselFactory

class TestEngineIntegrity(unittest.TestCase):
    def setUp(self):
        self.sm = SecurityManager()
        self.mock_scenario = {
            "vessels": [{"id": 1, "type": "Trireme", "side": "Greece", "pos": [0,0]}]
        }

    def test_fips_hmac_valid(self):
        """Ensure valid signatures are accepted."""
        sig = self.sm.generate_signature(str(self.mock_scenario))
        self.assertTrue(self.sm.verify_scenario(self.mock_scenario, sig))

    def test_tamper_detection(self):
        """Ensure modified data is rejected (NIST requirement)."""
        sig = self.sm.generate_signature(str(self.mock_scenario))
        self.mock_scenario["vessels"][0]["side"] = "Persia" # Tamper!
        self.assertFalse(self.sm.verify_scenario(self.mock_scenario, sig))

if __name__ == "__main__":
    unittest.main()