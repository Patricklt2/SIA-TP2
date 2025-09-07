if (-not (Test-Path "venv")) {
    Write-Host "Virtual environment not found. Run setup.ps1 first."
    exit 1
}

# Activate the virtual environment
. .\venv\Scripts\Activate.ps1

# Always use the venv’s Python
$PYTHON = Join-Path $env:VIRTUAL_ENV "Scripts\python.exe"

# Debug: confirm which python is being used
Write-Host "Python executable in use: " (& $PYTHON -c "import sys; print(sys.executable)")
Write-Host "VIRTUAL_ENV: $env:VIRTUAL_ENV"

$WORKERS = $null

if ($args.Count -gt 0 -and ($args[0] -eq "-w" -or $args[0] -eq "--workers")) {
    if ($args.Count -gt 1 -and $args[1] -match '^\d+$') {
        $WORKERS = [int]$args[1]
    } else {
        try {
            $NCPU = (Get-CimInstance Win32_Processor | Measure-Object -Property NumberOfLogicalProcessors -Sum).Sum
        } catch {
            $NCPU = 1
        }

        if ($NCPU -gt 1) {
            $WORKERS = $NCPU - 1
        } else {
            $WORKERS = 1
        }
    }

    if (-not $env:TILE_SIZE) { $env:TILE_SIZE = 8 }
    if (-not $env:IMAGE) { $env:IMAGE = "monalisa.webp" }

    Write-Host "Starting run_with_workers via main(): workers=$WORKERS, tile_size=$env:TILE_SIZE, image=$env:IMAGE"
    $env:WORKERS = $WORKERS
    & $PYTHON -m src.genetics.genetics
} else {
    & $PYTHON -m src.genetics.genetics
}
