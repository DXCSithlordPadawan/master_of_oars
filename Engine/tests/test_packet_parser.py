"""Tests for PacketParser: schema validation, HMAC verification, formatting.

Covers: S1-03 (method name fix), S2-06 (JSON schema validation).
"""
import json
import pytest


@pytest.fixture(autouse=True)
def valid_env(monkeypatch):
    monkeypatch.setenv("HMAC_KEY", "TestKey_ExactlyThirtyTwoChars!!")


def _make_signed_packet(packet_type: str, data: dict) -> bytes:
    """Helper: build a correctly signed packet for a given type."""
    from security_utils import SecurityManager
    sm = SecurityManager()
    sig = sm.generate_signature(str(data))
    packet = {"type": packet_type, "data": data, "signature": sig}
    return json.dumps(packet).encode("utf-8")


class TestParseClientMessage:
    def test_valid_init_scenario_parsed(self):
        from packet_parser import PacketParser
        data = {
            "scenario_id": "TEST_001",
            "vessels": [{"id": 1, "type": "Trireme", "side": "Greece", "pos": [0.0, 0.0]}]
        }
        raw = _make_signed_packet("INIT_SCENARIO", data)
        parser = PacketParser()
        result = parser.parse_client_message(raw)
        assert result is not None
        assert result["type"] == "INIT_SCENARIO"

    def test_valid_player_action_parsed(self):
        from packet_parser import PacketParser
        data = {"commands": [{"id": 1, "mp_used": 3, "vector": [1.0, 0.0], "action": "MOVE"}]}
        raw = _make_signed_packet("PLAYER_ACTION", data)
        parser = PacketParser()
        result = parser.parse_client_message(raw)
        assert result is not None
        assert result["type"] == "PLAYER_ACTION"

    def test_invalid_hmac_returns_none(self):
        from packet_parser import PacketParser
        data = {"scenario_id": "X", "vessels": [{"id": 1, "type": "T", "side": "G", "pos": [0, 0]}]}
        packet = {"type": "INIT_SCENARIO", "data": data, "signature": "a" * 64}
        raw = json.dumps(packet).encode("utf-8")
        parser = PacketParser()
        result = parser.parse_client_message(raw)
        assert result is None

    def test_malformed_json_returns_none(self):
        from packet_parser import PacketParser
        parser = PacketParser()
        result = parser.parse_client_message(b"{not valid json}")
        assert result is None

    def test_unknown_packet_type_returns_none(self):
        from packet_parser import PacketParser
        from security_utils import SecurityManager
        sm = SecurityManager()
        data = {"foo": "bar"}
        sig = sm.generate_signature(str(data))
        packet = {"type": "UNKNOWN_TYPE", "data": data, "signature": sig}
        raw = json.dumps(packet).encode("utf-8")
        parser = PacketParser()
        result = parser.parse_client_message(raw)
        assert result is None

    def test_schema_rejects_missing_required_field(self):
        """INIT_SCENARIO missing 'vessels' field should fail schema validation."""
        from packet_parser import PacketParser
        from security_utils import SecurityManager
        sm = SecurityManager()
        # Missing 'vessels' — invalid per scenario_schema.json
        data = {"scenario_id": "MISSING_VESSELS"}
        sig = sm.generate_signature(str(data))
        packet = {"type": "INIT_SCENARIO", "data": data, "signature": sig}
        raw = json.dumps(packet).encode("utf-8")
        parser = PacketParser()
        result = parser.parse_client_message(raw)
        assert result is None


class TestFormatServerUpdate:
    def test_output_is_bytes(self):
        from packet_parser import PacketParser
        parser = PacketParser()
        out = parser.format_server_update([{"id": 1, "hull": 100}])
        assert isinstance(out, bytes)

    def test_output_contains_signature(self):
        from packet_parser import PacketParser
        parser = PacketParser()
        out = parser.format_server_update({"turn": 1})
        packet = json.loads(out.decode("utf-8").strip())
        assert "signature" in packet
        assert len(packet["signature"]) == 64

    def test_output_is_newline_terminated(self):
        from packet_parser import PacketParser
        parser = PacketParser()
        out = parser.format_server_update({"turn": 1})
        assert out.endswith(b"\n")
