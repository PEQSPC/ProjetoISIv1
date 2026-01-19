# Kind Cluster - Guia de Comandos

## Instalação

```bash
# Windows (com Chocolatey)
choco install kind

# Windows (com Scoop)
scoop install kind

# Linux/macOS
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind
```

---

## Gestão de Clusters

### Criar Cluster

```bash
# Cluster simples
kind create cluster

# Cluster com nome específico
kind create cluster --name meu-cluster

# Cluster com configuração personalizada
kind create cluster --config kind-config.yaml
```

### Listar Clusters

```bash
kind get clusters
```

### Eliminar Cluster

```bash
# Eliminar cluster default
kind delete cluster

# Eliminar cluster específico
kind delete cluster --name meu-cluster
```

### Ver Info do Cluster

```bash
kubectl cluster-info --context kind-kind
kubectl cluster-info --context kind-meu-cluster
```

---

## Kubectl - Comandos Básicos

### Contexto

```bash
# Ver contexto atual
kubectl config current-context

# Listar todos os contextos
kubectl config get-contexts

# Mudar de contexto
kubectl config use-context kind-meu-cluster
```

### Namespaces

```bash
# Listar namespaces
kubectl get namespaces

# Criar namespace
kubectl create namespace iot-sims

# Eliminar namespace
kubectl delete namespace iot-sims

# Definir namespace default
kubectl config set-context --current --namespace=iot-sims
```

---

## Pods

### Listar Pods

```bash
# Todos os pods no namespace atual
kubectl get pods

# Todos os pods em todos os namespaces
kubectl get pods -A

# Pods num namespace específico
kubectl get pods -n iot-sims

# Pods com mais detalhes
kubectl get pods -o wide

# Watch (atualização em tempo real)
kubectl get pods -w
```

### Detalhes de um Pod

```bash
kubectl describe pod <pod-name>
kubectl describe pod <pod-name> -n iot-sims
```

### Logs de um Pod

```bash
# Logs normais
kubectl logs <pod-name>

# Logs em tempo real (follow)
kubectl logs -f <pod-name>

# Últimas N linhas
kubectl logs --tail=50 <pod-name>

# Logs de um container específico (se pod tem múltiplos containers)
kubectl logs <pod-name> -c <container-name>
```

### Executar Comandos num Pod

```bash
# Executar comando
kubectl exec <pod-name> -- ls -la

# Shell interativo
kubectl exec -it <pod-name> -- /bin/bash
kubectl exec -it <pod-name> -- /bin/sh
```

### Criar/Eliminar Pods

```bash
# Criar pod a partir de YAML
kubectl apply -f pod.yaml

# Eliminar pod
kubectl delete pod <pod-name>

# Eliminar pod forçado
kubectl delete pod <pod-name> --force --grace-period=0
```

---

## Deployments

```bash
# Listar deployments
kubectl get deployments
kubectl get deploy

# Criar deployment
kubectl apply -f deployment.yaml

# Escalar deployment
kubectl scale deployment <name> --replicas=3

# Atualizar imagem
kubectl set image deployment/<name> <container>=<new-image>

# Ver histórico de rollouts
kubectl rollout history deployment/<name>

# Rollback
kubectl rollout undo deployment/<name>

# Reiniciar deployment
kubectl rollout restart deployment/<name>
```

---

## Services

```bash
# Listar services
kubectl get services
kubectl get svc

# Criar service
kubectl apply -f service.yaml

# Expor deployment como service
kubectl expose deployment <name> --port=80 --target-port=8080

# Port forward (acesso local)
kubectl port-forward svc/<service-name> 8080:80
kubectl port-forward pod/<pod-name> 8080:80
```

---

## ConfigMaps e Secrets

### ConfigMaps

```bash
# Listar
kubectl get configmaps

# Criar a partir de ficheiro
kubectl create configmap <name> --from-file=config.json

# Criar a partir de literal
kubectl create configmap <name> --from-literal=KEY=value

# Ver conteúdo
kubectl describe configmap <name>
kubectl get configmap <name> -o yaml
```

### Secrets

```bash
# Listar
kubectl get secrets

# Criar secret genérico
kubectl create secret generic <name> --from-literal=password=mysecret

# Criar secret para Docker registry
kubectl create secret docker-registry regcred \
  --docker-server=ghcr.io \
  --docker-username=<user> \
  --docker-password=<token>

# Ver secret (base64)
kubectl get secret <name> -o yaml

# Descodificar secret
kubectl get secret <name> -o jsonpath='{.data.password}' | base64 -d
```

---

## Ingress

```bash
# Instalar NGINX Ingress Controller no Kind
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

# Esperar pelo ingress controller
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=90s

# Listar ingresses
kubectl get ingress

# Criar ingress
kubectl apply -f ingress.yaml
```

---

## Carregar Imagens Docker no Kind

```bash
# Carregar imagem local para o cluster
kind load docker-image <image-name>:<tag>
kind load docker-image <image-name>:<tag> --name meu-cluster

# Exemplo
kind load docker-image my-api:latest
kind load docker-image ghcr.io/user/repo:sha-abc123
```

---

## Debug e Troubleshooting

### Ver Eventos

```bash
# Eventos do namespace atual
kubectl get events

# Eventos ordenados por tempo
kubectl get events --sort-by='.lastTimestamp'

# Eventos de um pod específico
kubectl get events --field-selector involvedObject.name=<pod-name>
```

### Recursos do Cluster

```bash
# Nodes
kubectl get nodes
kubectl describe node <node-name>

# Uso de recursos
kubectl top nodes
kubectl top pods
```

### Debug de Pod

```bash
# Pod não inicia? Ver eventos e describe
kubectl describe pod <pod-name>
kubectl get events --field-selector involvedObject.name=<pod-name>

# Ver logs mesmo de pods crashed
kubectl logs <pod-name> --previous
```

---

## Ficheiros YAML Úteis

### Pod Simples

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
  labels:
    app: my-app
spec:
  containers:
  - name: my-container
    image: nginx:latest
    ports:
    - containerPort: 80
```

### Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-deployment
spec:
  replicas: 2
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: my-container
        image: nginx:latest
        ports:
        - containerPort: 80
```

### Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  selector:
    app: my-app
  ports:
  - port: 80
    targetPort: 80
  type: ClusterIP
```

---

## Comandos Rápidos para Este Projeto

```bash
# Criar namespace para simulações
kubectl create namespace iot-sims

# Ver pods de simulação
kubectl get pods -n iot-sims

# Logs de uma simulação
kubectl logs -n iot-sims sim-<id>

# Eliminar simulação manualmente
kubectl delete pod -n iot-sims sim-<id>

# Ver todas as simulações a correr
kubectl get pods -n iot-sims -l app=iot-simulator

# Port forward para a API (se a correr no cluster)
kubectl port-forward -n iot-sims svc/iot-simulator-api 8000:80
```

---

## Atalhos Úteis (Aliases)

Adicionar ao `.bashrc` ou `.zshrc`:

```bash
alias k='kubectl'
alias kgp='kubectl get pods'
alias kgpa='kubectl get pods -A'
alias kgs='kubectl get svc'
alias kgd='kubectl get deploy'
alias kl='kubectl logs'
alias klf='kubectl logs -f'
alias kd='kubectl describe'
alias kaf='kubectl apply -f'
alias kdf='kubectl delete -f'
alias kex='kubectl exec -it'
```

---

## Links Úteis

- [Kind Documentation](https://kind.sigs.k8s.io/)
- [Kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
