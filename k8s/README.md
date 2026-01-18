# Kubernetes Deployments

Configurações Kubernetes para o projeto IoT Simulator Platform.

## Estrutura

- `api-deployment.yaml` - Deployment da API FastAPI
- `api-service.yaml` - Service para a API
- `frontend-deployment.yaml` - Deployment do frontend React
- `frontend-service.yaml` - Service para o frontend
- `frontend-ingress.yaml` - Ingress para expor o frontend (opcional)
- `rbac-config.yaml` - Configuração RBAC para a API gerir pods

## Namespace

Todos os recursos usam o namespace `iot-sims`. Criar o namespace primeiro:

```bash
kubectl create namespace iot-sims
```

## Deploy da API

```bash
kubectl apply -f k8s/rbac-config.yaml
kubectl apply -f k8s/api-deployment.yaml
kubectl apply -f k8s/api-service.yaml
```

## Deploy do Frontend

```bash
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml
```

### Verificar Status

```bash
# Ver pods
kubectl get pods -n iot-sims

# Ver services
kubectl get svc -n iot-sims

# Ver logs do frontend
kubectl logs -n iot-sims -l app=frontend --tail=50
```

## Aceder aos Serviços

### Via Port-Forward (Desenvolvimento)

**Frontend:**
```bash
kubectl port-forward -n iot-sims svc/frontend-service 8080:80
```
Aceder em: `http://localhost:8080`

**API:**
```bash
kubectl port-forward -n iot-sims svc/manager-api-service 8000:80
```
Aceder em: `http://localhost:8000`

### Via Ingress (Produção)

Se tiveres um Ingress Controller instalado (ex: ingress-nginx):

```bash
kubectl apply -f k8s/frontend-ingress.yaml
```

Depois adicionar ao `/etc/hosts` (ou equivalente):
```
<ingress-ip> iot-simulator.local
```

## Variáveis de Ambiente

### Frontend

- `VITE_API_URL` - URL da API backend (padrão: `http://manager-api-service:80`)

**Nota:** Variáveis de ambiente do Vite são injetadas no build time. Se precisares de alterar após o build, usa um ConfigMap ou reconstrói a imagem.

### API

- `SIMULATOR_IMAGE` - Imagem Docker do simulador a usar
- `K8s_NAMESPACE` - Namespace Kubernetes onde criar pods

## Build e Push das Imagens

### Frontend

```bash
cd frontend
docker build -t ghcr.io/peqspc/iot-simulator-frontend:latest .
docker push ghcr.io/peqspc/iot-simulator-frontend:latest
```

### API

```bash
cd iot-simulator-api
docker build -t ghcr.io/peqspc/manager-api:latest .
docker push ghcr.io/peqspc/manager-api:latest
```

## Escalabilidade

O deployment do frontend está configurado com `replicas: 2` para alta disponibilidade. Ajustar conforme necessário:

```bash
kubectl scale deployment frontend -n iot-sims --replicas=3
```

## Troubleshooting

**Pods não iniciam:**
```bash
kubectl describe pod <pod-name> -n iot-sims
kubectl logs <pod-name> -n iot-sims
```

**Imagem não encontrada:**
- Verificar se a imagem foi pushed para o registry
- Verificar `imagePullPolicy` e credenciais

**Frontend não conecta à API:**
- Verificar se `VITE_API_URL` está correto
- Verificar se o service da API está acessível
- Verificar DNS do cluster (usar nome do service)


