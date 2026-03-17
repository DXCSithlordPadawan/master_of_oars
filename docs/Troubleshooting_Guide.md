# War Galley v1.0: Network & Integration Troubleshooting Guide

This guide addresses common failures in the bridge between the Python Authoritative Engine and the Unity Client.

## 1. Socket & Connectivity Errors

### [C#] `SocketException: Connection Refused`
- **Cause:** Unity cannot find the Python server at the specified IP/Port.
- **Fix:** 1. Check if the Podman container is running: `podman ps`.
  2. Verify the port mapping in `podman-compose.yaml`. It must be `5555:5555`.
  3. Ensure your Firewall isn't blocking local TCP traffic on `5555`.

### [C#] `SocketException: Connection Reset by Peer`
- **Cause:** The Python server crashed or forcibly closed the connection.
- **Fix:** Check Python logs: `podman logs wargalley_logic`. Usually caused by an unhandled exception in the `packet_parser.py`.

---

## 2. Security & HMAC Failures

### [Python] `[CRITICAL] HMAC Verification Failed`
- **Cause:** The packet sent by Unity was tampered with or used an incorrect secret key.
- **Fix:** 1. Ensure the `HMAC_KEY` in your `.env` file is identical to the key hardcoded (or loaded) in Unity's `VesselBridge.cs`.
  2. Ensure Unity is signing the *entire* JSON string, including brackets and whitespace.

### [Python] `[WARNING] Scenario Hash Mismatch`
- **Cause:** The `.json` scenario file in Unity is different from the one on the server.
- **Fix:** Re-run `python security_utils.py --sign-all`. Never edit a scenario file without re-generating the signature database.

---

## 3. Visual & Transform Glitches

### Vessels are "Stuttering" or "Jumping"
- **Cause:** Network latency is high or the Server Tick Rate (20Hz) is fighting Unity's Update loop.
- **Fix:** Increase the `interpolationFactor` in your `VesselController.cs`. Use `Vector3.Lerp(current, target, Time.deltaTime * smoothing)`.

### Oars are Static or Rotating Incorrectly
- **Cause:** The `_RowSpeed` parameter in the `OarShader` isn't receiving data.
- **Fix:** 1. Check Unity Inspector: Is the `Material` actually using the `Custom/OarShader`?
  2. Ensure the C# code uses the exact string `_RowSpeed` when calling `material.SetFloat()`.

---

## 4. Administrative Dashboard (Web)

### `404 Not Found` on http://localhost:8080
- **Cause:** The `api_service.py` failed to start.
- **Fix:** Verify the Python container has the Flask/FastAPI dependencies installed. Run `podman exec -it wargalley_logic pip list`.

### Dashboard shows "0 Vessels" despite Unity being connected
- **Cause:** The Logic Engine isn't pushing state updates to the API internal memory.
- **Fix:** Verify `main.py` is calling `api_service.update_state(current_fleet)` at the end of every tick.