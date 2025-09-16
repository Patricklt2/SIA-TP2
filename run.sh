#!/usr/bin/env bash
set -Eeuo pipefail

usage() {
  cat <<'EOF'
Uso:
  ./run.sh <ruta/al/config.json>        # modo normal (GA tradicional)
  ./run.sh -t <ruta/al/config.json>        # modo tiled
  ./run.sh --tiled <ruta/al/config.json>

Notas:
- Requiere un venv en ./venv (Linux/macOS): venv/bin/activate
- Si el JSON tiene render_mode se exporta la variable de entorno GEN_RENDER_MODE.
EOF
}

# --- ubicar carpeta del script ---
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
cd "$SCRIPT_DIR"

# --- parseo de args: [-t|--tiled] CONFIG ---
TILED=false
CONFIG=""

while (("$#")); do
  case "$1" in
    -t|--tiled) TILED=true; shift ;;
    -h|--help) usage; exit 0 ;;
    -*)
      echo "Argumento no reconocido: $1" >&2
      usage; exit 1 ;;
    *)
      if [[ -z "$CONFIG" ]]; then CONFIG="$1"; shift; else break; fi ;;
  esac
done

[[ -n "$CONFIG" ]] || { usage; exit 1; }

# --- venv ---
[[ -f "venv/bin/activate" ]] || { echo "No encontré venv/bin/activate. Corré primero ./setup.sh"; exit 1; }
# shellcheck disable=SC1091
. "venv/bin/activate"

# --- python dentro del venv ---
PYTHON="$(command -v python3 || command -v python || true)"
[[ -n "$PYTHON" ]] || { echo "No se encontró python en el venv."; exit 1; }
echo "[run] Python en uso: $("$PYTHON" -c 'import sys; print(sys.executable)')"

# --- resolver ruta del config ---
if [[ ! -f "$CONFIG" ]]; then
  RESOLVED="$SCRIPT_DIR/$CONFIG"
  [[ -f "$RESOLVED" ]] && CONFIG="$RESOLVED"
fi
[[ -f "$CONFIG" ]] || { echo "No encontré el archivo de config: $CONFIG"; usage; exit 1; }
echo "[run] Usando config: $CONFIG"

# --- función auxiliar: exportar GEN_RENDER_MODE según el JSON ---
export_render_mode() {
  CFG="$CONFIG" "$PYTHON" - <<'PY'
import json, os
cfg_path = os.environ["CFG"]
try:
    with open(cfg_path, "r", encoding="utf-8") as f:
        c = json.load(f)
except Exception as e:
    raise SystemExit(f"ERROR leyendo JSON: {cfg_path}: {e}")

render = c.get("render_mode")
if render is None and ("use_fast_render" in c):
    render = "fast" if bool(c.get("use_fast_render")) else "compat"

if render:
    # imprime línea shell para exportar
    import shlex
    print("export GEN_RENDER_MODE=" + shlex.quote(str(render)))
PY
}


if $TILED; then
  # --- modo tiled: exportar GEN_RENDER_MODE y correr tiled_ga ---
  eval "$(export_render_mode || true)"
  echo "[run] python -m src.genetics.tiled_ga --config \"$CONFIG\""
  exec "$PYTHON" -m src.genetics.tiled_ga --config "$CONFIG"

else
  # --- modo normal: exportar GEN_RENDER_MODE y correr genetics ---
  eval "$(export_render_mode || true)"
  echo "[run] python -m src.genetics.genetics --config \"$CONFIG\""
  exec "$PYTHON" -m src.genetics.genetics --config "$CONFIG"
fi