#!/bin/sh
set -e

if [ ! -f /app/index/index.faiss ]; then
    echo "Index not found. Building from PDFs (first run only)..."
    if [ -n "$HF_TOKEN" ]; then
        echo "Using HF_TOKEN from environment"
    fi
    python pipeline/build_index.py || echo "Index build failed (will retry on next restart)"
fi

exec python -m uvicorn route.api:app --host 0.0.0.0 --port 8000
