if (Get-Command python -ErrorAction SilentlyContinue) {
    $PYTHON = "python"
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $PYTHON = "python3"
} else {
    Write-Host "Python is not installed."
    exit 1
}

if (-not (Test-Path "venv")) {
    Write-Host "Virtual environment not found. Run setup.ps1 first."
    exit 1
}

.\venv\Scripts\Activate.ps1

& $PYTHON -m src.genetics.genetics