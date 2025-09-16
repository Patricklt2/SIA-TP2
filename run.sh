#!/usr/bin/env bash
set -Eeuo pipefail

usage() {
  cat <<'EOF'
Uso:
  ./run.sh <ruta/al/config.json>            # modo normal (GA tradicional)
  ./run.sh -t <ruta/al/config.json>         # modo tiled
  ./run.sh --tiled <ruta/al/config.json>

Notas:
- Requiere un venv en ./venv (Linux/macOS): venv/bin/activate
- En modo tiled mapea del JSON: image_path, tile_size, tile_threads, output_image,
  n_polygons, population_size, max_generations, elite_size, mutation_rate,
  crossover_rate, tile_preview (o show_live), tile_preview_interval (o plot_interval).
- Si el JSON tiene render_mode (o use_fast_render true/false) se exporta GEN_RENDER_MODE.
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
  # --- modo tiled: leer JSON y mapear a flags de src.genetics.tiled_ga ---
  # Producimos variables shell escapadas correctamente (usando shlex.quote desde Python)
  # para evitar problemas con espacios.
  eval "$(
    CFG="$CONFIG" "$PYTHON" - <<'PY'
import json, os, shlex
cfg_path = os.environ["CFG"]
try:
    with open(cfg_path, "r", encoding="utf-8") as f:
        c = json.load(f)
except Exception as e:
    raise SystemExit(f"ERROR leyendo JSON: {cfg_path}: {e}")

def q(v): return shlex.quote(str(v))

img   = c.get("image_path")
if not img:
    raise SystemExit("Config: falta 'image_path'")
tile  = int(c.get("tile_size", 64))
procs = int(c.get("tile_threads", 0))
out   = c.get("output_image", "out/tiled_best.png")
polys = int(c.get("n_polygons", 60))
pop   = int(c.get("population_size", 40))
gens  = int(c.get("max_generations", 400))
elite = int(c.get("elite_size", 6))
mut   = float(c.get("mutation_rate", 0.10))
cross = float(c.get("crossover_rate", 0.70))

preview = bool(c.get("tile_preview", c.get("show_live", False)))
pint    = int(c.get("tile_preview_interval", c.get("plot_interval", 8)))

print(f"IMG={q(img)}")
print(f"TILE={tile}")
print(f"PROCS={procs}")
print(f"OUTP={q(out)}")
print(f"POLYS={polys}")
print(f"POP={pop}")
print(f"GENS={gens}")
print(f"ELITE={elite}")
print(f"MUT={mut}")
print(f"CROSS={cross}")
print(f"PREVIEW={'true' if preview else 'false'}")
print(f"PINT={pint}")
PY
  )"

  # exportar GEN_RENDER_MODE si corresponde
  eval "$(export_render_mode || true)"

  # armar args
  ARGS=(
    -m src.genetics.tiled_ga
    --image "$IMG"
    --tile "$TILE"
    --out "$OUTP"
    --polys-per-tile "$POLYS"
    --pop "$POP"
    --gens "$GENS"
    --elite "$ELITE"
    --mut "$MUT"
    --cross "$CROSS"
  )
  if (( PROCS > 0 )); then
    ARGS+=( --processes "$PROCS" )
  fi
  if [[ "$PREVIEW" == "true" ]]; then
    ARGS+=( --preview --preview-interval "$PINT" )
  fi

  echo "[run] python ${ARGS[*]}"
  exec "$PYTHON" "${ARGS[@]}"

else
  # --- modo normal: exportar GEN_RENDER_MODE si corresponde y correr genetics ---
  eval "$(export_render_mode || true)"
  echo "[run] python -m src.genetics.genetics --config \"$CONFIG\""
  exec "$PYTHON" -m src.genetics.genetics --config "$CONFIG"
fi
