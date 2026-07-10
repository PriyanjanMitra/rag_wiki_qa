#!/bin/sh
set -e
export PATH="$HOME/.local/bin:$PATH"

echo "Removing deployments..."
kubectl delete -f k8s/ 2>/dev/null || true

echo "Stopping minikube..."
minikube stop

echo "All stopped."
