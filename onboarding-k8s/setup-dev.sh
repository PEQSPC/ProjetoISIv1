#!/bin/bash

# ==========================================
# Local Dev Onboarding Script
# ==========================================
CLUSTER_NAME="isi-dev-cluster"
IMAGE_REGISTRY="peqspc"
API_IMAGE="manager-api:latest"
SIM_IMAGE="mqtt-simulator:latest"

echo "Starting Onboarding for ISIv1 SaaS..."

# 1. Check Prerequisites
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed. Aborting." >&2; exit 1; }
command -v kind >/dev/null 2>&1 || { echo "❌ Kind is required but not installed. Aborting." >&2; exit 1; }
command -v kubectl >/dev/null 2>&1 || { echo "❌ Kubectl is required but not installed. Aborting." >&2; exit 1; }

# 2. Cleanup Old Cluster (Optional)
if kind get clusters | grep -q "^$CLUSTER_NAME$"; then
    read -p "Cluster '$CLUSTER_NAME' already exists. Delete and recreate? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kind delete cluster --name $CLUSTER_NAME
    else
        echo "Example: Keeping existing cluster..."
    fi
fi

# 3. Create Kind Cluster
if ! kind get clusters | grep -q "^$CLUSTER_NAME$"; then
    echo "Creating Kind Cluster..."
    kind create cluster --name $CLUSTER_NAME
fi

# 4. Build Docker Images (Local Build)
 echo "Building Manager API Image..."
 docker build -t $IMAGE_REGISTRY/$API_IMAGE ./app

 echo "Building IoT Simulator Image..."
 docker build -t $IMAGE_REGISTRY/$SIM_IMAGE ./simulator

# 5. Load Images into Kind (No need to push to DockerHub for local dev)
echo "Loading images into Kind nodes..."
kind load docker-image $IMAGE_REGISTRY/$API_IMAGE --name $CLUSTER_NAME
kind load docker-image $IMAGE_REGISTRY/$SIM_IMAGE --name $CLUSTER_NAME

# 6. Apply Infrastructure
echo "Applying Kubernetes Manifests..."

# Create Namespace
kubectl --context kind-$CLUSTER_NAME create namespace iot-sims --dry-run=client -o yaml | kubectl apply -f -

# Apply RBAC (Crucial for API to create Pods)
kubectl --context kind-$CLUSTER_NAME apply -f k8s/rbac-config.yaml

# Apply API Deployment & Service
kubectl --context kind-$CLUSTER_NAME apply -f k8s/api-deployment.yaml
kubectl --context kind-$CLUSTER_NAME apply -f k8s/api-service.yaml
# 7. Install ArgoCD (Optional - for Production Parity)
echo "Installing ArgoCD (for later use)..."
kubectl --context kind-$CLUSTER_NAME create namespace argocd --dry-run=client -o yaml | kubectl apply -f -
kubectl --context kind-$CLUSTER_NAME apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# 8. Status & Instructions
echo ""
echo "========================================="
echo "           Setup Complete!"
echo "========================================="
echo "To access your API from Windows:"
echo "  kubectl port-forward svc/manager-api-service 5000:80 -n iot-sims"
echo ""
echo "Then send a POST request to: http://localhost:5000/create-sim"