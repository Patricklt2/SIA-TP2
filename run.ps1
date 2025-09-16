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
  # Read JSON to optionally set render mode env; then call tiled_ga with --config
  try {
    $cfg = Get-Content -Raw -Path $Config | ConvertFrom-Json
    $render = if ($cfg.render_mode) { [string]$cfg.render_mode } elseif ($cfg.use_fast_render -ne $null) { if ([bool]$cfg.use_fast_render) { 'fast' } else { 'compat' } } else { $null }
    if ($render) { $env:GEN_RENDER_MODE = $render }
  } catch {
    Write-Error "Failed to read JSON config: $Config"
    exit 1
  }

  & $PYTHON -m src.genetics.tiled_ga --config $Config
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
