# War Galley v1.0: Performance & Optimization Guide

This document outlines the configuration required to support large-scale naval engagements (100-300 units) at 60 FPS.

## 1. Rendering Strategy: GPU Instancing
To minimize Draw Calls, all vessel materials must support GPU Instancing.
* **Component:** `VesselController.cs`
* **Implementation:** Use `MaterialPropertyBlock` to set individual ship colors or damage states without breaking the instance batch.

## 2. Vertex-Driven Animation
**Strict Prohibition:** Do not use Animator components or Bone-rigs for oars.
* **Logic:** All oar movement is calculated in the `NavalOars.hlsl` vertex shader. 
* **Impact:** Reduces CPU overhead by ~70% for oar-heavy fleets.

## 3. Network & Logic Throttling
The Python backend (Authoritative Server) should not send updates every frame.
* **Tick Rate:** Set `main.py` logic to 20Hz (20 ticks per second).
* **Interpolation:** The Unity client uses `Vector3.Lerp` to smooth the movement between these 20Hz updates, providing a 60fps visual experience with 20fps data costs.

## 4. UI Optimization
The "Command Pulse" and "Selection Box" use the **Canvas System**.
* **Optimization:** Disable `Pixel Perfect` on the UI Canvas. 
* **Static UI:** Use a separate Canvas for static elements (HUD) and dynamic elements (Health bars over ships) to prevent constant re-batching of the entire UI.

## 5. Memory Management (NIST/DISA Compliance)
* **Heap Allocation:** Minimize `new` keyword usage in `Update()` loops.
* **Pooling:** Use Object Pooling for `OarSplash` particles and `Missile` (Arrow/Ballista) projectiles.