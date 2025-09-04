#!/bin/bash
set -e

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

$PYTHON -m src.main