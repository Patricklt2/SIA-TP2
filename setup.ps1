$ErrorActionPreference = "Stop"

if (Get-Command python -ErrorAction SilentlyContinue) {
    $PYTHON = "python"
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $PYTHON = "python3"
} else {
    Write-Host "Python is not installed."
    exit 1
}

if (Get-Command pip -ErrorAction SilentlyContinue) {
    $PIP = "pip"
} elseif (Get-Command pip3 -ErrorAction SilentlyContinue) {
    $PIP = "pip3"
} else {
    Write-Host "pip is not installed."
    exit 1
}

if (-not (Test-Path "venv")) {
    Write-Host "Creating venv"
    & $PYTHON -m venv venv
}

.\venv\Scripts\Activate.ps1

if (Test-Path "requirements.txt") {
    Write-Host "Installing dependencies..."
    & $PIP install -r requirements.txt
} else {
    Write-Host "No requirements.txt found."
}

Write-Host "Setup completed successfully!"