# Architecture Guide — War Galley v1.0

## Overview

The system follows an **Authoritative Server Pattern**. The Unity client is a "dumb" visualiser; all state changes (ramming, fatigue, sinking) are calculated in the Python engine container and sent back to Unity as signed JSON updates.

## System Architecture Diagram

```mermaid
graph LR
    subgraph Client_Zone ["Unity 3D Frontend"]
        UI["UI / Input Manager"]
        VIS["Visualiser / Shaders"]
    end

    subgraph Security_Gateway ["Security Layer"]
        HMAC["HMAC-SHA256 Validator"]
        TLS["TLS 1.3 — Planned"]
    end

    subgraph Logic_Core ["Python Authoritative Engine (Port 5555)"]
        PKT["PacketParser\nSchema + HMAC"]
        V_ENG["WarGalleyEngine\nTurn Resolution"]
        C_RES["CombatResolver\nRAM / OAR_RAKE / Doctrines"]
        AI["NavalAI\nAutonomous Actions"]
        SEA["SeasonalManager\nMP Modifiers"]
    end

    subgraph Admin ["Admin Dashboard (Port 8080)"]
        API["api_service.py\nFlask REST API"]
        STATE["engine_state.json\nIPC via shared volume"]
    end

    UI -->|"Signed TCP Packet"| TLS
    TLS -->|"Decrypted bytes"| HMAC
    HMAC --> PKT
    PKT --> V_ENG
    V_ENG --> C_RES
    V_ENG --> AI
    V_ENG --> SEA
    V_ENG -->|"Signed JSON response"| UI
    V_ENG -->|"Atomic write"| STATE
    STATE --> API
    VIS -.->|"Reads state"| V_ENG
```

## Component Descriptions

**PacketParser** validates every incoming packet against a JSON Schema before checking the HMAC signature. Malformed or tampered packets are dropped and logged before reaching the engine.

**WarGalleyEngine** is the single authoritative source of truth. It holds the vessel list, processes seasonal modifiers, delegates movement, and calls CombatResolver for RAM and OAR_RAKE commands. It returns a serialised vessel state list after every tick.

**CombatResolver** handles all damage calculations using `apply_damage()` on the Vessel base class. It also implements the three national doctrines: Corvus boarding (Rome), crew speed burst (Carthage), and Ballista fire (Egypt).

**NavalAI** provides autonomous actions (RETREAT or ATTACK_NEAREST) for vessels that fall outside the flagship command radius.

**SeasonalManager** applies per-season MP modifiers and storm attrition at the start of each turn.

**api_service.py** exposes a single authenticated GET endpoint (`/api/v1/telemetry`) that reads `engine_state.json`, which is written atomically by `main.py` after every tick via a shared Podman volume.

## Security Architecture

All packets are signed with HMAC-SHA256 (FIPS 140-2). The server validates signature before any game logic executes. TLS 1.3 transport encryption is planned for v1.1. The Admin API requires a Bearer token validated using `hmac.compare_digest()` to prevent timing attacks.

## Container Architecture

```mermaid
graph TB
    subgraph Podman_Network ["wargalley-net (bridge)"]
        LC["wargalley_logic\nPython 3.12-slim\nPort 5555\nread-only rootfs"]
        WEB["wargalley_web\nPython 3.12-slim\nPort 8080\nread-only rootfs"]
    end
    VOL["./Engine/logs\nShared Volume :Z"]
    LC -->|"engine_state.json"| VOL
    WEB -->|"reads state"| VOL
```

Both containers run with `read_only: true`, `tmpfs` mounts for `/tmp` and `/run`, CPU and memory resource limits, and a default seccomp profile (CIS Level 2).
