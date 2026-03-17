# Container Build Guide — War Galley v1.0

## Prerequisites

- Podman >= 4.x configured for rootless operation
- `podman-compose` >= 1.0 (or `podman compose` plugin)
- Python 3.12+ on the host (for pre-build signing step)

### Verify Rootless Podman

```bash
podman info | grep -i rootless
# Expected: rootless: true
```

If not rootless, configure with: `podman system migrate`

---

## Building the Engine Image

```bash
podman build -t wargalley-engine:latest -f Podmanfile .
```

The `Podmanfile` performs the following steps:

1. Uses `python:3.12-slim` as a minimal base (reduced attack surface)
2. Sets `PYTHONDONTWRITEBYTECODE=1` and `PYTHONUNBUFFERED=1`
3. Creates a non-privileged user `strategy_user` in group `strategy_group` (DISA STIG requirement)
4. Installs only the system dependencies required by `pythonnet` (`gcc`, `libglib2.0-0`)
5. Installs Python dependencies from `Engine/requirements.txt` with `--no-cache-dir`
6. Copies only `Engine/`, `Scenarios/`, and `.env` into the image
7. Sets ownership to `strategy_user` and switches to that user before `CMD`
8. Exposes only port 5555

---

## CIS Level 2 Hardening Applied

The following hardening flags are set in `podman-compose.yaml` for both services:

| Control | Setting | Rationale |
|---|---|---|
| Read-only root filesystem | `read_only: true` | Prevents writes to the container filesystem |
| Transient temp storage | `tmpfs: [/tmp, /run]` | Allows necessary transient writes without a writable rootfs |
| CPU limit | `1.0` cores (logic), `0.5` cores (web) | Prevents runaway process from starving the host |
| Memory limit | `512M` (logic), `256M` (web) | Caps RAM usage; triggers OOM kill before host is affected |
| Seccomp profile | `seccomp:unconfined` (default) | Restricts available syscalls to the default safe set |
| Non-root user | `strategy_user` | Container process does not run as UID 0 |

---

## Building the Full Stack

Sign scenarios, then start both containers:

```bash
python Engine/security_utils.py --sign-all
podman compose up -d --build
```

`--build` forces a rebuild of the `logic-engine` image. Omit it for faster restarts when only configuration has changed.

---

## Scanning the Image for Vulnerabilities

```bash
# Install Trivy (if not already present)
# https://aquasecurity.github.io/trivy/

trivy image --severity CRITICAL,HIGH wargalley-engine:latest
```

The CI pipeline (`ci-cd.yml`) runs this scan automatically on every push to `main`. A build with CRITICAL or HIGH CVEs fails the pipeline.

---

## Running Bandit SAST Locally

```bash
bandit -r Engine/ -ll --exclude Engine/tests
```

`-ll` reports MEDIUM and HIGH severity findings. Zero HIGH findings are required before release.

---

## Git LFS for FBX Assets

FBX files in `Assets/Models/` are binary and large (~1.3 MB each for rigged characters). They must be tracked with Git LFS before committing:

```bash
git lfs install
git lfs track "*.fbx"
git add .gitattributes
git add Assets/Models/
git commit -m "Add Blender-MCP generated FBX assets"
```

Verify LFS tracking: `git lfs status`

---

## Environment Variable Injection

The engine container reads all configuration from `.env` via the `env_file` directive in `podman-compose.yaml`. The `.env` file is **never committed to Git** (it is listed in `.gitignore`). Use `.env.example` as the template.

Required variables for a valid container start:

```
HMAC_KEY=<32+ char key>
ADMIN_API_KEY=<32+ char key, different from HMAC_KEY>
SERVER_IP=0.0.0.0
SERVER_PORT=5555
ENV_MODE=PRODUCTION
LOG_PATH=./Engine/logs/security.log
AUDIT_LOG_LEVEL=INFO
```
