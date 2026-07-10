#!/bin/sh
if ! docker image inspect rag_wiki_qa >/dev/null 2>&1; then
    echo "Building image (one-time)..."
    docker build -t rag_wiki_qa .
fi
docker kill $(docker ps -q) 2>/dev/null
docker run -p 8000:8000 -p 5173:5173 \
  -v ollama_data:/root/.ollama \
  -v "$(pwd)"/run.py:/app/run.py \
  -v "$(pwd)"/frontend/vite.config.ts:/app/frontend/vite.config.ts \
  rag_wiki_qa
