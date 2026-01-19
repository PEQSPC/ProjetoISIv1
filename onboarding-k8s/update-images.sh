#!/bin/bash
# ==========================================
# Update Images Script - Rebuild and redeploy
# Usage: ./update-images.sh [api|frontend|simulator|all]
# ==========================================
set -e

CLUSTER_NAME="isi-dev-cluster"
IMAGE_REGISTRY="peqspc"
API_IMAGE="manager-api:latest"
SIM_IMAGE="mqtt-simulator:latest"
FRONTEND_IMAGE="iot-simulator-frontend:latest"
DOMAIN="iot-simulator.local"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Check if cluster exists
if ! kind get clusters | grep -q "^$CLUSTER_NAME$"; then
    echo "❌ Cluster '$CLUSTER_NAME' not found. Run setup-dev.sh first."
    exit 1
fi

# Function to rebuild and reload API
update_api() {
    echo "📦 Rebuilding Manager API..."
    docker build -t $IMAGE_REGISTRY/$API_IMAGE "$PROJECT_DIR/iot-simulator-api"

    echo "📤 Loading API image into Kind..."
    kind load docker-image $IMAGE_REGISTRY/$API_IMAGE --name $CLUSTER_NAME

    echo "🔄 Restarting API deployment..."
    kubectl rollout restart deployment/manager-api -n iot-sims
    kubectl rollout status deployment/manager-api -n iot-sims --timeout=120s

    echo "✅ API updated!"
}

# Function to rebuild and reload Frontend
update_frontend() {
    echo "📦 Rebuilding Frontend..."
    docker build \
        --build-arg VITE_API_URL="https://$DOMAIN/api" \
        -t $IMAGE_REGISTRY/$FRONTEND_IMAGE \
        "$PROJECT_DIR/frontend"

    echo "📤 Loading Frontend image into Kind..."
    kind load docker-image $IMAGE_REGISTRY/$FRONTEND_IMAGE --name $CLUSTER_NAME

    echo "🔄 Restarting Frontend deployment..."
    kubectl rollout restart deployment/frontend -n iot-sims
    kubectl rollout status deployment/frontend -n iot-sims --timeout=120s

    echo "✅ Frontend updated!"
}

# Function to rebuild and reload Simulator
update_simulator() {
    echo "📦 Rebuilding MQTT Simulator..."
    docker build -t $IMAGE_REGISTRY/$SIM_IMAGE "$PROJECT_DIR/mqtt-simulator-master"

    echo "📤 Loading Simulator image into Kind..."
    kind load docker-image $IMAGE_REGISTRY/$SIM_IMAGE --name $CLUSTER_NAME

    echo "✅ Simulator updated! (New simulations will use the new image)"
}

# Main logic
case "${1:-all}" in
    api)
        update_api
        ;;
    frontend)
        update_frontend
        ;;
    simulator)
        update_simulator
        ;;
    all)
        echo "==========================================="
        echo "   Updating ALL images"
        echo "==========================================="
        update_api
        echo ""
        update_frontend
        echo ""
        update_simulator
        echo ""
        echo "==========================================="
        echo "   ✅ All images updated!"
        echo "==========================================="
        ;;
    *)
        echo "Usage: $0 [api|frontend|simulator|all]"
        echo ""
        echo "  api       - Rebuild and redeploy Manager API"
        echo "  frontend  - Rebuild and redeploy Frontend"
        echo "  simulator - Rebuild MQTT Simulator (new simulations use it)"
        echo "  all       - Update all images (default)"
        exit 1
        ;;
esac

echo ""
echo "📊 Current pod status:"
kubectl get pods -n iot-sims
