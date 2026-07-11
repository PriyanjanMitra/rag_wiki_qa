#!/bin/sh
set -e

if [ ! -f /app/index/index.faiss ]; then
    echo "Index not found. Building from PDFs (first run only)..."
    python pipeline/build_index.py
    echo "Index built."
fi

exec python -m uvicorn route.api:app --host 0.0.0.0 --port 8000
