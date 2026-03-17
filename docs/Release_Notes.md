# ⚓ War Galley Release Notes

## [v1.0.0-Alpha] - 2026-03-14

### 🚀 New Features
- **Authoritative Logic Engine:** Core simulation moved to Python 3.12 for server-side truth.
- **HMAC Security Layer:** Implementation of FIPS 140-2 compliant packet signing to prevent client-side manipulation.
- **Procedural Oar System:** HLSL-driven vertex animation for oars, supporting 100+ vessels at 60 FPS.
- **Command Radius:** Implemented Flagship signal logic; units now toggle between Player and AI control based on proximity.
- **Fatigue Mechanics:** Added rowing-speed to stamina-drain ratios and MP (Movement Point) penalties.

### 🎨 Visual & Asset Updates
- **Trireme Hull v1:** High-detail FBX with oxidized bronze and aged oak PBR materials.
- **Naval Wake System:** Procedural scrolling foam shaders that scale with vessel velocity.
- **Environment:** Low-poly rock obstacles and procedural Mediterranean seabed generation.

### 🔧 Technical Optimizations
- **GPU Instancing:** Automated batching for all vessel classes.
- **Podman Orchestration:** Containerized deployment for consistent environments across Dev/Ops.
- **RTS Selection:** Added 2D-to-3D screen-space box selection for fleet management.

### 🛡️ Security & Compliance
- **NIST 800-53:** Initial audit logging implemented in the `api_service`.
- **RBAC:** Internal role-based access for the Admin Dashboard.

### 🐞 Bug Fixes
- Fixed "Inverted Z-Axis" issue during Blender-to-Unity FBX export.
- Resolved race condition where Unity would attempt to connect before the Python socket was initialized.
- Corrected Hull Integrity calculation where ramming damage was not factoring in vessel mass.

---

## 📈 Known Issues
- Vessels may clip through landmasses if the `Physics.Raycast` update exceeds 50ms.
- Admin Dashboard telemetry lag of ~1s during high-unit-count collisions.

## 🗺️ Roadmap
- **v1.1.0:** Multiplayer Lobby & NAT Punchthrough.
- **v1.2.0:** Weather Systems (Storms and High Seas impact on MP).
- **v1.3.0:** Custom Fleet Builder and Persistent Campaign Map.