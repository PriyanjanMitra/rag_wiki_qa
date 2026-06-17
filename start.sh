#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

python main.py &
BACKEND=$!

cd frontend
npm run dev &
FRONTEND=$!

trap 'kill $BACKEND $FRONTEND 2>/dev/null' EXIT

wait
