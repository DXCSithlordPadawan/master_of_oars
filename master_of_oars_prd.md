# PRD: War Galley v1.0

## 1. Project Overview
A secure, authoritative naval simulation engine focusing on 1st-person command and 3rd-person tactical management of ancient Mediterranean fleets.  The game is based on the rule from https://www.gmtgames.com/living_rules/WG%20rules-2006.pdf

## 2. Technical Goals
- **Separation of Concerns:** Unity handles pixels; Python handles physics.
- **Security:** NIST/FIPS compliant data integrity.
- **Scalability:** 100+ ships using GPU instancing and vertex shaders.

## 3. Core Mechanics
### 3.1 The Command Pulse
Units must remain within X units of a Flagship to receive player orders. Failure results in AI takeover (Autonomous Mode).

### 3.2 Fatigue & MP
Movement Points (MP) are a finite resource per turn, influenced by the Crew Stamina attribute. Over-sprinting leads to permanent stamina loss for that encounter.

## 4. Compliance Matrix
| Standard | Implementation |
| :--- | :--- |
| FIPS 140-2 | HMAC-SHA256 Signing |
| CIS Level 2 | Rootless Podman |
| DISA STIG | Encrypted Audit Logs |
| OWASP | Schema Validation |

## 5. Deployment
Must be deployable via `podman-compose` to ensure service orchestration between the Logic Engine and Admin UI.