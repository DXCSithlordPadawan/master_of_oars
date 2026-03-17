# Maintenance & Operations Guide — War Galley v1.0

## Daily Tasks

- Monitor `Engine/logs/security.log` for failed HMAC validations and rejected packets.
- Check `Engine/logs/engine_state.json` for current engine status (written after every tick).
- Review the Admin Dashboard at `http://localhost:8080/api/v1/telemetry` for anomalies.

## Weekly Tasks

- Run the full test suite to verify engine integrity:

  ```bash
  cd master_of_oars
  pip install -r Engine/requirements.txt
  pytest Engine/tests/ -v
  ```

- Run `bandit` SAST scan on the Engine directory:

  ```bash
  bandit -r Engine/ -ll --exclude Engine/tests
  ```

- Run dependency CVE audit:

  ```bash
  pip-audit -r Engine/requirements.txt
  ```

## Monthly Tasks

### HMAC Key Rotation

Key rotation replaces `HMAC_KEY` in `.env`, re-signs all scenarios, and restarts the engine:

1. Generate a new 32-character key: `openssl rand -hex 32`
2. Edit `.env` and replace `HMAC_KEY` with the new value.
3. Re-sign all scenarios: `python Engine/security_utils.py --sign-all`
4. Verify `Scenarios/signatures.db` has been updated (check file modification time).
5. Restart the engine container: `podman compose restart logic-engine`
6. Confirm the dashboard returns `"engine_running": false` (engine ready, awaiting client).

### Backup Procedure

Back up the following files before any key rotation or upgrade:

| File | Purpose |
|---|---|
| `Scenarios/signatures.db` | HMAC signatures for all scenario files |
| `Engine/logs/security.log` | Audit trail (rotate after backup if > 25 MB) |
| `Engine/logs/engine_state.json` | Last known engine state |
| `.env` | Environment config (store encrypted, never in Git) |

## Container Health Checks

```bash
podman ps                          # Confirm both containers are running
podman logs wargalley_logic        # Engine logs
podman logs wargalley_web          # Dashboard logs
podman stats --no-stream           # CPU / memory usage vs limits
```

## Deployment Hardening Checklist

- Podman running in rootless mode (`podman info | grep rootless`)
- No ports exposed beyond 5555 (engine) and 8080 (dashboard)
- `.env` file has `chmod 600` permissions
- `Scenarios/signatures.db` has `chmod 600` permissions
- Both containers have `read_only: true` and resource limits set in `podman-compose.yaml`
