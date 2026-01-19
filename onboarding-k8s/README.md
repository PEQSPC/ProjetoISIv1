# Local Development Setup Guide

Este guia explica como configurar o ambiente de desenvolvimento local para a plataforma **IoT Simulation-as-a-Service** usando Kubernetes (Kind).

## Arquitetura Local

``` diagram
┌─────────────────────────────────────────────────────────────┐
│                    Kind Cluster                              │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                 Ingress Controller                       ││
│  │            (NGINX - ports 80/443)                        ││
│  └─────────────────────────────────────────────────────────┘│
│                           │                                  │
│           ┌───────────────┴───────────────┐                 │
│           │                               │                  │
│           ▼                               ▼                  │
│  ┌─────────────────┐             ┌─────────────────┐        │
│  │    Frontend     │             │   Manager API   │        │
│  │   (2 replicas)  │             │  (2 replicas)   │        │
│  │    nginx:80     │             │  FastAPI:8000   │        │
│  └─────────────────┘             └────────┬────────┘        │
│                                           │                  │
│                                           ▼                  │
│                                  ┌─────────────────┐        │
│                                  │  Simulator Pods │        │
│                                  │   (on-demand)   │        │
│                                  └─────────────────┘        │
│                                                              │
│  Namespace: iot-sims                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## Pré-requisitos

### Windows + WSL2 (Recomendado)

| Ferramenta | Instalação |
|------------|------------|
| **WSL2** | `wsl --install` (PowerShell como Admin) |
| **Ubuntu** | Microsoft Store → Ubuntu 22.04 |
| **Docker Desktop** | [Download](https://www.docker.com/products/docker-desktop/) |

**Configuração Docker Desktop:**
1. Settings → Resources → WSL Integration
2. ✅ Enable integration with your distro (Ubuntu)
3. Apply & Restart

**Instalar ferramentas no WSL:**

```bash
# Kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Kind
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind

# Verificar
docker --version
kubectl version --client
kind --version
```

### Linux / macOS

```bash
# Docker
# Linux: https://docs.docker.com/engine/install/
# macOS: Docker Desktop

# Kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install kubectl /usr/local/bin/

# Kind
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-$(uname -s | tr '[:upper:]' '[:lower:]')-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/
```

---

## Quick Start

### 1. Clonar o Repositório

**WSL (Recomendado - melhor performance):**

```bash
cd ~
git clone https://github.com/PEQSPC/ProjetoISIv1.git
cd ProjetoISIv1
```

> ⚠️ **Importante:** Clonar dentro do filesystem WSL (`~/...`) e NÃO em `/mnt/c/...` para melhor performance.

### 2. Executar o Script

```bash
cd onboarding-k8s
chmod +x setup-dev.sh
./setup-dev.sh
```

### 3. Configurar Hosts File

**Windows (PowerShell como Admin):**

```powershell
Add-Content C:\Windows\System32\drivers\etc\hosts "127.0.0.1 iot-simulator.local"
```

**Linux/macOS/WSL:**

```bash
echo "127.0.0.1 iot-simulator.local" | sudo tee -a /etc/hosts
```

### 4. Aceder à Aplicação

Abrir no browser: **https://iot-simulator.local**

> ⚠️ Aceitar o aviso de certificado self-signed (é esperado em dev)

---

## O Que o Script Faz

| Passo | Descrição |
|-------|-----------|
| **[1/9]** | Verifica pré-requisitos (docker, kind, kubectl, openssl) |
| **[2/9]** | Remove cluster existente (opcional, pergunta ao utilizador) |
| **[3/9]** | Cria cluster Kind com configuração de Ingress (portas 80/443) |
| **[4/9]** | Instala NGINX Ingress Controller |
| **[5/9]** | Compila imagens Docker (Manager API + MQTT Simulator) |
| **[6/9]** | Carrega imagens no cluster Kind |
| **[7/9]** | Gera certificado TLS self-signed para HTTPS |
| **[8/9]** | Aplica manifests K8s (namespace, secrets, configmaps, deployments, ingress) |
| **[9/9]** | Aguarda que os deployments fiquem prontos |

**Recursos criados:**

- Namespace: `iot-sims`
- Deployments: `manager-api` (2 réplicas), `frontend` (2 réplicas)
- Services: `manager-api-service`, `frontend-service`
- Ingress: TLS enabled em `iot-simulator.local`
- Secrets: JWT key, TLS certificate
- ConfigMaps: API configuration

---

## Estrutura de Ficheiros

```
ProjetoISIv1/
├── onboarding-k8s/
│   ├── setup-dev.sh          # Script principal de setup
│   ├── README.md             # Este ficheiro
│   └── certs/                # Certificados gerados (gitignored)
│
├── k8s/
│   ├── kind-config.yaml      # Configuração do cluster Kind
│   ├── api-deployment.yaml   # Deployment da API (2 réplicas, health checks)
│   ├── api-service.yaml      # Service da API
│   ├── frontend-deployment.yaml
│   ├── frontend-service.yaml
│   ├── frontend-ingress.yaml # Ingress com TLS
│   ├── rbac-config.yaml      # Permissões para criar simulator pods
│   ├── configmap.yaml        # Configurações não-sensíveis
│   └── secrets.yaml          # Template de secrets
│
├── iot-simulator-api/        # Código da API (FastAPI + Python)
├── mqtt-simulator-master/    # Código do simulador MQTT
└── frontend/                 # Frontend React + Vite
```

---

## Explicação dos Ficheiros K8s

### `kind-config.yaml`

Configuração do cluster Kind que simula um ambiente de produção localmente.

| Campo | Descrição |
|-------|-----------|
| `extraPortMappings` | Mapeia portas 80/443 do host para o cluster (necessário para Ingress) |
| `node-labels: ingress-ready=true` | Marca o node para receber o Ingress Controller |

### `api-deployment.yaml`

Deployment da Manager API (FastAPI).

| Campo | Valor | Descrição |
|-------|-------|-----------|
| `replicas` | 2 | Duas réplicas para alta disponibilidade |
| `image` | `peqspc/manager-api:latest` | Imagem Docker da API |
| `containerPort` | 8000 | Porta onde a API escuta |
| `livenessProbe` | `/health` | Verifica se o container está vivo |
| `readinessProbe` | `/health` | Verifica se está pronto para receber tráfego |
| `resources.limits` | 256Mi/200m | Limites de memória e CPU |

### `api-service.yaml`

Service ClusterIP que expõe a API internamente no cluster.

| Campo | Valor | Descrição |
|-------|-------|-----------|
| `type` | ClusterIP | Apenas acessível dentro do cluster |
| `port` | 80 | Porta do service |
| `targetPort` | 8000 | Porta do container |

### `frontend-deployment.yaml`

Deployment do Frontend (React + Nginx).

| Campo | Valor | Descrição |
|-------|-------|-----------|
| `replicas` | 2 | Duas réplicas para alta disponibilidade |
| `image` | `peqspc/iot-simulator-frontend:latest` | Imagem Docker do frontend |
| `containerPort` | 80 | Porta onde nginx escuta |

### `frontend-service.yaml`
Service ClusterIP que expõe o Frontend internamente.

| Campo | Valor | Descrição |
|-------|-------|-----------|
| `type` | ClusterIP | Apenas acessível dentro do cluster |
| `port` | 80 | Porta do service |
| `targetPort` | 80 | Porta do container nginx |

### `frontend-ingress.yaml`
Ingress que expõe a aplicação externamente com TLS.

| Campo | Descrição |
|-------|-----------|
| `host: iot-simulator.local` | Domínio local (configurar em `/etc/hosts`) |
| `tls.secretName: tls-secret` | Certificado TLS para HTTPS |
| `path: /` | Rota para o Frontend |
| `path: /api` | Rota para a API (reescrita para `/`) |
| `rewrite-target: /$2` | Remove `/api` antes de enviar à API |

### `rbac-config.yaml`
Permissões para a API criar pods de simuladores dinamicamente.

| Recurso | Descrição |
|---------|-----------|
| `ServiceAccount` | Identidade da API no cluster |
| `Role` | Permissões: create, get, list, delete pods |
| `RoleBinding` | Liga o ServiceAccount ao Role |

### `configmap.yaml`
Configurações não-sensíveis da aplicação.

| Chave | Valor | Descrição |
|-------|-------|-----------|
| `jwt-expire-minutes` | 60 | Expiração do token JWT |
| `log-level` | INFO | Nível de logging |
| `max-simulation-duration` | 120 | Duração máxima de simulação (minutos) |
| `allowed-origins` | `https://iot-simulator.local` | Origens CORS permitidas |

### `secrets.yaml`

Template de secrets (valores reais gerados pelo script).

| Secret | Descrição |
|--------|-----------|
| `api-secrets.jwt-secret-key` | Chave para assinar tokens JWT |
| `tls-secret` | Certificado TLS para HTTPS |

> ⚠️ **Nunca** commitar valores reais em `secrets.yaml`. Usar sealed-secrets ou vault em produção.

---

## Variáveis de Ambiente

### Manager API (FastAPI)

| Variável | Origem | Descrição |
|----------|--------|-----------|
| `JWT_SECRET_KEY` | Secret `api-secrets` | Chave para assinar/verificar tokens JWT |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | ConfigMap `api-config` | Tempo de expiração do token (default: 60) |
| `ALLOWED_ORIGINS` | ConfigMap `api-config` | Origens CORS permitidas (comma-separated) |
| `K8s_NAMESPACE` | Inline no deployment | Namespace onde criar pods de simuladores |
| `SIMULATOR_IMAGE` | Inline no deployment | Imagem Docker do simulador MQTT |

**Definição no Deployment:**
```yaml
env:
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
- name: K8s_NAMESPACE
  value: "iot-sims"
- name: SIMULATOR_IMAGE
  value: "peqspc/mqtt-simulator:latest"
```

### Frontend (React + Vite)

| Variável | Quando | Descrição |
|----------|--------|-----------|
| `VITE_API_URL` | **Build time** | URL da API (ex: `https://iot-simulator.local/api`) |

**Importante:** Variáveis `VITE_*` são **baked** no bundle JavaScript durante o build. Não podem ser alteradas em runtime.

**Build com variável customizada:**
```bash
docker build \
  --build-arg VITE_API_URL="https://iot-simulator.local/api" \
  -t peqspc/iot-simulator-frontend:latest \
  ./frontend
```

**Uso no código React:**
```typescript
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
```

### Simulador MQTT

| Variável | Descrição |
|----------|-----------|
| `SIM_CONFIG` | JSON com configuração do simulador (passado pelo API) |
| `DURATION_MINUTES` | Duração da simulação |

---

## Atualizar Imagens (update-images.sh)

Após fazer alterações ao código, usa o script `update-images.sh` para reconstruir e fazer redeploy:

```bash
chmod +x update-images.sh

# Atualizar apenas a API
./update-images.sh api

# Atualizar apenas o Frontend
./update-images.sh frontend

# Atualizar apenas o Simulador
./update-images.sh simulator

# Atualizar tudo (default)
./update-images.sh all
./update-images.sh
```

### O que o script faz

| Comando | Ação |
|---------|------|
| `api` | Rebuild imagem → Load no Kind → Rollout restart deployment |
| `frontend` | Rebuild com VITE_API_URL → Load no Kind → Rollout restart |
| `simulator` | Rebuild imagem → Load no Kind (novas simulações usam a nova imagem) |
| `all` | Executa os três acima |

> 💡 **Nota:** O simulador não tem deployment permanente. A nova imagem é usada quando se criam novas simulações.

---

## Comandos Úteis

### Ver Estado do Cluster

```bash
# Listar todos os pods
kubectl get pods -n iot-sims

# Ver logs da API (follow)
kubectl logs -f deploy/manager-api -n iot-sims

# Ver logs do frontend
kubectl logs -f deploy/frontend -n iot-sims

# Estado do ingress
kubectl get ingress -n iot-sims

# Ver eventos (útil para debug)
kubectl get events -n iot-sims --sort-by='.lastTimestamp'

# Descrever um pod com problemas
kubectl describe pod <pod-name> -n iot-sims
```

### Reiniciar Deployments

```bash
# Após alterações no código, reconstruir e reiniciar
kubectl rollout restart deployment/manager-api -n iot-sims
kubectl rollout restart deployment/frontend -n iot-sims
```

### Reconstruir Imagens Após Alterações

```bash
# Reconstruir API
docker build -t peqspc/manager-api:latest ../iot-simulator-api
kind load docker-image peqspc/manager-api:latest --name isi-dev-cluster
kubectl rollout restart deployment/manager-api -n iot-sims

# Reconstruir Simulator
docker build -t peqspc/mqtt-simulator:latest ../mqtt-simulator-master
kind load docker-image peqspc/mqtt-simulator:latest --name isi-dev-cluster
```

### Limpar Tudo

```bash
# Eliminar o cluster completamente
kind delete cluster --name isi-dev-cluster

# Limpar imagens Docker não usadas (opcional)
docker system prune -a
```

---

## Troubleshooting

### ❌ "Docker is not running" / "Cannot connect to Docker daemon"

**WSL:**

- Verificar se Docker Desktop está a correr no Windows
- Settings → Resources → WSL Integration → Ubuntu ✅

**Linux:**

```bash
sudo systemctl start docker
sudo usermod -aG docker $USER  # Evitar usar sudo
```

### ❌ "ImagePullBackOff" ou "ErrImageNeverPull"

A imagem não foi carregada no Kind:

```bash
# Verificar imagens no Kind
docker exec -it isi-dev-cluster-control-plane crictl images

# Recarregar imagem
kind load docker-image peqspc/manager-api:latest --name isi-dev-cluster
```

### ❌ Pods em "CrashLoopBackOff"

```bash
# Ver logs do pod
kubectl logs -n iot-sims <pod-name>

# Ver logs do container anterior (se crashou)
kubectl logs -n iot-sims <pod-name> --previous

# Ver eventos
kubectl describe pod -n iot-sims <pod-name>
```

### ❌ "connection refused" / Ingress não funciona

1. Verificar se o ingress controller está a correr:

```bash
kubectl get pods -n ingress-nginx
# Deve mostrar pod "ingress-nginx-controller-xxx" em Running
```

1. Verificar hosts file:

```bash
cat /etc/hosts | grep iot-simulator
# Deve mostrar: 127.0.0.1 iot-simulator.local
```

1. Testar conexão direta:

```bash
curl -k https://localhost
curl -k https://iot-simulator.local
```

### ❌ Performance muito lenta (WSL)

O projeto está no filesystem Windows. Mover para WSL:

```bash
# Copiar para WSL
cp -r /mnt/c/Users/<user>/projects/ProjetoISIv1 ~/projects/

# Trabalhar a partir de WSL
cd ~/projects/ProjetoISIv1
```

### ❌ "permission denied" ao executar script

```bash
chmod +x setup-dev.sh
./setup-dev.sh
```

### ❌ "Cluster already exists"

O script pergunta se quer eliminar. Se preferir manter:

- Responder "n" para manter o cluster existente
- Os manifests serão reaplicados

---

## Diferenças: Local vs Produção

| Aspecto | Local (Dev) | Produção |
|---------|-------------|----------|
| **Cluster** | Kind (single node) | EKS/GKE/AKS (multi-node) |
| **Imagens** | Locais (`imagePullPolicy: Never`) | Registry (`imagePullPolicy: Always`) |
| **TLS** | Self-signed certificate | Let's Encrypt (cert-manager) |
| **Secrets** | Gerados pelo script | HashiCorp Vault / Sealed Secrets |
| **Domínio** | `iot-simulator.local` | Domínio real com DNS |
| **Réplicas** | 2 por deployment | 3+ com HPA (auto-scaling) |
| **Monitoring** | Não configurado | Prometheus + Grafana |

---

## Credenciais Default

| Serviço | Username | Password |
|---------|----------|----------|
| **App Login** | `admin` | `admin123` |

> ⚠️ Alterar em produção!

---

## Próximos Passos

Após o setup local funcionar:

- [ ] Configurar ArgoCD para GitOps
- [ ] Adicionar monitoring (Prometheus + Grafana)
- [ ] Configurar CI/CD pipeline completo
- [ ] Implementar backup da base de dados
- [ ] Configurar Network Policies
