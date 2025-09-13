if (-not (Test-Path "venv")) {
    Write-Host "Virtual environment not found. Run setup.ps1 first."
    exit 1
}

# Activar venv
. .\venv\Scripts\Activate.ps1

# Python del venv
$PYTHON = Join-Path $env:VIRTUAL_ENV "Scripts\python.exe"
Write-Host "Python executable in use: " (& $PYTHON -c "import sys; print(sys.executable)")

# ------------------------------
# NUEVO: aceptar parámetro -Config
# ------------------------------
param(
    [string]$Config = "example_config.json"
)

& $PYTHON -m src.genetics.genetics2 --config $Config
