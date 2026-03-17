#!/bin/bash
# War Galley Project Initializer

echo "[*] Creating directory structure..."
mkdir -p Engine/logs
mkdir -p Scenarios
mkdir -p docs
mkdir -p build

echo "[*] Generating .env from template..."
if [ ! -f .env ]; then
    cat <<EOF > .env
HMAC_KEY=$(openssl rand -hex 32)
SERVER_IP=0.0.0.0
SERVER_PORT=5555
ENV_MODE=PRODUCTION
LOG_PATH=./Engine/logs/security.log
EOF
    echo "[+] .env generated with random HMAC key."
else
    echo "[!] .env already exists. Skipping."
fi

echo "[*] Setting file permissions..."
chmod +x *.sh
chmod 600 .env

echo "[+] Initialization complete."