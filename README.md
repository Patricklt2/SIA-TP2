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
  "image_path": "data/target.jpg",
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

> **Obligatorios:** `image_path`, `n_polygons`.  
> El resto tiene *defaults* razonables si se omiten.

### 2) Correr

**Windows (PowerShell)**
```powershell
# usa siempre el venv y pasa el --config
.\run.ps1 -Config ".\config.json"
```

**macOS / Linux (bash)**
```bash
chmod +x run.sh
./run.sh ./config.json
```

## Salidas

- **Imagen final** en `output_image` (por defecto `out/best.png`).
- **CSV de métricas** (`metrics_csv`) con columnas:
  ```text
  generation, best_fitness, avg_fitness, worst_fitness, std_dev, mutation_rate,
  stagnation_counter, processes, population_size, n_polygons, fitness,
  selection, crossover, mutation, elapsed_sec
  ```

## Parámetros (con defaults y dominios)

- **Entradas**
  - `image_path` *(string, **obligatorio**)*: ruta a la imagen objetivo.
  - `metrics_csv` *(string, default: `"out/metrics.csv"`)*: CSV con métricas por generación (se crea la carpeta si no existe).
  - `output_image` *(string, default: `"out/best.png"`)*: dónde guardar la mejor solución final.

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
