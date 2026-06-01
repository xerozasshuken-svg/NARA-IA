#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [ -d "venv" ] && [ ! -x "./venv/bin/python" ]; then
  echo "El entorno virtual copiado no es usable en este equipo. Recreando venv..."
  rm -rf venv
fi

if [ -x "./venv/bin/python" ] && ! ./venv/bin/python --version >/dev/null 2>&1; then
  echo "El entorno virtual copiado no es usable en este equipo. Recreando venv..."
  rm -rf venv
fi

if [ ! -d "venv" ]; then
  python3 -m venv venv
fi

./venv/bin/python -m pip install --upgrade pip
./venv/bin/python -m pip install -r requirements.txt

echo "Entorno listo. Ejecuta: bash start.sh"
