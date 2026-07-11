#!/bin/sh
set -e
kubectl() { minikube kubectl -- "$@"; }

echo "Removing deployments..."
kubectl delete -f k8s/ 2>/dev/null || true

echo "Stopping minikube..."
minikube stop

echo "All stopped."
