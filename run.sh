#!/usr/bin/env bash
set -Eeuo pipefail

# Uso: ./run.sh path/al/config.json
[ "$#" -eq 1 ] || { echo "Uso: $0 path/al/config.json"; exit 1; }
CONFIG="$1"

# Ubicarse en la carpeta del script
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
cd "$SCRIPT_DIR"

# Verificar venv y activar
[ -f "venv/bin/activate" ] || { echo "No encontré venv/bin/activate. Corré primero ./setup.sh"; exit 1; }
# shellcheck disable=SC1091
. "venv/bin/activate"

# Python dentro del venv
PYTHON="$(command -v python3 || command -v python || true)"
[ -n "$PYTHON" ] || { echo "No se encontró Python en el venv."; exit 1; }

# Resolver ruta del config si viene relativa a donde está el script
if [ ! -f "$CONFIG" ]; then
  RESOLVED="$SCRIPT_DIR/$CONFIG"
  [ -f "$RESOLVED" ] && CONFIG="$RESOLVED"
fi
[ -f "$CONFIG" ] || { echo "No encontré el archivo de config: $CONFIG"; exit 1; }

echo "Usando config: $CONFIG"
exec "$PYTHON" -m src.genetics.genetics --config "$CONFIG"
