# Roadmap Completo - Plataforma de Simulação IoT

**Projeto:** Sistema de Simulação IoT sob Demanda  
**Objetivo:** API REST que provisiona simuladores MQTT dinamicamente  
**Stack Base:** Python + FastAPI + Docker + MQTT  
**Duração Total:** 12-16 semanas (3 fases)

---

## Visão Geral

```
Fase 1 (MVP)          Fase 2 (Kubernetes)     Fase 3 (Produção)
Semanas 1-4           Semanas 5-10            Semanas 11-16
    │                      │                        │
    ├─ API REST           ├─ K8s Client            ├─ CI/CD
    ├─ Docker Local       ├─ Pods Dinâmicos        ├─ Monitoring
    ├─ SQLite             ├─ PostgreSQL            ├─ Auth/Billing
    └─ Demo Funcional     └─ Multi-User            └─ Deploy Cloud
```

**Estado Atual:** Fase 1 - 70% completo (API + Docker + SQLite funcionais)

---

## FASE 1 - MVP Funcional (4 semanas)

**Objetivo:** Sistema local funcional para demonstração universitária  
**Entregáveis:** API REST + Docker + SQLite + Documentação + Demo

### Semana 1: Core Implementation (ATUAL)

**Status:** 🟡 Em Progresso

#### Dia 1-2: Finalizar Integração Docker
- [x] Pull da imagem `ghcr.io/damascenorafael/mqtt-simulator:sha-a73a2e8`
- [x] API cria containers com config JSON
- [x] Adicionar flag `-f` no comando Docker
- [ ] **Testar:** Container lê config corretamente
- [ ] **Validar:** `docker logs` mostra tópicos configurados

**Código-chave:**
```python
container = docker_client.containers.run(
    "ghcr.io/damascenorafael/mqtt-simulator:sha-a73a2e8",
    command=["-f", "/config/settings.json"],
    volumes={config_path: {'bind': '/config/settings.json', 'mode': 'ro'}},
    detach=True,
    remove=True
)
```

#### Dia 3-4: Persistência SQLite
- [x] Modelo `Simulation` com SQLAlchemy
- [x] Endpoints CRUD completos
- [ ] **Corrigir:** Health check database "disconnected"
- [ ] **Adicionar:** Campo `expires_at` na tabela
- [ ] **Implementar:** Cleanup de expirados ao startup

**Tasks específicas:**
```bash
# Recriar BD com novo campo
rm simulations.db
python3 -c "from database import Base, engine; Base.metadata.create_all(bind=engine)"

# Adicionar ao database.py
expires_at = Column(DateTime, nullable=False)

# Adicionar ao main.py startup
@app.on_event("startup")
async def startup_event():
    cleanup_expired_simulations()
```

#### Dia 5-7: Auto-Stop e Cleanup
- [x] Thread para auto-stop após duração
- [ ] **Implementar:** Função `cleanup_expired_simulations()`
- [ ] **Testar:** Criar simulação 2 min → para automaticamente
- [ ] **Testar:** Reiniciar API → containers órfãos limpos
- [ ] **Validar:** BD atualiza status para "expired"

**Checklist de Validação:**
- [ ] Container para após `duration_minutes`
- [ ] BD atualiza `stopped_at` e `status='expired'`
- [ ] Ficheiro config temporário é removido
- [ ] Containers órfãos limpos ao reiniciar API

---

### Semana 2: Robustez e Error Handling

#### Dia 8-9: Tratamento de Erros
- [ ] Try/catch robusto em todos endpoints
- [ ] Validação Pydantic completa (todos campos obrigatórios)
- [ ] Mensagens de erro descritivas
- [ ] HTTP status codes corretos (404, 422, 500)

**Endpoints a revisar:**
```python
# POST /simulations
- 422: Config JSON inválido
- 404: Docker image não encontrada
- 500: Erro ao criar container

# GET /simulations/{id}
- 404: Simulação não existe
- 200: Retorna logs mesmo se container parou

# DELETE /simulations/{id}
- 404: Simulação não existe
- 400: Simulação já parada
- 204: Sucesso
```

#### Dia 10-11: Features Adicionais
- [ ] Endpoint `GET /simulations?status=running&limit=20`
- [ ] Endpoint `GET /stats` (total, running, stopped, expired)
- [ ] Endpoint `GET /simulations/{id}/logs` (últimas 100 linhas)
- [ ] Response models Pydantic para todos endpoints

**Código exemplo:**
```python
@app.get("/simulations", response_model=List[SimulationListItem])
async def list_simulations(
    status: Optional[str] = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):
    query = db.query(Simulation)
    
    if status:
        query = query.filter(Simulation.status == status)
    
    total = query.count()
    sims = query.order_by(Simulation.created_at.desc()).offset(offset).limit(limit).all()
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "simulations": [...]
    }
```

#### Dia 12-14: Testes Manuais Completos
- [ ] Criar 5 configs JSON diferentes (single, multiple, list topics)
- [ ] Testar cada endpoint com Postman/curl
- [ ] Stress test: criar 10 simulações simultâneas
- [ ] Load test: criar → parar → criar 50x
- [ ] Verificar memory leaks (containers não limpos)

**Checklist de Testes:**
```bash
# Test 1: Happy path
curl -X POST http://localhost:8000/simulations -d @config.json
# Verificar: container ativo, BD tem entrada, logs funcionam

# Test 2: Config inválido
curl -X POST http://localhost:8000/simulations -d '{"invalid": true}'
# Verificar: retorna 422 com mensagem clara

# Test 3: Listar e filtrar
curl http://localhost:8000/simulations?status=running
# Verificar: só mostra simulações ativas

# Test 4: Auto-stop
# Criar simulação 1 min, esperar → container deve parar

# Test 5: Cleanup após restart
# Criar 3 simulações, matar API (Ctrl+C), reiniciar
# Verificar: simulações expiradas têm status correto
```

---

### Semana 3: Documentação e Cliente de Teste

#### Dia 15-16: README.md Completo
- [ ] Secção "Instalação" passo-a-passo
- [ ] Secção "Configuração" (Docker, SQLite)
- [ ] Secção "Uso" com exemplos de curl/Postman
- [ ] Secção "Arquitetura" com diagrama
- [ ] Secção "API Reference" (ou link para Swagger)
- [ ] Screenshots do Swagger UI

**Template README.md:**
```markdown
# IoT Simulator Platform

API REST para criar simuladores IoT sob demanda usando Docker.

## Features
- ✅ Criação dinâmica de simuladores MQTT
- ✅ Configuração JSON flexível
- ✅ Auto-stop após duração especificada
- ✅ Persistência SQLite
- ✅ Cleanup automático de containers órfãos

## Instalação

### Requisitos
- Python 3.11+
- Docker
- pip

### Setup
```bash
git clone <repo>
cd iot-simulator-api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Executar
```bash
uvicorn main:app --reload --port 8000
```

Aceder: http://localhost:8000/docs

## Uso

### Criar Simulação
```bash
curl -X POST http://localhost:8000/simulations \
  -H "Content-Type: application/json" \
  -d '{
    "BROKER_URL": "test.mosquitto.org",
    "BROKER_PORT": 1883,
    "TIME_INTERVAL": 10,
    "duration_minutes": 30,
    "TOPICS": [...]
  }'
```

### Listar Simulações
```bash
curl http://localhost:8000/simulations
```

### Ver Logs
```bash
curl http://localhost:8000/simulations/{id}/logs
```

## Arquitetura

```
┌─────────────┐
│   Cliente   │
└──────┬──────┘
       │ POST /simulations
       ▼
┌──────────────────┐
│  FastAPI REST    │
│  :8000           │
└────┬─────────────┘
     │
     ├──► Docker Engine (cria container)
     │
     └──► SQLite (guarda metadata)
```

## Exemplos de Config

Ver pasta `examples/` para configs prontos:
- `factory.json` - Simulação industrial
- `agriculture.json` - Sensores agrícolas
- `smart-home.json` - Casa inteligente

## Troubleshooting

**Erro: Database disconnected**
```bash
rm simulations.db
python3 -c "from database import Base, engine; Base.metadata.create_all(bind=engine)"
```

**Container não para**
- Verificar `duration_minutes` foi especificado
- Ver logs da API para mensagens "[AUTO-STOP]"
```

#### Dia 17-18: Cliente HTML de Teste
- [ ] HTML básico para conectar a broker MQTT
- [ ] Usar MQTT.js para subscrever tópicos
- [ ] Mostrar mensagens em tempo real
- [ ] Adicionar gráfico Chart.js (opcional)

**Ficheiro `test-client/index.html`:**
```html
<!DOCTYPE html>
<html>
<head>
    <title>IoT Simulator - Test Client</title>
    <script src="https://unpkg.com/mqtt@5.3.5/dist/mqtt.min.js"></script>
    <style>
        body { font-family: Arial; max-width: 800px; margin: 50px auto; }
        input { padding: 10px; width: 300px; }
        button { padding: 10px 20px; }
        #messages { 
            border: 1px solid #ccc; 
            height: 400px; 
            overflow-y: scroll; 
            padding: 10px; 
            margin-top: 20px;
            font-family: monospace;
        }
        .message { padding: 5px; border-bottom: 1px solid #eee; }
    </style>
</head>
<body>
    <h1>🔌 IoT Simulator Test Client</h1>
    
    <div>
        <input id="broker" placeholder="Broker (ex: test.mosquitto.org)" value="test.mosquitto.org">
        <input id="topic" placeholder="Topic pattern (ex: fabrica/#)" value="demo/#">
        <button onclick="connect()">Connect</button>
        <button onclick="disconnect()">Disconnect</button>
        <button onclick="clearMessages()">Clear</button>
    </div>
    
    <div id="status">Disconnected</div>
    <div id="messages"></div>
    
    <script>
        let client = null;
        
        function connect() {
            const broker = document.getElementById('broker').value;
            const topic = document.getElementById('topic').value;
            
            if (client) client.end();
            
            document.getElementById('status').textContent = 'Connecting...';
            
            client = mqtt.connect(`ws://${broker}:8080`);
            
            client.on('connect', () => {
                document.getElementById('status').textContent = '✅ Connected';
                client.subscribe(topic);
                addMessage(`Subscribed to: ${topic}`, 'info');
            });
            
            client.on('message', (t, payload) => {
                try {
                    const data = JSON.parse(payload.toString());
                    addMessage(`${t}: ${JSON.stringify(data, null, 2)}`, 'data');
                } catch {
                    addMessage(`${t}: ${payload.toString()}`, 'data');
                }
            });
            
            client.on('error', (err) => {
                document.getElementById('status').textContent = '❌ Error';
                addMessage(`Error: ${err.message}`, 'error');
            });
        }
        
        function disconnect() {
            if (client) {
                client.end();
                document.getElementById('status').textContent = 'Disconnected';
                addMessage('Disconnected', 'info');
            }
        }
        
        function clearMessages() {
            document.getElementById('messages').innerHTML = '';
        }
        
        function addMessage(msg, type) {
            const div = document.createElement('div');
            div.className = `message ${type}`;
            div.textContent = `[${new Date().toLocaleTimeString()}] ${msg}`;
            document.getElementById('messages').appendChild(div);
            div.scrollIntoView();
        }
    </script>
</body>
</html>
```

#### Dia 19-21: Configs de Exemplo
- [ ] `examples/factory.json` - Linha de produção
- [ ] `examples/agriculture.json` - Sensores agrícolas
- [ ] `examples/smart-home.json` - Casa inteligente
- [ ] `examples/fleet.json` - Gestão de frota (GPS)

**Exemplo `examples/factory.json`:**
```json
{
  "BROKER_URL": "test.mosquitto.org",
  "BROKER_PORT": 1883,
  "TIME_INTERVAL": 5,
  "duration_minutes": 10,
  "TOPICS": [
    {
      "TYPE": "multiple",
      "PREFIX": "fabrica/maquina",
      "RANGE_START": 1,
      "RANGE_END": 5,
      "DATA": [
        {
          "NAME": "producao_unidades",
          "TYPE": "int",
          "MIN_VALUE": 50,
          "MAX_VALUE": 100,
          "MAX_STEP": 5,
          "INCREASE_PROBABILITY": 0.6,
          "RETAIN_PROBABILITY": 0.7
        },
        {
          "NAME": "temperatura_motor",
          "TYPE": "float",
          "MIN_VALUE": 40.0,
          "MAX_VALUE": 85.0,
          "MAX_STEP": 2.5,
          "INCREASE_PROBABILITY": 0.5,
          "RETAIN_PROBABILITY": 0.8
        },
        {
          "NAME": "defeitos",
          "TYPE": "int",
          "MIN_VALUE": 0,
          "MAX_VALUE": 3,
          "MAX_STEP": 1,
          "INCREASE_PROBABILITY": 0.2,
          "RETAIN_PROBABILITY": 0.95
        }
      ]
    }
  ]
}
```

---

### Semana 4: Apresentação e Demo

#### Dia 22-23: Slides de Apresentação
- [ ] Slide 1: Título + Nome + Data
- [ ] Slide 2-3: Problema e Contexto
- [ ] Slide 4: Solução Proposta
- [ ] Slide 5: Arquitetura Técnica
- [ ] Slide 6: Stack Tecnológica
- [ ] Slide 7-8: Demo ao Vivo
- [ ] Slide 9: Features Implementadas
- [ ] Slide 10: Roadmap Futuro (Fase 2-3)
- [ ] Slide 11: Conclusão
- [ ] Slide 12: Q&A

**Template Slides (Markdown → reveal.js):**
```markdown
---
title: Plataforma de Simulação IoT
author: [Teu Nome]
date: 2025
---

# Plataforma de Simulação IoT
## API REST para Simulação sob Demanda

[Teu Nome]  
Projeto ISI - 2024/2025

---

## O Problema

- Desenvolvimento IoT **custa 45.000-500.000 USD**
- Setup de hardware **demora semanas**
- Impossível testar cenários extremos
- Riscos: danificar equipamento caro

**Solução:** Virtualizar sensores

---

## Solução Proposta

**API REST** que cria **simuladores MQTT** dinamicamente

```bash
POST /simulations + JSON config
↓
Container Docker inicia
↓
Dados MQTT em tempo real
```

**Benefícios:**
- Setup em < 1 minuto
- Custo: 0 EUR (usa broker público)
- Cenários impossíveis no mundo real

---

## Arquitetura

```
┌──────────┐
│ Cliente  │
└────┬─────┘
     │ POST /simulations
     ▼
┌─────────────┐
│ FastAPI     │──► SQLite (metadata)
│ REST API    │
└──────┬──────┘
       │
       └──► Docker Engine
            │
            └──► mqtt-simulator container
                 (publica MQTT)
```

---

## Stack Tecnológica

**Backend:**
- Python 3.11
- FastAPI (API REST)
- SQLAlchemy + SQLite
- Docker SDK

**Simulador:**
- mqtt-simulator (imagem existente)
- MQTT protocol
- Random walk data generation

**Tools:**
- Swagger UI (documentação automática)
- Postman (testes)

---

## Demo ao Vivo

1. Abrir Swagger UI
2. POST criar simulação (factory.json)
3. Ver container ativo: `docker ps`
4. Ver logs: `docker logs <id>`
5. Abrir cliente HTML
6. Ver dados MQTT em tempo real
7. Simulação para automaticamente

---

## Features Implementadas

✅ API REST completa (CRUD)  
✅ Persistência SQLite  
✅ Auto-stop após duração  
✅ Cleanup automático  
✅ Swagger UI  
✅ Tratamento de erros robusto  
✅ Cliente de teste HTML  
✅ Configs de exemplo prontos  

---

## Roadmap Futuro

**Fase 2 (4-6 semanas):**
- Kubernetes para multi-user
- PostgreSQL
- Isolamento por utilizador

**Fase 3 (8+ semanas):**
- Autenticação JWT
- Billing e quotas
- Monitoring (Prometheus/Grafana)
- Deploy cloud (AWS/GCP)

---

## Conclusão

**Objetivo Alcançado:**
- ✅ MVP funcional
- ✅ Demonstra conceito
- ✅ Código limpo e documentado
- ✅ Extensível (roadmap claro)

**Aprendizagens:**
- FastAPI + Docker integration
- SQLAlchemy ORM
- MQTT protocol
- Container lifecycle management

---

## Perguntas?

📧 [teu-email]@example.com  
🔗 GitHub: [link-repo]  
📄 Documentação: http://localhost:8000/docs
```

#### Dia 24-25: Script e Ensaio de Demo
- [ ] Escrever script palavra-a-palavra (7-10 minutos)
- [ ] Ensaiar 3x sozinho
- [ ] Gravar vídeo backup (se demo falhar)
- [ ] Preparar dados de teste (não improvisar)

**Script de Demo (7 minutos):**

```
[00:00-01:00] Introdução
"Bom dia. Hoje vou apresentar uma plataforma de simulação IoT que 
permite testar aplicações sem hardware físico.

O problema: desenvolver IoT custa entre 45 mil e 500 mil dólares,
e demora semanas só para configurar sensores.

A minha solução: API REST que cria simuladores virtuais em segundos."

[01:00-02:00] Mostrar Arquitetura
"A arquitetura é simples: FastAPI recebe config JSON, cria container
Docker com o simulador, e publica dados via MQTT.

Stack: Python, FastAPI, Docker, SQLite para persistência."

[02:00-05:00] Demo ao Vivo
"Vou demonstrar. Aqui está o Swagger UI da API.

1. POST /simulations - vou criar uma simulação de fábrica
   [Colar factory.json pré-preparado]
   
2. Executar... sucesso! Retornou simulation_id e container_id.

3. Ver container ativo [terminal: docker ps]
   Aqui está, nome sim-abc123, a correr.

4. Ver logs [terminal: docker logs sim-abc123]
   Dados sendo publicados: fabrica/maquina1, maquina2...

5. Abrir cliente HTML [browser]
   Conectar ao broker... subscribed!
   Dados chegam em tempo real, aqui temperatura, produção, defeitos.

6. Listar simulações [Swagger GET /simulations]
   Aparece na base de dados, status running.

7. Esta simulação está configurada para 2 minutos...
   [esperar ou cortar] ...e para automaticamente.

8. Se reiniciar a API [Ctrl+C, uvicorn main:app]
   Containers órfãos são limpos ao startup."

[05:00-06:00] Código
"Rapidamente o código: main.py tem ~300 linhas.
POST /simulations valida JSON com Pydantic, cria container Docker,
guarda na BD, agenda auto-stop.

Database.py - modelo SQLAlchemy simples, SQLite para persistência."

[06:00-07:00] Conclusão
"Resumindo: sistema funcional que demonstra o conceito.
MVP completo com persistência, auto-stop, cleanup.

Próximos passos seriam adicionar Kubernetes para multi-user,
autenticação, billing.

Mas para esta fase, objetivo alcançado: API REST que cria
simuladores sob demanda. Obrigado."
```

#### Dia 26-28: Buffer e Polimento Final
- [ ] Corrigir bugs encontrados durante ensaios
- [ ] Melhorar mensagens de erro
- [ ] Adicionar logs mais descritivos
- [ ] Verificar todos requirements.txt
- [ ] Limpar código commented out
- [ ] Formatar código (black, autopep8)

**Checklist Pré-Apresentação:**
```bash
# Código
- [ ] Sem erros ao iniciar: uvicorn main:app
- [ ] Swagger abre: http://localhost:8000/docs
- [ ] Health check OK: curl http://localhost:8000/health
- [ ] Criar simulação funciona com factory.json
- [ ] Cliente HTML conecta e mostra dados

# Documentação
- [ ] README.md completo e sem typos
- [ ] Comentários em funções críticas
- [ ] requirements.txt atualizado

# Demo
- [ ] factory.json testado e funciona
- [ ] Cliente HTML funciona em browser fresh
- [ ] Script impresso ou em tablet
- [ ] Vídeo backup gravado e testado
- [ ] Slides exportados em PDF

# Contingência
- [ ] Laptop carregado
- [ ] Segundo laptop disponível
- [ ] Internet backup (hotspot telemóvel)
- [ ] Docker images pré-downloaded
```

---

## 🎓 MARCO: Apresentação Fase 1

**Entregáveis Mínimos:**
- ✅ Código fonte funcionando
- ✅ README.md
- ✅ Slides apresentação
- ✅ Demo ao vivo (ou vídeo backup)

**Critérios de Sucesso:**
- API cria simulações com config JSON
- Containers Docker iniciam e publicam MQTT
- Auto-stop funciona
- Persistência SQLite funciona
- Cleanup de órfãos funciona ao reiniciar

---

## FASE 2 - Kubernetes Multi-User (6 semanas)

**Objetivo:** Migrar para Kubernetes, suportar múltiplos utilizadores  
**Pré-requisitos:** Fase 1 100% funcional, conhecimento básico K8s

### Semana 5-6: Setup Kubernetes

#### Aprender Kubernetes Básico
- [ ] Curso online (2-3 dias): Kubernetes for Beginners
- [ ] Conceitos: Pods, Deployments, Services, Namespaces
- [ ] kubectl comandos básicos
- [ ] Instalar minikube ou kind para testes locais

**Recursos:**
- Kubernetes.io tutorials
- "Kubernetes Up & Running" (livro)
- KodeKloud free tier

#### Setup Cluster Local
- [ ] Instalar minikube: `brew install minikube`
- [ ] Iniciar cluster: `minikube start`
- [ ] Testar: `kubectl get nodes`
- [ ] Criar namespace: `kubectl create namespace simulations`

#### Kubernetes Python Client
- [ ] Instalar: `pip install kubernetes`
- [ ] Testar conexão:
```python
from kubernetes import client, config
config.load_kube_config()
v1 = client.CoreV1Api()
print(v1.list_pod_for_all_namespaces())
```

### Semana 7-8: Migrar Docker → Kubernetes

#### Criar Pods Dinamicamente
- [ ] Refactor `create_simulation()` para usar K8s API
- [ ] Criar Pod spec para simulador
- [ ] Montar ConfigMap com JSON config
- [ ] Testar criação de Pod

**Código-chave:**
```python
from kubernetes import client, config

config.load_kube_config()
k8s = client.CoreV1Api()

def create_simulator_pod(sim_id: str, config_json: dict):
    # Criar ConfigMap
    configmap = client.V1ConfigMap(
        metadata=client.V1ObjectMeta(name=f"config-{sim_id}"),
        data={"settings.json": json.dumps(config_json)}
    )
    k8s.create_namespaced_config_map("simulations", configmap)
    
    # Criar Pod
    pod = client.V1Pod(
        metadata=client.V1ObjectMeta(name=f"sim-{sim_id}"),
        spec=client.V1PodSpec(
            containers=[
                client.V1Container(
                    name="simulator",
                    image="ghcr.io/damascenorafael/mqtt-simulator:sha-a73a2e8",
                    command=["-f", "/config/settings.json"],
                    volume_mounts=[
                        client.V1VolumeMount(
                            name="config",
                            mount_path="/config"
                        )
                    ]
                )
            ],
            volumes=[
                client.V1Volume(
                    name="config",
                    config_map=client.V1ConfigMapVolumeSource(
                        name=f"config-{sim_id}"
                    )
                )
            ],
            restart_policy="Never"
        )
    )
    
    k8s.create_namespaced_pod("simulations", pod)
    return f"sim-{sim_id}"
```

#### Expor Pods via Service
- [ ] Criar Service para acesso externo
- [ ] Testar acesso MQTT via NodePort
- [ ] Documentar endpoint para utilizadores

#### Cleanup em Kubernetes
- [ ] Implementar `delete_pod()` com K8s API
- [ ] Adicionar `activeDeadlineSeconds` aos Pods
- [ ] CronJob para limpar Pods expirados

### Semana 9-10: PostgreSQL e Multi-User

#### Migrar SQLite → PostgreSQL
- [ ] Instalar PostgreSQL (Docker ou managed)
- [ ] Migração schema (manual ou Alembic)
- [ ] Atualizar connection string
- [ ] Testar CRUD operations

**Migration script:**
```python
# migrate_to_postgres.py
import sqlite3
import psycopg2

# Ler de SQLite
sqlite_conn = sqlite3.connect('simulations.db')
sqlite_cursor = sqlite_conn.cursor()
rows = sqlite_cursor.execute("SELECT * FROM simulations").fetchall()

# Escrever em PostgreSQL
pg_conn = psycopg2.connect("postgresql://user:pass@localhost/iotsim")
pg_cursor = pg_conn.cursor()

for row in rows:
    pg_cursor.execute(
        "INSERT INTO simulations (...) VALUES (...)",
        row
    )

pg_conn.commit()
```

#### Adicionar Utilizadores
- [ ] Tabela `users` (id, email, password_hash)
- [ ] Endpoint POST /auth/register
- [ ] Endpoint POST /auth/login (retorna JWT)
- [ ] Middleware para verificar JWT
- [ ] Filtrar simulações por user_id

**Modelo User:**
```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    simulations = relationship("Simulation", back_populates="user")

class Simulation(Base):
    # ... campos existentes ...
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="simulations")
```

#### Rate Limiting
- [ ] Instalar Redis
- [ ] Implementar rate limiter (5 simulações/hora/user)
- [ ] Middleware para verificar limites
- [ ] Retornar 429 Too Many Requests

---

## FASE 3 - Production Ready (6 semanas)

**Objetivo:** Sistema pronto para deploy real  
**Pré-requisitos:** Fase 2 funcional, cluster K8s real

### Semana 11-12: Autenticação e Segurança

#### JWT Completo
- [ ] Refresh tokens
- [ ] Logout (blacklist tokens)
- [ ] Password reset flow
- [ ] Email verification (opcional)

#### RBAC Kubernetes
- [ ] ServiceAccount para API
- [ ] Role com permissões mínimas
- [ ] RoleBinding
- [ ] Testar permissões

#### Secrets Management
- [ ] Kubernetes Secrets para DB password
- [ ] Secrets para JWT secret key
- [ ] Não commitar secrets no Git

### Semana 13-14: Monitoring e Observability

#### Prometheus
- [ ] Instalar Prometheus no cluster
- [ ] Adicionar metrics na API (prometheus_client)
- [ ] Dashboards Grafana básicos

**Métricas importantes:**
```python
from prometheus_client import Counter, Histogram

simulations_created = Counter('simulations_created_total', 'Total sims')
simulation_duration = Histogram('simulation_duration_seconds', 'Duration')
pods_active = Gauge('pods_active', 'Active pods')
```

#### Logging
- [ ] Structured logging (JSON)
- [ ] Loki para agregação logs
- [ ] Queries úteis em Grafana

### Semana 15-16: CI/CD e Deploy

#### GitHub Actions
- [ ] Pipeline: test → build → push image
- [ ] Deploy automático ao push main
- [ ] Rollback automático se falhar

**Exemplo `.github/workflows/deploy.yml`:**
```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker image
      run: docker build -t iotsim-api:${{ github.sha }} .
    
    - name: Push to registry
      run: docker push iotsim-api:${{ github.sha }}
    
    - name: Deploy to K8s
      run: |
        kubectl set image deployment/iotsim-api \
          api=iotsim-api:${{ github.sha }}
```

#### Deploy Cloud
- [ ] Escolher provider (DigitalOcean, Linode, AWS)
- [ ] Criar cluster managed Kubernetes
- [ ] Configurar DNS
- [ ] SSL/TLS (Let's Encrypt)

---

## Milestones e Entregáveis

### Milestone 1: MVP Demo (Semana 4)
**Entregáveis:**
- Código fonte completo
- README.md
- API funcionando localmente
- Demo gravada (backup)
- Slides apresentação

**Critérios de Sucesso:**
- [ ] API cria simulações
- [ ] Auto-stop funciona
- [ ] Persistência funciona
- [ ] Demo de 7 min ensaiada

---

### Milestone 2: Kubernetes Working (Semana 10)
**Entregáveis:**
- Código migrado para K8s
- Manifests YAML
- PostgreSQL funcional
- Multi-user básico

**Critérios de Sucesso:**
- [ ] Pods criados dinamicamente
- [ ] Múltiplos users isolados
- [ ] Rate limiting funciona
- [ ] Documentação atualizada

---

### Milestone 3: Production Deploy (Semana 16)
**Entregáveis:**
- Sistema deployed em cloud
- CI/CD funcional
- Monitoring setup
- Documentação completa

**Critérios de Sucesso:**
- [ ] API acessível publicamente
- [ ] SSL/TLS configurado
- [ ] Logs e métricas visíveis
- [ ] Zero-downtime deploys

---

## Checklists de Validação

### Checklist Fase 1 (antes de apresentar)
```
Funcionalidade:
- [ ] POST /simulations cria container Docker
- [ ] GET /simulations lista todas
- [ ] GET /simulations/{id} mostra detalhes + logs
- [ ] DELETE /simulations/{id} para container
- [ ] Container para após duration_minutes
- [ ] Containers órfãos limpos ao reiniciar API

Base de Dados:
- [ ] Simulações persistem após restart
- [ ] Status atualiza corretamente (running→expired→stopped)
- [ ] expires_at calculado e usado
- [ ] Ficheiros config temporários limpos

Qualidade:
- [ ] Erros retornam HTTP status corretos
- [ ] Swagger UI funciona e está completo
- [ ] Código sem warnings/erros
- [ ] README.md completo

Demo:
- [ ] factory.json funciona
- [ ] Cliente HTML conecta e mostra dados
- [ ] Script de 7 min ensaiado 3x
- [ ] Vídeo backup gravado
```

### Checklist Fase 2 (antes de migrar para Fase 3)
```
Kubernetes:
- [ ] Pods criados dinamicamente via K8s API
- [ ] ConfigMaps montados corretamente
- [ ] Pods param após activeDeadlineSeconds
- [ ] CronJob limpa Pods expirados

Multi-User:
- [ ] PostgreSQL substituiu SQLite
- [ ] Tabela users existe e funciona
- [ ] JWT authentication funciona
- [ ] Users só vêem suas simulações
- [ ] Rate limiting por user funciona

Robustez:
- [ ] RBAC K8s configurado
- [ ] Secrets geridos corretamente
- [ ] Error handling robusto
- [ ] Documentação atualizada
```

### Checklist Fase 3 (antes de considerar "pronto")
```
Produção:
- [ ] Deploy em cloud pública
- [ ] DNS configurado
- [ ] SSL/TLS ativo
- [ ] Logs agregados (Loki/ELK)
- [ ] Métricas visíveis (Grafana)
- [ ] Alertas configurados

DevOps:
- [ ] CI/CD funcional
- [ ] Testes automatizados
- [ ] Rollback funciona
- [ ] Backups database automáticos

Segurança:
- [ ] Secrets não no Git
- [ ] RBAC mínimo necessário
- [ ] Network policies configuradas
- [ ] Security scan passou
```

---

## 📈 Métricas de Sucesso

### Fase 1 (MVP)
- **Funcionalidade:** 100% dos endpoints funcionam
- **Performance:** API responde < 200ms (P95)
- **Confiabilidade:** 0 crashes durante demo
- **Documentação:** README completo + comentários

### Fase 2 (Kubernetes)
- **Escalabilidade:** Suporta 10+ utilizadores simultâneos
- **Isolamento:** Users não vêem simulações de outros
- **Performance:** 50+ pods criados sem degradação
- **Confiabilidade:** Cleanup 100% eficaz

### Fase 3 (Produção)
- **Uptime:** 99%+ SLA
- **Deploy:** < 5 min do commit ao prod
- **Observability:** Logs e métricas 100% cobertura
- **Segurança:** 0 vulnerabilidades críticas

---

## Próximos Passos Imediatos (Esta Semana)

### Segunda-feira
- [ ] Corrigir health check database
- [ ] Adicionar campo expires_at
- [ ] Implementar cleanup_expired_simulations()
- [ ] Testar: criar simulação 2 min → para sozinha

### Terça-feira
- [ ] Testar: reiniciar API → órfãos limpos
- [ ] Adicionar filtros GET /simulations?status=running
- [ ] Adicionar GET /stats

### Quarta-feira
- [ ] Começar README.md
- [ ] Criar factory.json de exemplo
- [ ] Testar todos endpoints com Postman

### Quinta-feira
- [ ] Cliente HTML básico
- [ ] Testar cliente com simulação real
- [ ] Começar slides apresentação

### Sexta-feira
- [ ] Finalizar slides
- [ ] Ensaiar demo 1x
- [ ] Identificar gaps/bugs

---

## Recursos Úteis

### Documentação Oficial
- FastAPI: https://fastapi.tiangolo.com
- Docker SDK: https://docker-py.readthedocs.io
- SQLAlchemy: https://docs.sqlalchemy.org
- Kubernetes Python: https://github.com/kubernetes-client/python

### Tutoriais
- FastAPI + Docker: https://testdriven.io/blog/fastapi-docker/
- Kubernetes Basics: https://kubernetes.io/docs/tutorials/
- MQTT.js: https://github.com/mqttjs/MQTT.js

### Tools
- Postman: Testar API
- Swagger UI: Documentação automática
- Docker Desktop: Gerir containers
- minikube: Kubernetes local

---

## Conclusão

Este roadmap cobre **12-16 semanas** de desenvolvimento estruturado em 3 fases:

1. **Fase 1 (4 semanas):** MVP funcional para apresentação universitária ← **FOCO ATUAL**
2. **Fase 2 (6 semanas):** Kubernetes + multi-user
3. **Fase 3 (6 semanas):** Produção com CI/CD, monitoring

**Recomendação:** Completar Fase 1 perfeitamente antes de pensar em Fase 2. Um MVP bem executado vale mais que features incompletas.

**Próxima Ação:** Seguir checklist "Próximos Passos Imediatos" acima.