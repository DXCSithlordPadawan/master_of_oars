# ⚓ War Galley v1.0: Master Project Documentation

## 1. Product Requirements Document (PRD)

### 1.1 Project Vision
**War Galley** is a high-fidelity (Unity Engine), authoritative-server naval simulation designed to model the tactical and strategic complexities of Mediterranean warfare (480 BC – 250 BC). It balances historical rigor with modern cybersecurity standards (FIPS 140-2, NIST).

### 1.2 Functional Requirements (FR)
| ID | Requirement | Description |
| :--- | :--- | :--- |
| **FR-01** | **Authoritative Logic** | All movement and combat must be calculated in the Python backend. |
| **FR-02** | **Command Radius** | Units outside the Flagship's signal range enter an AI-driven "Autonomous" state. |
| **FR-03** | **Fatigue Simulation** | Rowing speed directly impacts crew stamina and available Movement Points (MP). |
| **FR-04** | **National Doctrines** | Unique mechanics for Rome (Corvus), Carthage (MP Boost), and Egypt (Artillery). |

### 1.3 Technical Stack
- **Backend:** Python 3.12 (Logic Core).
- **Frontend:** Unity 3D (Visualization & Input).
- **Communication:** TCP Socket (Port 5555) using JSON serialization.
- **Containerization:** Podman (Rootless, CIS Level 2 hardened).

---

## 2. UI Design Document & Style Guide

### 2.1 Design Philosophy
**"Tactical Minimalism."** High-density information (stamina, hull, command range) is available at a glance without obstructing the 3D battlefield.

### 2.2 Visual Style Guide
- **Palette:** - Athenian Bronze (`#CD7F32`): Borders, Icons, Selection Box.
  - Deep Ionian (`#1A2A3A`): Backgrounds and HUD panels.
  - Tyrant Red (`#E74C3C`): Enemy units and Critical failure.
  - Olive Leaf (`#2ECC71`): Allied units and Full status.
- **Typography:** - Headings: `Cinzel` or `Trajan` (Serif).
  - Data: `Roboto Mono` (Monospace).

---

## 3. Asset & Modeling Standards (Blender 5 to Unity)

### 3.1 Export Configuration
- **Orientation:** `-Z Forward`, `Y Up`.
- **Pivot Point:** Must be at the **Waterline (Y=0)** at the center of the vessel's length.
- **Scale:** Fixed at `1.0`.

### 3.2 Internal Hierarchy
1. `Vessel_Root`
   - `Hull_Mesh` (Main Geometry)
   - `Oar_Bank_Port` (Parent for left-side oars)
   - `Oar_Bank_Starboard` (Parent for right-side oars)
   - `Socket_Ram` (Empty transform for collision logic)

---

## 4. Performance & Optimization Guide

### 4.1 Rendering
- **GPU Instancing:** Enabled on all materials to batch 100+ vessels into single draw calls.
- **Vertex Animation:** Oar movement is handled by the `OarShader.shader` (HLSL) to offload animation from the CPU.

### 4.2 Network Throttling
- **Tick Rate:** Server operates at 20Hz.
- **Interpolation:** Unity client uses `Vector3.Lerp` to smooth movement between server ticks.

---

## 5. Security & Compliance (FIPS/NIST)

### 5.1 Data Integrity
All scenario files and player action packets are signed using **HMAC-SHA256**. The engine rejects any data that fails the signature verification check.

### 5.2 Infrastructure
The environment is containerized via **Podman** with the following security flags:
- `--security-opt label=disable` (where SELinux allows).
- Non-root user execution (`USER strategy_user`).
- Read-only root filesystem where applicable.

---

## 6. First Launch & Deployment Checklist

### Phase 1: Infrastructure
- [ ] Run `init_project.sh` to generate `.env` and folder structures.
- [ ] Run `python Engine/security_utils.py --sign-all` to initialize signatures.
- [ ] Execute `podman compose up -d` to launch the stack.

### Phase 2: Frontend Integration
- [ ] Import `.fbx` models into `Assets/Models`.
- [ ] Assign `VesselBridge.cs` to the `GameManager` in Unity.
- [ ] Set `VesselBridge` IP to `127.0.0.1` and Port `5555`.

### Phase 3: Verification
- [ ] Verify "Connection Established" in Unity Console.
- [ ] Check `localhost:8080` for Admin Dashboard telemetry.
