# RACI Matrix — War Galley v1.0

**Roles:**
- **Admiral** — Project Lead / Product Owner
- **Strategist** — Developer / Engineer
- **Centurion** — QA / Analyst / Operator
- **Consul** — Security / Compliance Officer

*R = Responsible (does the work), A = Accountable (owns the outcome), C = Consulted (input required), I = Informed (notified of outcome)*

---

## Development Tasks

| Task | Admiral | Strategist | Centurion | Consul |
|---|---|---|---|---|
| Scenario logic design | A | R | C | I |
| Engine feature development | I | A/R | C | I |
| National doctrine implementation | C | A/R | C | I |
| Unity C# bridge scripts | I | A/R | C | I |
| Blender asset generation | C | A/R | I | I |
| Test suite authoring and maintenance | I | A/R | C | I |
| CI/CD pipeline maintenance | I | A/R | I | C |
| JSON schema authoring | I | A/R | C | C |

## Security Tasks

| Task | Admiral | Strategist | Centurion | Consul |
|---|---|---|---|---|
| HMAC key generation (initial) | A | R | I | C |
| HMAC key rotation (monthly) | A | R | C | C |
| Security hardening (FIPS/OWASP/STIG) | C | A/R | I | R |
| Scenario signing (`--sign-all`) | I | R | R | A |
| Bandit SAST scan review | I | R | I | A |
| Dependency CVE audit (`pip-audit`) | I | R | I | A |
| Trivy container image scan | I | R | I | A |
| Admin API key management | A | R | I | C |
| Legal review (GMT Games IP) | A | I | I | C |

## Operations Tasks

| Task | Admiral | Strategist | Centurion | Consul |
|---|---|---|---|---|
| Container deployment | A | R | C | I |
| Container restart after crash | I | C | R/A | I |
| Log monitoring (daily) | I | I | A/R | C |
| Security violation escalation | I | C | R | A |
| Backup of `signatures.db` and logs | I | I | A/R | I |
| Performance monitoring | I | C | A/R | I |

## Documentation Tasks

| Task | Admiral | Strategist | Centurion | Consul |
|---|---|---|---|---|
| Architecture Guide | C | A/R | I | C |
| API Guide | I | A/R | C | I |
| Security Compliance document | C | R | I | A |
| RACI / RBAC maintenance | A | R | C | C |
| User Guide | C | R | A | I |
| Deployment Guide | I | A/R | C | I |
| Maintenance Guide | I | R | A | C |
| Support Tasks Guide | I | R | A | I |
| Container Build Guide | I | A/R | C | C |
| Release Notes | A | R | C | I |
