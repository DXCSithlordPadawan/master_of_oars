# Role-Based Access Control (RBAC) — War Galley v1.0

## Role Definitions

| Role | Description | Permissions | Technical Enforcement |
|---|---|---|---|
| **Administrator** | Full system control | Full config access, key rotation, container exec, log deletion | Host OS access; `.env` file ownership (`chmod 600`); `podman exec` on both containers |
| **Scenario Designer** | Creates and signs game scenarios | Write access to `Scenarios/*.json`; run `--sign-all` | Git repository write access; `python Engine/security_utils.py --sign-all` (requires `HMAC_KEY` in `.env`) |
| **Analyst** | Reads telemetry and logs | Read-only access to dashboard and log files | Bearer token for `GET /api/v1/telemetry` (enforced by `hmac.compare_digest()` in `api_service.py`); read-only filesystem access to `Engine/logs/` |
| **Developer** | Modifies source code | Code write access; run test suite; CI/CD pipeline | Git repository write access; `pytest Engine/tests/`; CI pipeline secrets (`UNITY_LICENSE`, `GITHUB_TOKEN`) |
| **Player** | Submits game turn commands | Send signed `PLAYER_ACTION` and `INIT_SCENARIO` packets | TCP Port 5555 — packets validated by `PacketParser` (JSON Schema + HMAC); invalid packets silently dropped |

---

## Permission Matrix

| Action | Administrator | Developer | Scenario Designer | Analyst | Player |
|---|---|---|---|---|---|
| Edit `.env` / rotate HMAC key | ✅ | ❌ | ❌ | ❌ | ❌ |
| Run `--sign-all` | ✅ | ✅ | ✅ | ❌ | ❌ |
| Edit scenario JSON files | ✅ | ✅ | ✅ | ❌ | ❌ |
| Call `GET /api/v1/telemetry` | ✅ | ✅ | ❌ | ✅ | ❌ |
| Send `INIT_SCENARIO` packet | ✅ | ✅ | ✅ | ❌ | ✅ |
| Send `PLAYER_ACTION` packet | ✅ | ✅ | ❌ | ❌ | ✅ |
| View `Engine/logs/security.log` | ✅ | ✅ | ❌ | ✅ | ❌ |
| Execute inside containers | ✅ | ❌ | ❌ | ❌ | ❌ |
| Modify source code | ✅ | ✅ | ❌ | ❌ | ❌ |
| Run test suite | ✅ | ✅ | ❌ | ❌ | ❌ |

---

## Technical Enforcement Details

**TCP Port 5555 (Player / Engine):** All packets validated by `PacketParser` using `jsonschema.validate()` then `SecurityManager.verify_scenario()`. Unauthenticated or malformed packets are logged and dropped — no error detail is returned to the sender (OWASP A07).

**HTTP Port 8080 (Analyst / Dashboard):** Flask route `/api/v1/telemetry` is protected by a `Bearer` token check using `hmac.compare_digest()` (constant-time comparison, prevents timing attacks). Failed requests return HTTP 401 with no body (OWASP A07).

**File permissions:** `.env` and `Scenarios/signatures.db` must be `chmod 600`. The `init_project.sh` script sets this on first run. The `--sign-all` CLI enforces `0o600` on `signatures.db` at write time via `os.chmod()`.

**Container isolation:** Both containers run as `strategy_user` (non-root). The root filesystem is `read_only: true`. Resource limits prevent privilege escalation via resource exhaustion.
