# Deployment Guide — War Galley v1.0

## Prerequisites

- Podman >= 4.x (rootless mode — CIS Level 2)
- `podman-compose` or `podman compose`
- Git with Git LFS configured (for FBX binary assets)
- Python 3.12+ (for the `--sign-all` signing step on the host, pre-container)

---

## Step-by-Step Deployment

### 1. Clone the Repository

```bash
git clone <repository-url> master_of_oars
cd master_of_oars
git lfs pull   # Pull FBX binary assets from Git LFS
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and set the following mandatory values:

| Variable | Requirement |
|---|---|
| `HMAC_KEY` | Minimum 32 characters. Generate with: `openssl rand -hex 32` |
| `ADMIN_API_KEY` | Minimum 32 characters. Must differ from `HMAC_KEY` |
| `SERVER_IP` | `0.0.0.0` for container deployment |
| `ENV_MODE` | Set to `PRODUCTION` |

### 3. Sign All Scenarios

The engine will refuse to load any scenario that has not been signed. Run the signing script once after setting `HMAC_KEY`:

```bash
pip install python-dotenv
python Engine/security_utils.py --sign-all
```

This writes `Scenarios/signatures.db` with HMAC-SHA256 signatures for every `.json` file in `Scenarios/`. The file is written with `0o600` permissions.

### 4. Build and Start the Containers

```bash
podman compose up -d
```

This builds the `wargalley_logic` image from `Podmanfile` and starts both services:

| Container | Port | Purpose |
|---|---|---|
| `wargalley_logic` | 5555 | Authoritative Python engine (TCP) |
| `wargalley_web` | 8080 | Admin dashboard (HTTP) |

Both containers run with read-only root filesystems, CPU/memory limits, and a seccomp profile.

### 5. Verify Services Are Running

```bash
podman ps
```

Check engine is accepting connections:

```bash
curl -H "Authorization: Bearer <ADMIN_API_KEY>" http://localhost:8080/api/v1/telemetry
```

Expected response includes `"engine_running": false` until Unity connects and sends `INIT_SCENARIO`.

### 6. Launch Unity Client

Open the Unity project and enter Play Mode. The `VesselBridge.cs` script connects to `SERVER_IP:5555` and sends `INIT_SCENARIO` to start the session.

---

## Stopping and Restarting

```bash
podman compose down          # Stop and remove containers
podman compose up -d         # Restart
podman compose logs -f       # Follow logs from both containers
```

---

## Key Rotation (Post-Deployment)

To rotate the HMAC key without downtime:

```bash
python Engine/security_utils.py --sign-all   # Re-sign with new key after editing .env
podman compose restart logic-engine          # Reload container with new key
```

See `Maintenance_Guide.md` for full rotation procedure.
