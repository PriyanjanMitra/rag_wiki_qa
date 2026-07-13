#!/bin/sh
set -e
kubectl() { minikube kubectl -- "$@"; }

if ! minikube status >/dev/null 2>&1; then
    echo "Starting minikube..."
    minikube start --driver=docker --cpus=4 --memory=6g
    minikube addons enable ingress
fi

echo "Deploying from ghcr.io/priyanjanmitra..."
kubectl apply -f k8s/backend-deploy.yaml
kubectl apply -f k8s/frontend-deploy.yaml
kubectl apply -f k8s/ollama-deploy.yaml

echo ""
echo "Waiting for ingress controller to be ready..."
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=300s 2>/dev/null || \
  echo "  (continuing without ingress controller ready)"

echo "Applying ingress..."
kubectl apply -f k8s/ingress.yaml 2>/dev/null || \
  echo "  (ingress will be applied once the webhook is available)"

echo ""
echo "Waiting for pods (first run downloads models, may take a few minutes)..."
echo "  Use Ctrl+C to skip wait — pods will continue in background."
kubectl wait --for=condition=Ready --timeout=900s pods --all 2>/dev/null || \
  echo "  Not all pods ready yet — check with: minikube kubectl -- get pods"

echo ""
echo "App is ready at: http://$(minikube ip)/"
