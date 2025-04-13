#!/bin/bash

kubectl apply -f manifests/namespace.yaml
kubectl apply -f manifests/db-deployment.yaml
kubectl apply -f manifests/ingestion-api-deployment.yaml
kubectl apply -f manifests/sensor-deployment.yaml
kubectl apply -f manifests/detection-deployment.yaml
kubectl apply -f manifests/dashboard-deployment.yaml
kubectl apply -f manifests/ingress.yaml

# A FAIRE AVANT (1 SEULE FOIS) : chmod +x scripts/deploy.sh
# ensuite : ./scripts/deploy.sh
