# ⚓ War Galley v1.0: First Launch Checklist

Use this checklist to verify the integrity of the environment, security handshake, and asset alignment before initiating the first "Sea Trial."

---

## Phase 1: Infrastructure & Backend (Podman)
- [ ] **Environment Initialization:** Run `./init_project.sh` to ensure the `.env` file and local log directories exist.
- [ ] **Security Key Sync:** Verify that the `HMAC_KEY` in `.env` is a 32-character hex string.
- [ ] **Scenario Signing:** Run `python Engine/security_utils.py --sign-all`. Confirm that `Scenarios/signatures.db` is generated and contains hashes for your `.json` files.
- [ ] **Container Launch:** Run `podman-compose up -d`.
- [ ] **Port Audit:** Run `podman ps` to confirm:
    - Port `5555` (TCP) is mapped for the Unity Bridge.
    - Port `8080` (HTTP) is mapped for the Admin Dashboard.
- [ ] **Log Verification:** Run `podman logs wargalley_logic` and confirm the message: `[INFO] Authoritative Engine listening on 0.0.0.0:5555`.

---

## Phase 2: Unity Client Configuration
- [ ] **Asset Import:** Confirm all `.fbx` files in `Assets/Models/` have their scale set to `1.0` and "Read/Write" enabled in the Import Settings.
- [ ] **Physics Layers:** Ensure a Layer named `Vessels` is created in Unity and assigned to all ship Prefabs.
- [ ] **Bridge Setup:** - Attach `VesselBridge.cs` to a persistent `GameManager` object.
    - Set the IP Address to `127.0.0.1`.
    - Set the Port to `5555`.
- [ ] **Input Management:** Assign the `Selection Box` UI element (RectTransform) to the `NavalInputManager` script.

---

## Phase 3: Runtime Validation
- [ ] **Handshake Check:** Upon pressing 'Play' in Unity, verify the console logs: `Connection Established with Authoritative Engine`.
- [ ] **HMAC Validation:** Attempt to move a vessel. Verify that the Python logs show `[AUTH] Signature Verified for Action: PLAYER_MOVE`.
- [ ] **Visual Sync:** Ensure the oars move via the `OarShader` when the vessel's `stamina` is above 0.
- [ ] **Telemetry Check:** Open `http://localhost:8080` and confirm that the "Active Vessels" count matches the number of ships in the Unity scene.

---

## Phase 4: Error Handling (Troubleshooting)
- [ ] **Connection Refused:** Check if your OS Firewall is blocking port `5555`.
- [ ] **Signature Mismatch:** Re-run the `security_utils.py` script. Any manual change to a `.json` scenario file invalidates its signature.
- [ ] **Upside-Down Vessels:** Check the `.fbx` import settings. Ensure "Bake Axis Conversion" is checked or orientation is set to `-Z Forward, Y Up`.