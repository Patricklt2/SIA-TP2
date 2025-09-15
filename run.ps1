param(
  [Parameter(Mandatory = $true)]
  [ValidateNotNullOrEmpty()]
  [string]$Config,
  [switch]$Tiled
)

# ----- paths -----
$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvPath   = Join-Path $ScriptRoot "venv"

if (-not (Test-Path $VenvPath)) {
  Write-Host "Virtual environment not found. Run setup.ps1 first."
  exit 1
}

# activar venv
. (Join-Path $VenvPath "Scripts\Activate.ps1")

# python del venv
$PYTHON = Join-Path $env:VIRTUAL_ENV "Scripts\python.exe"
Write-Host "Python executable in use: " (& $PYTHON -c "import sys; print(sys.executable)")

# resolver ruta del config por si llaman desde otro cwd
if (-not (Test-Path $Config)) {
  $Resolved = Join-Path $ScriptRoot $Config
  if (Test-Path $Resolved) {
    $Config = $Resolved
  }
}

if (-not (Test-Path $Config)) {
  Write-Error "Config file not found: $Config
Uso: .\run.ps1 -Config .\src\configs\config.json"
  exit 1
}

Write-Host "Using config: $Config"

if ($Tiled) {
  # Read JSON and map to tiled_ga args
  try {
    $cfg = Get-Content -Raw -Path $Config | ConvertFrom-Json
  } catch {
    Write-Error "Failed to read JSON config: $Config"
    exit 1
  }

  $img    = $cfg.image_path
  if (-not $img) { Write-Error "Config is missing image_path"; exit 1 }
  $tile   = if ($cfg.tile_size) { [int]$cfg.tile_size } else { 64 }
  $procs  = if ($cfg.tile_threads) { [int]$cfg.tile_threads } else { 0 }
  $out    = if ($cfg.output_image) { [string]$cfg.output_image } else { "out/tiled_best.png" }
  $polys  = if ($cfg.n_polygons) { [int]$cfg.n_polygons } else { 60 }
  $pop    = if ($cfg.population_size) { [int]$cfg.population_size } else { 40 }
  $gens   = if ($cfg.max_generations) { [int]$cfg.max_generations } else { 400 }
  $elite  = if ($cfg.elite_size) { [int]$cfg.elite_size } else { 6 }
  $mut    = if ($cfg.mutation_rate) { [double]$cfg.mutation_rate } else { 0.10 }
  $cross  = if ($cfg.crossover_rate) { [double]$cfg.crossover_rate } else { 0.70 }
  $preview= if ($cfg.tile_preview) { [bool]$cfg.tile_preview } elseif ($cfg.show_live) { [bool]$cfg.show_live } else { $false }
  $pint   = if ($cfg.tile_preview_interval) { [int]$cfg.tile_preview_interval } elseif ($cfg.plot_interval) { [int]$cfg.plot_interval } else { 8 }

  # Optional extras
  $stop   = if ($cfg.stop_fitness) { [double]$cfg.stop_fitness } else { $null }
  $epochs = if ($cfg.epochs) { [int]$cfg.epochs } else { $null }
  $pad    = if ($cfg.pad) { [int]$cfg.pad } else { $null }
  $render = if ($cfg.render_mode) { [string]$cfg.render_mode } elseif ($cfg.use_fast_render -ne $null) { if ([bool]$cfg.use_fast_render) { 'fast' } else { 'compat' } } else { $null }

  $argsList = @(
    '-m','src.genetics.tiled_ga',
    '--image', $img,
    '--tile',  $tile,
    '--out',   $out,
    '--polys-per-tile', $polys,
    '--pop',   $pop,
    '--gens',  $gens,
    '--elite', $elite,
    '--mut',   $mut,
    '--cross', $cross
  )
  if ($procs -gt 0) { $argsList += @('--processes', $procs) }
  if ($preview) { $argsList += @('--preview', '--preview-interval', $pint) }

  if ($render) { $env:GEN_RENDER_MODE = $render }
  & $PYTHON @argsList
} else {
  # ejecutar GA tradicional con --config
  # Lee config para mapear render_mode -> GEN_RENDER_MODE también en modo no tiled
  try {
    $cfg2 = Get-Content -Raw -Path $Config | ConvertFrom-Json
    $render2 = if ($cfg2.render_mode) { [string]$cfg2.render_mode } elseif ($cfg2.use_fast_render -ne $null) { if ([bool]$cfg2.use_fast_render) { 'fast' } else { 'compat' } } else { $null }
    if ($render2) { $env:GEN_RENDER_MODE = $render2 }
  } catch {}
  & $PYTHON -m src.genetics.genetics --config $Config
}
