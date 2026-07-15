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
echo "Deploying Langfuse tracing stack..."
kubectl apply -f k8s/langfuse-secret.yaml 2>/dev/null || echo "  (langfuse secret already exists)"
kubectl apply -f k8s/langfuse-db.yaml
kubectl apply -f k8s/langfuse-zookeeper.yaml
kubectl apply -f k8s/langfuse-clickhouse.yaml
kubectl apply -f k8s/langfuse.yaml

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
echo ""
echo "Langfuse: deploy + port-forward to inject API keys"
echo "  1. minikube kubectl -- port-forward svc/langfuse 3000:3000"
echo "  2. Open http://localhost:3000 → create project → get API keys"
echo "  3. Run the command it prints below"
echo ""
echo "To backfill old traces, port-forward is enough — tracing starts"
echo "as soon as keys are set:"
echo "  minikube kubectl -- set env deployment/backend \\"
echo "    LANGFUSE_SECRET_KEY=sk-lf-... \\"
echo "    LANGFUSE_PUBLIC_KEY=pk-lf-... \\"
echo "    LANGFUSE_HOST=http://langfuse:3000"
echo "======================================"
