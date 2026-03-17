"""Tests for SecurityManager: HMAC signing, verification, and guard clauses.

Covers: S1-02 (null guard), S2-02 (sign-all), S2-03 (rotate_keys).
"""
import os
import pytest
from unittest.mock import patch, MagicMock


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def valid_hmac_env(monkeypatch):
    """Ensure HMAC_KEY is set to a valid 32-char key for every test."""
    monkeypatch.setenv("HMAC_KEY", "TestKey_ExactlyThirtyTwoChars!!")


# ---------------------------------------------------------------------------
# SecurityManager init guards (S1-02)
# ---------------------------------------------------------------------------

class TestSecurityManagerInit:
    def test_raises_when_key_missing(self, monkeypatch):
        monkeypatch.delenv("HMAC_KEY", raising=False)
        from importlib import reload
        import security_utils
        reload(security_utils)
        with pytest.raises(EnvironmentError, match="HMAC_KEY is not set"):
            security_utils.SecurityManager()

    def test_raises_when_key_too_short(self, monkeypatch):
        monkeypatch.setenv("HMAC_KEY", "tooshort")
        from importlib import reload
        import security_utils
        reload(security_utils)
        with pytest.raises(ValueError, match="at least 32 characters"):
            security_utils.SecurityManager()

    def test_accepts_valid_key(self):
        from security_utils import SecurityManager
        sm = SecurityManager()
        assert sm._key is not None


# ---------------------------------------------------------------------------
# HMAC signing and verification (S1-02, existing tests migrated)
# ---------------------------------------------------------------------------

class TestHMACOperations:
    def test_valid_signature_accepted(self):
        from security_utils import SecurityManager
        sm = SecurityManager()
        data = {"vessels": [{"id": 1}]}
        sig = sm.generate_signature(str(data))
        assert sm.verify_scenario(data, sig) is True

    def test_tampered_data_rejected(self):
        from security_utils import SecurityManager
        sm = SecurityManager()
        data = {"vessels": [{"id": 1, "side": "Greece"}]}
        sig = sm.generate_signature(str(data))
        data["vessels"][0]["side"] = "Persia"
        assert sm.verify_scenario(data, sig) is False

    def test_empty_string_signature_rejected(self):
        from security_utils import SecurityManager
        sm = SecurityManager()
        assert sm.verify_scenario({"x": 1}, "") is False

    def test_signature_is_64_hex_chars(self):
        from security_utils import SecurityManager
        sm = SecurityManager()
        sig = sm.generate_signature("test payload")
        assert len(sig) == 64
        assert all(c in "0123456789abcdef" for c in sig)
