param(
  [string]$Config = "src/configs/config.json"
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
  if (Test-Path $Resolved) { $Config = $Resolved }
}
if (-not (Test-Path $Config)) {
  Write-Error "Config file not found: $Config"
  exit 1
}
Write-Host "Using config: $Config"

# ejecutar genetics2 con --config
& $PYTHON -m src.genetics.genetics2 --config $Config
