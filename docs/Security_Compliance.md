# Security Compliance Document

## Applied Standards
* **FIPS 140-2:** All cryptographic modules (HMAC-SHA256) for scenario signing follow FIPS-approved algorithms.
* **OWASP Top 10:** Protection against Injection (JSON Schema Validation) and Broken Access Control (RBAC).
* **DISA STIG:** Automated logging of administrative actions and secure configuration of the TCP listener.
* **CIS Benchmark Level 2:** Containerized deployment using rootless Podman with restricted syscalls.

## Security Gap Analysis
| Identified Risk | Mitigation Strategy | Status |
| :--- | :--- | :--- |
| **Telemetry Tampering** | Authoritative state resolution in Python backend. | Resolved |
| **Scenario Spoofing** | Mandatory HMAC signature check on JSON load. | Resolved |
| **Secret Exposure** | Env-var isolation for HMAC keys (No hardcoding). | Resolved |
| **Man-in-the-Middle** | TLS 1.3 encryption for backend communication. | In Progress |