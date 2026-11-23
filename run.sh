#!/usr/bin/env bash
# Ejecuta el bot. Crea un .env con tus credenciales primero (ver .env.example).
set -euo pipefail
cd "$(dirname "$0")"
pip install -r requirements.txt -q
python main.py "$@"
