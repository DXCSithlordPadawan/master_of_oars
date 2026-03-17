#!/bin/bash
# Podman Stack Launcher

echo "[*] Initializing War Galley Multi-Service Stack..."

# Check for podman-compose or use podman compose
if command -v podman-compose &> /dev/null; then
    podman-compose up -d
else
    podman compose up -d
fi

echo "[+] Stack is live."
echo "[+] Unity Bridge: localhost:5555"
echo "[+] Admin Dashboard: http://localhost:8080"