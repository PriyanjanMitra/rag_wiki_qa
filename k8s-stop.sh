#!/bin/sh
set -e

echo "Stopping minikube..."
minikube stop

echo ""
echo "To delete the cluster entirely, run: minikube delete"
echo "Note: PVC data (index, models) is preserved until you run minikube delete."
