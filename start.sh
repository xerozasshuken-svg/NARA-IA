#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [ -x "./venv/bin/python" ]; then
  ./venv/bin/python run.py
else
  echo "No hay venv local usable. Ejecuta: bash setup.sh"
  python3 run.py
fi
