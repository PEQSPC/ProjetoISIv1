#!/bin/bash
# ==========================================
# Local Dev Onboarding Script - Production Ready
# Tested on: WSL2 (Ubuntu 22.04), Linux, macOS
# ==========================================
set -e

CLUSTER_NAME="isi-dev-cluster"
IMAGE_REGISTRY="peqspc"
API_IMAGE="manager-api:latest"
SIM_IMAGE="mqtt-simulator:latest"
FRONTEND_IMAGE="iot-simulator-frontend:latest"
DOMAIN="iot-simulator.local"

# Get script directory (works on WSL, Linux, macOS)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Detect WSL and warn about performance if running from Windows mount
if [[ "$PROJECT_DIR" == /mnt/* ]]; then
    echo ""
    echo "⚠️  WARNING: Running from Windows filesystem (/mnt/...)."
    echo "   For better performance, clone the repo to WSL filesystem:"
    echo "   git clone <repo> ~/projects/ProjetoISIv1"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    [[ ! $REPLY =~ ^[Yy]$ ]] && exit 1
fi

echo "========================================="
echo "   ISIv1 SaaS - Local Dev Setup"
echo "========================================="
echo "📁 Project: $PROJECT_DIR"
echo ""

# 1. Check Prerequisites
echo "[1/10] Checking prerequisites..."
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed. Aborting." >&2; exit 1; }
command -v kind >/dev/null 2>&1 || { echo "❌ Kind is required but not installed. Aborting." >&2; exit 1; }
command -v kubectl >/dev/null 2>&1 || { echo "❌ Kubectl is required but not installed. Aborting." >&2; exit 1; }
command -v openssl >/dev/null 2>&1 || { echo "❌ OpenSSL is required but not installed. Aborting." >&2; exit 1; }

# Check if Docker daemon is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker daemon is not running." >&2
    echo "   WSL: Start Docker Desktop on Windows" >&2
    echo "   Linux: sudo systemctl start docker" >&2
    exit 1
fi

echo "✅ All prerequisites installed and Docker running"

# 2. Cleanup Old Cluster (Optional)
if kind get clusters | grep -q "^$CLUSTER_NAME$"; then
    read -p "Cluster '$CLUSTER_NAME' already exists. Delete and recreate? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "[2/10] Deleting existing cluster..."
        kind delete cluster --name $CLUSTER_NAME
    else
        echo "[2/10] Keeping existing cluster (will update deployments)..."
    fi
else
    echo "[2/10] No existing cluster found"
fi

# 3. Create Kind Cluster with Ingress Config
if ! kind get clusters | grep -q "^$CLUSTER_NAME$"; then
    echo "[3/10] Creating Kind cluster with ingress support..."
    kind create cluster --config "$PROJECT_DIR/k8s/kind-config.yaml"
else
    echo "[3/10] Using existing cluster"
fi

# Set kubectl context
kubectl config use-context kind-$CLUSTER_NAME

# 4. Install NGINX Ingress Controller
echo "[4/10] Installing NGINX Ingress Controller..."
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

echo "Waiting for ingress controller deployment to exist..."
until kubectl get deployment ingress-nginx-controller -n ingress-nginx >/dev/null 2>&1; do
  echo "  Waiting for deployment to be created..."
  sleep 2
done

echo "Waiting for ingress controller pods to exist..."
until kubectl get pods -n ingress-nginx -l app.kubernetes.io/component=controller 2>/dev/null | grep -q "ingress-nginx"; do
  echo "  Waiting for pods to be created..."
  sleep 3
done

echo "Waiting for ingress controller pods to be ready..."
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=180s

# 5. Build Docker Images (Local Build)
echo "[5/10] Building Docker images..."

echo "  📦 Building Manager API..."
docker build -t $IMAGE_REGISTRY/$API_IMAGE "$PROJECT_DIR/iot-simulator-api"

echo "  📦 Building MQTT Simulator..."
docker build -t $IMAGE_REGISTRY/$SIM_IMAGE "$PROJECT_DIR/mqtt-simulator-master"

echo "  📦 Building Frontend (with API URL for local dev)..."
docker build \
  --build-arg VITE_API_URL="https://$DOMAIN/api" \
  -t $IMAGE_REGISTRY/$FRONTEND_IMAGE \
  "$PROJECT_DIR/frontend"

# 6. Load Images into Kind
echo "[6/10] Loading images into Kind..."
kind load docker-image $IMAGE_REGISTRY/$API_IMAGE --name $CLUSTER_NAME
kind load docker-image $IMAGE_REGISTRY/$SIM_IMAGE --name $CLUSTER_NAME
kind load docker-image $IMAGE_REGISTRY/$FRONTEND_IMAGE --name $CLUSTER_NAME

# 7. Generate TLS Certificate (self-signed)
echo "[7/10] Generating self-signed TLS certificate..."
mkdir -p "$SCRIPT_DIR/certs"
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout "$SCRIPT_DIR/certs/tls.key" \
  -out "$SCRIPT_DIR/certs/tls.crt" \
  -subj "/CN=$DOMAIN/O=ISI-Dev" \
  -addext "subjectAltName=DNS:$DOMAIN,DNS:localhost" \
  2>/dev/null

# 8. Apply Kubernetes Manifests
echo "[8/10] Applying Kubernetes manifests..."

# Create Namespace
kubectl create namespace iot-sims --dry-run=client -o yaml | kubectl apply -f -

# Create TLS Secret from generated certs
kubectl create secret tls tls-secret \
  --cert="$SCRIPT_DIR/certs/tls.crt" \
  --key="$SCRIPT_DIR/certs/tls.key" \
  -n iot-sims \
  --dry-run=client -o yaml | kubectl apply -f -

# Apply ConfigMap from k8s folder
kubectl apply -f "$PROJECT_DIR/k8s/configmap.yaml"

# Apply API Secret (generate random JWT key for dev)
JWT_SECRET=$(openssl rand -hex 32)
kubectl create secret generic api-secrets \
  --from-literal=jwt-secret-key=$JWT_SECRET \
  -n iot-sims \
  --dry-run=client -o yaml | kubectl apply -f -

# Apply RBAC from k8s folder
kubectl apply -f "$PROJECT_DIR/k8s/rbac-config.yaml"

# 9. Apply Deployments (using local images)
echo "[9/10] Deploying applications..."

# API Deployment (inline to use local image with imagePullPolicy: Never)
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: manager-api
  namespace: iot-sims
spec:
  replicas: 2
  selector:
    matchLabels:
      app: manager-api
  template:
    metadata:
      labels:
        app: manager-api
    spec:
      serviceAccountName: sim-manager-sa
      containers:
      - name: api
        image: $IMAGE_REGISTRY/$API_IMAGE
        imagePullPolicy: Never
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: SIMULATOR_IMAGE
          value: "$IMAGE_REGISTRY/$SIM_IMAGE"
        - name: K8s_NAMESPACE
          value: "iot-sims"
        - name: JWT_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: jwt-secret-key
        - name: JWT_ACCESS_TOKEN_EXPIRE_MINUTES
          valueFrom:
            configMapKeyRef:
              name: api-config
              key: jwt-expire-minutes
        - name: ALLOWED_ORIGINS
          valueFrom:
            configMapKeyRef:
              name: api-config
              key: allowed-origins
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
EOF

# Frontend Deployment (inline to use local image)
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: iot-sims
spec:
  replicas: 2
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: $IMAGE_REGISTRY/$FRONTEND_IMAGE
        imagePullPolicy: Never
        ports:
        - containerPort: 80
          name: http
        resources:
          requests:
            memory: "64Mi"
            cpu: "50m"
          limits:
            memory: "128Mi"
            cpu: "100m"
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
EOF

# Apply Services from k8s folder
kubectl apply -f "$PROJECT_DIR/k8s/api-service.yaml"
kubectl apply -f "$PROJECT_DIR/k8s/frontend-service.yaml"

# Apply Ingress from k8s folder
kubectl apply -f "$PROJECT_DIR/k8s/frontend-ingress.yaml"

# 10. Wait for deployments
echo "[10/10] Waiting for deployments to be ready..."
kubectl rollout status deployment/manager-api -n iot-sims --timeout=120s || true
kubectl rollout status deployment/frontend -n iot-sims --timeout=120s || true

# Status & Instructions
echo ""
echo "========================================="
echo "         ✅ Setup Complete!"
echo "========================================="
echo ""
echo "📝 Add this to your hosts file:"
echo "   127.0.0.1 $DOMAIN"
echo ""
echo "   Windows: C:\\Windows\\System32\\drivers\\etc\\hosts"
echo "   Linux/Mac: /etc/hosts"
echo ""
echo "🌐 Access your app:"
echo "   https://$DOMAIN (accept self-signed cert warning)"
echo ""
echo "🔐 Default credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "📊 Useful commands:"
echo "   kubectl get pods -n iot-sims           # List pods"
echo "   kubectl logs -f deploy/manager-api -n iot-sims  # API logs"
echo "   kubectl logs -f deploy/frontend -n iot-sims     # Frontend logs"
echo "   kubectl get ingress -n iot-sims        # Check ingress"
echo ""
echo "🔑 JWT Secret generated for this session"
echo ""
echo "========================================="
