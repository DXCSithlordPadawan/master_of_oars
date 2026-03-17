# 📁 War Galley v1.0 Repository Checklist

Ensure the following file structure is present in the root of your repository before the final commit.

```
WarGalley/
├── .github/
│   └── workflows/
│       └── ci-cd.yaml          # Automated testing and container builds
├── Assets/                     # Unity Project Frontend
│   ├── Models/                 # .fbx files and .meta manifests
│   ├── Prefabs/                # Pre-configured Ship and FX objects
│   ├── Scripts/                # C# Bridge and Input logic
│   ├── Shaders/                # HLSL Oar and Water shaders
│   └── Textures/               # PBR Maps (Bronze, Wood, etc.)
├── Engine/                     # Python Authoritative Backend
│   ├── __init__.py
│   ├── api_service.py          # Flask/FastAPI Telemetry
│   ├── main.py                 # Core Logic Loop
│   ├── packet_parser.py        # JSON/TCP Handling
│   ├── security_utils.py       # HMAC/FIPS Signing logic
│   └── vessel_factory.py       # Object Inheritance
├── Web/                        # Admin Dashboard
│   ├── css/
│   ├── js/
│   └── index.html
├── Scenarios/                  # Simulation Data
│   ├── salamis_0480bc.json     # Example Scenario
│   └── signatures.db           # HMAC Hash Database (GitIgnored in Prod)
├── Docs/                       # Project Documentation
│   ├── PRD.md
│   ├── UI_Style_Guide.md
│   └── Performance_Guide.md
├── .env.example                # Template for HMAC Keys/Ports
├── .gitignore                  # Standard Unity/Python/OS ignores
├── init_project.sh             # Setup script
├── podman-compose.yaml         # Service Orchestration
├── Podmanfile                  # Container Blueprint
├── LICENSE                     # Project License
└── README.md                   # Master Project Documentation
```

## 1. Root Configuration
- [ ] `.env.example`: Template for environment variables (Do not commit actual `.env`).
- [ ] `.gitignore`: Must include `/Library/`, `/Temp/`, `__pycache__/`, and `.env`.
- [ ] `podman-compose.yaml`: Orchestration for `wargalley_logic` and `wargalley_web`.
- [ ] `init_project.sh`: Automated directory and permission setup script.

## 2. Backend Engine (`/Engine`)
- [ ] `main.py`: Entry point for the simulation.
- [ ] `security_utils.py`: HMAC-SHA256 signing utility.
- [ ] `vessel_factory.py`: Logic for Triremes, Quinqueremes, and Merchants.
- [ ] `packet_parser.py`: TCP socket management.

## 3. Unity Frontend (`/Assets`)
- [ ] `Scripts/VesselBridge.cs`: The C# TCP client.
- [ ] `Shaders/OarShader.shader`: HLSL vertex animation code.
- [ ] `Models/`: All exported `.fbx` models and their associated `.meta` files.
- [ ] `Prefabs/`: Prefabricated ship objects with `VesselController.cs` attached.

## 4. Documentation & Scenarios (`/Docs` & `/Scenarios`)
- [ ] `README.md`: Master documentation and launch guide.
- [ ] `Scenarios/*.json`: At least one valid, signed starting scenario.
- [ ] `Docs/UI_Style_Guide.md`: Visual standards for UI/UX.

## 5. Deployment Hardware (`/Podmanfile`)
- [ ] `Podmanfile`: Hardened container definition (non-root user, specific Python version).
- [ ] `.github/workflows/`: (Optional) Actions for automated build testing.