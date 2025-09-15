# SIA–TP2 · Aproximación de imágenes con Algoritmos Genéticos (polígonos)

Este proyecto aproxima una imagen objetivo dibujando **triángulos** mediante un **Algoritmo Genético** (AG).  

---

## Requisitos

Dependencias principales:
- `numpy`
- `Pillow` (PIL)
- `matplotlib`

> Si usás los scripts provistos, se instalarán automáticamente.

---


## Instalación / Setup

### Windows (PowerShell)
Desde la raíz del repo:
```powershell
.\setup.ps1
```
Esto crea el **venv** y instala dependencias.

### macOS / Linux (bash)
Desde la raíz del repo:
```bash
./setup.sh
# si no tenés permisos:
# chmod +x setup.sh && ./setup.sh
```
Esto crea el **venv** y instala dependencias.

---

## Ejecución

### 1) Preparar un JSON de configuración
Ejemplo mínimo (`config.json`):
```json
{
  "image_path": "entrada.jpg",
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
  "increased_mutation_rate": 0.24,

  "output_image": "out/best.png",
  "show_plot": true
}
```

> **Obligatorios:** `image_path`, `n_polygons`.  
> El resto tiene *defaults* razonables si se omiten.

### 2) Correr (modo normal)

**Windows (PowerShell)**
```powershell
# usa siempre el venv y pasa el --config
.\run2.ps1 -Config ".\configs\config.json"
```

**macOS / Linux (bash)**
```bash
./run2.sh -c ./configs/config.json
# si da permisos:
# chmod +x run.sh && ./run.sh -c ./configs/mi_config.json
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

- **Preview en vivo** de la mejor solución (si `show_plot: true`).
- **Imagen final** guardada en `output_image` (si lo definís en el JSON).
- Log por consola con `Best fitness` por generación.

En modo tiled:
- Secuencial: preview cada `plot_interval` generaciones.
- Paralelo: preview cuando se completan tiles (cada `tile_preview_interval`).

---

## Parámetros soportados (resumen)

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
