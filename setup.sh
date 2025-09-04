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

if command -v pip3 &>/dev/null; then
    PIP=pip3
elif command -v pip &>/dev/null; then
    PIP=pip
else
    echo "pip is not installed."
    exit 1
fi

if [ ! -d "venv" ]; then
    echo "Creating venv"
    $PYTHON -m venv venv
fi

source venv/bin/activate

if [ -f "requirements.txt" ]; then
    echo "Installing dependencies..."
    $PIP install -r requirements.txt
else
    echo "No requirements.txt found."
fi
