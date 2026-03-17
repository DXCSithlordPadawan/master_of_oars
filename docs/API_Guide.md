# API Guide — War Galley v1.0

## Overview

The system exposes two interfaces:

1. **TCP Bridge (Port 5555)** — Binary JSON packets exchanged between Unity and the Python engine. Not HTTP.
2. **Admin REST API (Port 8080)** — Flask HTTP endpoint for the web dashboard.

---

## TCP Bridge Protocol (Port 5555)

All packets are JSON objects with three required top-level keys:

```json
{
  "type": "<packet type>",
  "data": { ... },
  "signature": "<64-char HMAC-SHA256 hex string>"
}
```

The `signature` field is computed as `HMAC-SHA256(HMAC_KEY, str(data))`. The server validates the signature before processing any packet. Invalid signatures return an error response immediately.

### Packet Type: `INIT_SCENARIO`

Sent once per game session to load a scenario and initialise the engine.

**Request:**
```json
{
  "type": "INIT_SCENARIO",
  "data": {
    "scenario_id": "SALAMIS_001",
    "wind": [4.5, 180],
    "vessels": [
      {
        "id": 101,
        "type": "Trireme",
        "side": "Greece",
        "pos": [10.5, 20.0],
        "heading": 90,
        "crew": { "quality": "Elite", "specialists": ["Kybernetes"], "toxotai": 15 },
        "equipment": []
      }
    ]
  },
  "signature": "<hmac_sha256_hex>"
}
```

**Response (success):**
```json
{ "status": "READY", "msg": "Scenario Loaded" }
```

**Response (failure):**
```json
{ "status": "ERROR", "msg": "Invalid or malformed packet." }
```

### Packet Type: `PLAYER_ACTION`

Sent each turn to submit movement and combat commands.

**Request:**
```json
{
  "type": "PLAYER_ACTION",
  "data": {
    "commands": [
      { "id": 101, "mp_used": 4, "vector": [2.0, 1.5], "action": "MOVE" },
      { "id": 102, "mp_used": 6, "vector": [0.0, 0.0], "action": "RAM", "target_id": 201 }
    ]
  },
  "signature": "<hmac_sha256_hex>"
}
```

Valid `action` values: `MOVE`, `RAM`, `OAR_RAKE`, `HOLD`.

**Response (success):**
```json
{
  "status": "SUCCESS",
  "results": [
    { "id": 101, "pos": [12.5, 21.5], "heading": 90, "hull": 100.0, "oars": 1.0, "is_sunk": false, "is_autonomous": false },
    { "id": 201, "pos": [50.0, 25.0], "heading": 270, "hull": 62.5, "oars": 1.0, "is_sunk": false, "is_autonomous": false }
  ]
}
```

---

## Admin REST API (Port 8080)

### Authentication

All endpoints require a Bearer token in the `Authorization` header:

```
Authorization: Bearer <ADMIN_API_KEY>
```

`ADMIN_API_KEY` is set in `.env`. Requests without a valid token return `HTTP 401` with no body.

---

### `GET /api/v1/telemetry`

Returns current engine state for the admin dashboard. Reads from `Engine/logs/engine_state.json` written by the engine after every tick.

**Response (200 OK):**
```json
{
  "engine_running": true,
  "active_vessels": 5,
  "sunk_vessels": 1,
  "autonomous_vessels": 0,
  "security_violations": 0,
  "current_turn": 12,
  "recent_logs": []
}
```

**Response headers include:**
- `Content-Security-Policy: default-src 'none'`
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: no-referrer`
- `Cache-Control: no-store`

---

## JSON Schema Validation

All incoming TCP packets are validated against JSON schemas stored in `Engine/schemas/` before HMAC verification. Packets failing schema validation are dropped and logged. Schemas:

- `Engine/schemas/scenario_schema.json` — validates `INIT_SCENARIO` packets
- `Engine/schemas/action_schema.json` — validates `PLAYER_ACTION` packets
