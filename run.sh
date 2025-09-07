#!/bin/bash
set -e

# parse -w/--workers optional flag. Usage:
#   ./run.sh           -> normal single-process run
#   ./run.sh -w        -> worker mode, auto-detect CPU count
#   ./run.sh -w 4      -> worker mode with 4 workers
#!/bin/bash
set -e

# parse -w/--workers optional flag. Usage:
#   ./run.sh           -> normal single-process run
#   ./run.sh -w        -> worker mode, auto-detect CPU count
#   ./run.sh -w 4      -> worker mode with 4 workers

WORKERS_ARG=""
if [ "$1" = "-w" ] || [ "$1" = "--workers" ]; then
    if [ -n "$2" ] && [[ "$2" =~ ^[0-9]+$ ]]; then
        WORKERS_ARG="$2"
    else
        WORKERS_ARG="auto"
    fi
fi

if command -v python3 &>/dev/null; then
    PYTHON=python3
elif command -v python &>/dev/null; then
    PYTHON=python
else
    echo "Python is not installed."
    exit 1
fi

if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Run ./setup.sh first."
    exit 1
fi

source venv/bin/activate

if [ -n "$WORKERS_ARG" ]; then
    # determine worker count
    if [ "$WORKERS_ARG" = "auto" ]; then
        if command -v nproc &>/dev/null; then
            NCPU=$(nproc)
        else
            NCPU=$(getconf _NPROCESSORS_ONLN 2>/dev/null || echo 1)
        fi
        # leave one core for OS/coordination if possible
        if [ "$NCPU" -gt 1 ]; then
            WORKERS=$((NCPU - 1))
        else
            WORKERS=1
        fi
    else
        WORKERS=$WORKERS_ARG
    fi

    TILE_SIZE=${TILE_SIZE:-8}
    IMAGE=${IMAGE:-monalisa.webp}
    echo "Starting run_with_workers via main(): workers=$WORKERS, tile_size=$TILE_SIZE, image=$IMAGE"
    # export variables for main() to read
    export WORKERS=$WORKERS
    export TILE_SIZE=$TILE_SIZE
    export IMAGE=$IMAGE
    $PYTHON -m src.genetics.genetics
else
    $PYTHON -m src.genetics.genetics
fi