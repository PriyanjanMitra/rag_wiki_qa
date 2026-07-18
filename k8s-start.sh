#!/bin/sh
set -e

BASE_URL="https://raw.githubusercontent.com/PriyanjanMitra/rag_wiki_qa/master/k8s"

kubectl() { minikube kubectl -- "$@"; }

if ! minikube status >/dev/null 2>&1; then
    echo "Starting minikube..."
    minikube start --driver=docker --cpus=4 --memory=6g
    minikube addons enable ingress
fi

echo ""
echo "Select RAG version:"
echo "  1) Manual RAG"
echo "  2) DSPy RAG"
printf "Enter choice [1]: "
read -r choice
case "${choice:-1}" in
  2) TAG="feature-dspy-rag" ;;
  *) TAG="latest" ;;
esac
echo "Using image tag: $TAG"
echo ""

echo "Deploying from $BASE_URL ..."
kubectl apply -f "$BASE_URL/backend-deploy.yaml"
kubectl apply -f "$BASE_URL/frontend-deploy.yaml"
kubectl apply -f "$BASE_URL/ollama-deploy.yaml"

echo ""
echo "Applying ingress..."
kubectl apply -f "$BASE_URL/ingress.yaml" 2>/dev/null || \
  echo "  (ingress will be applied once the webhook is available)"

echo ""
echo "Overriding image tag to $TAG ..."
kubectl set image deployment/backend \
  "backend=ghcr.io/priyanjanmitra/rag_wiki_qa-backend:$TAG"
kubectl set image deployment/frontend \
  "frontend=ghcr.io/priyanjanmitra/rag_wiki_qa-frontend:$TAG"

echo ""
echo "Waiting for core app pods (first run downloads models)..."
echo "  Use Ctrl+C to skip — pods continue in background."
kubectl wait --for=condition=Ready --timeout=300s pod -l app=backend 2>/dev/null || \
  echo "  Backend not ready yet — check: minikube kubectl -- get pods"
kubectl wait --for=condition=Ready --timeout=60s pod -l app=frontend 2>/dev/null || \
  echo "  Frontend not ready yet"
kubectl wait --for=condition=Ready --timeout=600s pod -l app=ollama 2>/dev/null || \
  echo "  Ollama not ready yet — check: minikube kubectl -- get pods"

echo ""
echo "======================================"
echo "App is ready at: http://$(minikube ip)/"
echo "======================================"
