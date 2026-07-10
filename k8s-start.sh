#!/bin/sh
set -e
export PATH="$HOME/.local/bin:$PATH"

if ! minikube status >/dev/null 2>&1; then
    echo "Starting minikube..."
    minikube start --driver=docker --cpus=4 --memory=6g
    minikube addons enable ingress
fi

echo "Building images..."
eval $(minikube -p minikube docker-env)
docker build -f Dockerfile.backend -t rag_wiki_qa_backend .
docker build -f Dockerfile.frontend -t rag_wiki_qa_frontend .

# Ensure HuggingFace model cache exists in minikube VM
if ! minikube ssh "ls /tmp/huggingface/hub/models--sentence-transformers--distiluse-base-multilingual-cased-v2/snapshots/" >/dev/null 2>&1; then
    echo "Copying HuggingFace model cache into minikube..."
    CACHE_DIR="$HOME/.cache/huggingface"
    if [ -d "$CACHE_DIR" ]; then
        cd "$CACHE_DIR" && tar czf /tmp/hf-cache.tar.gz . 2>/dev/null
        minikube cp /tmp/hf-cache.tar.gz /tmp/hf-cache.tar.gz
        minikube ssh "mkdir -p /tmp/huggingface && tar xzf /tmp/hf-cache.tar.gz -C /tmp/huggingface && rm -f /tmp/hf-cache.tar.gz"
        rm -f /tmp/hf-cache.tar.gz
    else
        echo "Warning: HuggingFace cache not found at $CACHE_DIR"
        echo "The first backend request will download the model (slow)."
    fi
fi

echo "Deploying..."
kubectl apply -f k8s/

echo ""
echo "Waiting for pods..."
kubectl wait --for=condition=Ready --timeout=300s pods --all

echo ""
echo "App is ready at: http://$(minikube ip)/"
