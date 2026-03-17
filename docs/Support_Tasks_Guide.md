# Support Tasks Guide — War Galley v1.0

## Common Operator Tasks

### Restarting the Engine After a Crash

```bash
podman compose down
podman compose up -d
podman logs wargalley_logic --tail 50
```

Check that the last log line reads: `Authoritative Engine listening on 0.0.0.0:5555`.

### Checking for Security Violations

```bash
grep "SECURITY ALERT" Engine/logs/security.log
```

Each line shows a timestamp, the packet type, and the source address. Repeated violations from the same IP should be escalated to the Administrator role for firewall action.

### Verifying Scenario Signatures

```bash
python Engine/security_utils.py --sign-all
```

Re-running `--sign-all` is safe and idempotent. It overwrites `Scenarios/signatures.db` atomically. Run this any time a scenario `.json` file is edited.

### Rotating the HMAC Key

See `Maintenance_Guide.md` — Monthly Tasks — HMAC Key Rotation.

### Viewing Live Engine State

```bash
cat Engine/logs/engine_state.json
```

Or via the authenticated API:

```bash
curl -H "Authorization: Bearer <ADMIN_API_KEY>" http://localhost:8080/api/v1/telemetry
```

### Running the Test Suite

```bash
pytest Engine/tests/ -v --tb=short
```

All tests must pass before any deployment. A failing test suite must be escalated to the Developer role before proceeding.

### Checking Container Resource Usage

```bash
podman stats --no-stream
```

If `wargalley_logic` is consistently near its memory limit (512 MB), escalate to the Developer role to profile the engine for memory leaks.

---

## Escalation Paths

| Symptom | First Responder | Escalate To |
|---|---|---|
| HMAC validation failures in logs | Analyst (Centurion) | Developer (Strategist) |
| Engine container OOM-killed | Analyst | Developer |
| `signatures.db` missing or corrupt | Analyst | Developer (re-run `--sign-all`) |
| Unity cannot connect on port 5555 | Analyst | Administrator |
| Admin API returning 401 | Analyst | Administrator (check `ADMIN_API_KEY` in `.env`) |
| Test suite regression | Developer | Project Lead (Admiral) |

---

## Known Issues

Refer to `Release_Notes.md` for the current list of known issues and their workarounds.

TLS 1.3 transport encryption on port 5555 is not yet implemented. Until it is, the engine should only be reachable on a trusted internal network or VPN. This is tracked as a planned feature in `Architecture_Guide.md`.

---

## Reference Documents

- `Deployment_Guide.md` — initial setup and container startup
- `Maintenance_Guide.md` — backup and rotation procedures
- `RBAC_Matrix.md` — role permissions and technical enforcement
- `Troubleshooting_Guide.md` — diagnostic flowcharts
- `API_Guide.md` — packet formats and REST endpoint specification
