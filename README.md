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

## Salidas

- **Preview en vivo** de la mejor solución (si `show_plot: true`).
- **Imagen final** guardada en `output_image` (si lo definís en el JSON).
- Log por consola con `Best fitness` por generación.

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

