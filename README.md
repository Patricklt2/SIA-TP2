# SIA–TP2 · Aproximación de imágenes con Algoritmos Genéticos (polígonos)

Este proyecto aproxima una imagen objetivo dibujando **triángulos** mediante un **Algoritmo Genético** (AG).  

## Prerrequisitos

- **Python 3.8+**
- **Windows (PowerShell):** no requiere nada extra (el script `setup.ps1` crea y activa el `venv`).
- **Linux / WSL (Ubuntu/Debian):** módulo `venv` para Python
  ```bash
  sudo apt update && sudo apt install -y python3-venv
  ```
- **macOS (Homebrew):**
  ```bash
  brew install python
  ```

## Requisitos

Dependencias principales:
- `numpy`
- `Pillow` (PIL)
- `matplotlib`
- `scikit-image`

> Si usás los scripts provistos, se instalarán automáticamente.


## Instalación / Setup

### Windows (PowerShell)
Desde la raíz del repo:
```powershell
.\setup.ps1
```
Esto crea el **venv** y instala dependencias.

### Linux / macOS (bash)
Desde la raíz del repo:
```bash
chmod +x setup.sh
./setup.sh
```
Esto crea el **venv** y instala dependencias.

---

## Ejecución

### 1) Preparar un JSON de configuración
Ejemplo mínimo (`config.json`):
```json
{
  "image_path": "target.jpg",
  "n_polygons": 120,
  "n_vertices": 3,

  "population_size": 120,
  "mutation_rate": 0.12,
  "crossover_rate": 0.7,
  "elite_size": 8,
  "max_generations": 5000,
  "stop_fitness": 0.92,

  "fitness": "mse",
  "mutation": "multi_gene",
  "selection": "tournament",
  "replacement": "traditional",
  "crossover": "two_point",

  "stagnation_threshold": 30,
  "original_mutation_rate": 0.12,
  "increased_mutation_rate": 0.48,

  "show_live": true,
  "plot_interval": 10,

  "metrics_csv": "out/metrics.csv",
  "output_image": "out/best.png"
}
```

> **Obligatorio:** `image_path`.  
> El resto tiene *defaults* razonables si se omiten.

### 2) Correr

**Windows (PowerShell)**
```powershell
.\run.ps1 -Config ".\config.json"
```

**macOS / Linux (bash)**
```bash
chmod +x run.sh
./run.sh ./config.json
```

---

## Modo por tiles (tiled_ga)

Podés dividir la imagen en una grilla de tiles y ejecutar un AG por tile. Esto permite paralelizar y mejorar detalle local.

Ejemplos con los runners:
- PowerShell (Windows): `./run.ps1 -Config .\config.json -Tiled`
- Bash/WSL: `./run2.sh --config ./config.json --tiled`

Claves de `config.json` que usan los runners en modo tiled:
- `tile_size`: tamaño del tile en px (ej. 64, 96, 128)
- `tile_threads`: 0 = secuencial (preview por generación); >0 = procesos en paralelo
- `n_polygons`, `population_size`, `max_generations`, `elite_size`, `mutation_rate`, `crossover_rate` (por‑tile)
- `show_live` o `tile_preview`: muestra la ventana de preview
- `plot_interval` o `tile_preview_interval`: frecuencia de actualización del preview
- `output_image`: ruta del PNG compuesto final

Notas útiles:
- Secuencial (`tile_threads: 0`) muestra la imagen evolucionando cada `plot_interval` generaciones.
- Sin tiles, elevar n-polygons.
Llamada directa (sin runner):
```
python -m src.genetics.tiled_ga \
  --image entrada.jpg --tile 96 --processes 4 \
  --polys-per-tile 60 --pop 40 --gens 400 \
  --pad 6 --stop 2.0 --epochs 3 --preview
```

---

## Modos de render (rápido vs compatibilidad)

El render de cada individuo puede hacerse de dos formas equivalentes visualmente:
- `fast` (default): dibuja todos los polígonos sobre un único lienzo RGBA (mucho más rápido).
- `compat`: ruta “clásica”, compone cada polígono como una capa temporal con `alpha_composite`.

Seleccionás el modo desde `config.json` y los runners lo aplican automáticamente:
- `"render_mode": "fast"` | `"compat"`
- (legacy) `"use_fast_render": true|false`

No hace falta setear variables de entorno manualmente si usás los runners.

---

## Salidas

- **Imagen final** en `output_image` (por defecto `out/best.png`).
- **CSV de métricas** (`metrics_csv`) con columnas:
  ```text
  generation, best_fitness, avg_fitness, worst_fitness, std_dev, mutation_rate,
  stagnation_counter, processes, population_size, n_polygons, fitness,
  selection, crossover, mutation, elapsed_sec
  ```

En modo tiled:
- Secuencial: preview cada `plot_interval` generaciones.
- Paralelo: preview cuando se completan tiles (cada `tile_preview_interval`).

---
## Parámetros (con defaults y dominios)

- **Entradas**
  - `image_path` *(string, **obligatorio**)*: ruta a la imagen objetivo.
  - `metrics_csv` *(string, default: `"out/metrics.csv"`)*: CSV con métricas por generación (se crea la carpeta si no existe).
  - `output_image` *(string, default: `"out/best.png"`)*: dónde guardar la mejor solución final.

- **Imagen y cromosoma**
  - `image_path`: ruta a la imagen objetivo.
  - `n_polygons`: cantidad de triángulos por individuo.
- **AG**
  - `population_size`, `mutation_rate`, `crossover_rate`, `elite_size`
  - `max_generations`, `stop_fitness`
- **Operadores**
  - `fitness`: `mse` | `ssim` | `mixed` | `mixed_mse_ssim` | `deltaE`
  - `selection`: `elite` | `tournament` | `roulette` | `universal` | `boltzmann` | `ranking`
  - `crossover`: `single_point` | `two_point` | `uniform`
  - `mutation`: `single_gene` | `multi_gene` | `seed_guided`
  - `replacement`: `traditional` 
- **Anti‑estancamiento**
  - `stagnation_threshold`, `increased_mutation_rate`
- **Visualización / salida**
  - `show_plot` (true/false), `output_image`
  - tiled: `tile_size`, `tile_threads`, `tile_preview`/`show_live`, `tile_preview_interval`/`plot_interval`
  - render: `render_mode`: `fast` | `compat` (o `use_fast_render`)
- **Representación**
  - `n_polygons` *(int, default: 100)*: cantidad de polígonos por individuo.
  - `n_vertices` *(int, default: 3)*: vértices por polígono.

- **AG – hiperparámetros**
  - `population_size` *(int, default: 100)*
  - `mutation_rate` *(float, default: 0.1)*
  - `crossover_rate` *(float, default: 0.7)*
  - `elite_size` *(int, default: 7)*
  - `max_generations` *(int, default: 10000)*
  - `stop_fitness` *(float, default: 0.9)*: criterio de corte por fitness.

- **Operadores (valores posibles)**
  - `fitness`: `"mse"`, `"ssim"`, `"mixed"`, `"mixed_mse_ssim"`, `"deltaE"`
  - `mutation`: `"single_gene"`, `"multi_gene"`, `"seed_guided"`, `"non_uniform_multigen"`, `"doomsday"`
  - `selection`: `"elite"`, `"tournament"`, `"roulette"`, `"universal"`, `"boltzmann"`, `"ranking"`
  - `replacement`: `"traditional"`, `"young_bias"`
  - `crossover`: `"single_point"`, `"two_point"`, `"uniform"`, `"anular"`, `"artistic"`

- **Anti-estancamiento**
  - `stagnation_threshold` *(int, default: 20)*: generaciones sin mejora para disparar acción.
  - `original_mutation_rate` *(float, default: `mutation_rate`)*: tasa normal (se restaura al mejorar).
  - `increased_mutation_rate` *(float, default: `mutation_rate * 4.0`)*: tasa al detectar estancamiento.

- **Visualización**
  - `show_live` *(bool, default: `false`)*: actualiza ventana con la mejor imagen.
  - `plot_interval` *(int, default: `10`)*: cada cuántas generaciones refrescar el plot.

## Visualización rápida del avance (best_fitness)

El script `plot_fitness.py` grafica `best_fitness` vs `generation` y etiqueta cada curva con el **nombre del CSV**.

### Windows (PowerShell)
```powershell
# activar venv
.\venv\Scripts\Activate.ps1

# graficar dos runs (rutas explícitas para evitar expansiones raras)
python .\plot_fitness.py .\out\metrics.csv .\out\metrics2.csv
```

### Linux / macOS (bash)
```bash
# activar venv
source venv/bin/activate

# graficar dos runs
python plot_fitness.py out/metrics.csv out/metrics2.csv
```
