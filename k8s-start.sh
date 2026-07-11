#!/bin/sh
set -e
kubectl() { minikube kubectl -- "$@"; }

if ! minikube status >/dev/null 2>&1; then
    echo "Starting minikube..."
    minikube start --driver=docker --cpus=4 --memory=6g
    minikube addons enable ingress
fi

echo "Deploying from ghcr.io/priyanjanmitra..."
kubectl apply -f k8s/

echo ""
echo "Waiting for pods (first run downloads models, may take a few minutes)..."
kubectl wait --for=condition=Ready --timeout=600s pods --all

echo ""
echo "App is ready at: http://$(minikube ip)/"
