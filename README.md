# ProjetoISIv1 → IoT Simulator Platform

[![Documentation](https://img.shields.io/badge/docs-MkDocs-blue)](https://www.mkdocs.org/)
[![Python](https://img.shields.io/badge/Python-3.10+-green.svg)](https://www.python.org/)
[![Node.js](https://img.shields.io/badge/Node.js-18+-green.svg)](https://nodejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com/)
[![MQTT Simulator Fork](https://img.shields.io/badge/MQTT%20Simulator%20Fork-blue)](https://github.com/DamascenoRafael/mqtt-simulator)
[![License](https://img.shields.io/badge/license-Academic-orange.svg)](LICENSE)

Sistema de monitorização industrial que evoluiu para uma **plataforma de simulação IoT** comercial.

---

## Sobre o Projeto

Este projeto começou como trabalho académico da UC **Integração de Sistemas de Informação (ISI)** da LESI-IPCA e evoluiu para uma potencial solução SaaS.

### Fase 1: Monitorização Industrial (Out-Dez 2024) ✅

Sistema completo de monitorização com:
- Sensores IoT simulados (MQTT)
- Pipeline ETL (Node-RED)
- Base de dados (SQLite)
- Dashboard web (React)
- Relatórios automáticos (Email)
- Integração Azure IoT Hub

**Status**: Completo e documentado

### Fase 2: IoT Simulator Platform (Jan 2025+) 🚧

Plataforma SaaS para criar sensores IoT virtuais sob demanda:
- API REST (FastAPI)
- Orquestração Kubernetes
- Multi-tenancy isolado
- Pay-as-you-go pricing
- PostgreSQL + Redis

**Status**: Em desenvolvimento (MVP funcional)

**Lê mais**: [Contexto e Evolução](docs/projeto-contexto.md)

---

## Estrutura do Repositório

```
ProjetoISIv1/
├── docs/                      # Documentação completa (MkDocs)
│   ├── index.md              # Página principal
│   ├── projeto-contexto.md   # História Fase 1 → Fase 2
│   ├── arquitetura.md        # Arquitetura técnica
│   ├── azure-iot-integracao.md  # Azure IoT Hub
│   └── fase-2/               # Documentação Fase 2
│
├── mqtt-simulator/           # Simulador IoT (Fase 1)
│   ├── main.py              # Publisher MQTT
│   └── config.json          # Configuração sensores
│
├── node-red/                # Fluxos ETL (Fase 1)
│   ├── flows.json           # Versão atual
│   └── settings.js          # Configuração Node-RED
│
├── api/                     # API REST (Fase 2)
│   ├── main.py              # FastAPI application
│   ├── docker_manager.py    # Gestão containers
│   └── requirements.txt     # Dependências Python
│
├── dashboard/               # Frontend React (Fase 1)
│   └── src/                # Componentes React
│
├── send-email/             # Relatórios automáticos
│   └── report_generator.py
│
└── mkdocs.yml             # Configuração documentação
```

---

## Quick Start

### Pré-requisitos

**Fase 1 (Monitorização)**:
- Python 3.10+
- Node.js 18+
- Mosquitto MQTT Broker
- SQLite3

**Fase 2 (Plataforma)** adiciona:
- Docker / Kubernetes
- PostgreSQL
- Redis

### Instalação Fase 1

```bash
# 1. Clonar repositório
git clone https://github.com/PEQSPC/ProjetoISIv1.git
cd ProjetoISIv1

# 2. Instalar dependências Python
pip install -r requirements.txt

# 3. Iniciar Mosquitto MQTT
mosquitto -c mosquitto.conf

# 4. Iniciar Node-RED
node-red

# 5. Executar simulador IoT
python mqtt-simulator/main.py

# 6. Aceder dashboard (se instalado)
cd dashboard && npm start
```

### Instalação Fase 2 (MVP Local)

```bash
# 1. Instalar dependências API
cd api
pip install -r requirements.txt

# 2. Iniciar API FastAPI
uvicorn main:app --reload --port 8000

# 3. Criar simulação via API
curl -X POST http://localhost:8000/simulations \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test-sim",
    "config": {
      "topic": "test/sensor",
      "interval": 60
    }
  }'

# 4. Listar simulações
curl http://localhost:8000/simulations
```

**Detalhes completos**: [Documentação de Instalação](docs/instalacao.md)

---

## Documentação

A documentação técnica completa está disponível via **MkDocs**:

### Aceder Localmente

```bash
# Instalar MkDocs
pip install mkdocs mkdocs-material

# Servir documentação
mkdocs serve

# Aceder: http://localhost:8000
```

### Documentos Principais

| Documento | Descrição |
|-----------|-----------|
| [index.md](docs/index.md) | Visão geral e navegação |
| [projeto-contexto.md](docs/projeto-contexto.md) | História Fase 1 → Fase 2 |
| [arquitetura.md](docs/arquitetura.md) | Arquitetura técnica completa |
| [base-de-dados.md](docs/base-de-dados.md) | Schema SQLite e queries |
| [azure-iot-integracao.md](docs/azure-iot-integracao.md) | Azure IoT Hub integration |
| [api-integracao.md](docs/api-integracao.md) | API de preços (Node-RED) |
| [relatorios-emails.md](docs/relatorios-emails.md) | Sistema de relatórios |
| [dashboard.md](docs/dashboard.md) | Frontend React |
| [Fase 2 Roadmap](docs/fase-2/roadmap-Iot-Simulator-Platform.md) | Plataforma comercial |

---

## Stack Tecnológica

### Fase 1 (Académico)

| Camada | Tecnologia |
|--------|-----------|
| **IoT Simulation** | Python, paho-mqtt |
| **Message Broker** | Mosquitto MQTT |
| **ETL Processing** | Node-RED |
| **Database** | SQLite3 |
| **Cloud Integration** | Azure IoT Hub |
| **Frontend** | React 18, Material-UI |
| **Reporting** | Python (smtplib) |

### Fase 2 (Comercial)

| Camada | Tecnologia |
|--------|-----------|
| **API** | FastAPI, Uvicorn |
| **Orchestration** | Kubernetes (K8s) |
| **Database** | PostgreSQL |
| **Cache** | Redis |
| **Containers** | Docker |
| **Monitoring** | Prometheus, Grafana |

---

## Contexto Académico

**Instituição**: Instituto Politécnico do Cávado e do Ave (IPCA)  
**Curso**: Licenciatura em Engenharia de Sistemas Informáticos (LESI)  
**UC**: Integração de Sistemas de Informação (ISI)  
**Ano Letivo**: 2024/25  
**Equipa**: PEQSPC

**Nota**: A Fase 1 foi desenvolvida como trabalho académico. A Fase 2 é uma evolução independente focada em viabilidade comercial.

---

## Recursos

- **Repositório**: [github.com/PEQSPC/ProjetoISIv1](https://github.com/PEQSPC/ProjetoISIv1)
- **Documentação Online**: [Github Page](https://peqspc.github.io/ProjetoISIv1/)

---

## Métricas do Projeto

### Fase 1 (Completa)
- ✅ Simulador MQTT funcional
- ✅ 15+ Node-RED flows
- ✅ SQLite com 4 tabelas principais
- ✅ Dashboard React com 5 componentes
- ✅ Sistema de relatórios automáticos
- ✅ Azure IoT Hub integration
- ✅ Documentação completa (20+ páginas)

### Fase 2 (Em Desenvolvimento)
- ✅ FastAPI REST API (6 endpoints)
- ✅ Docker container management
- ✅ Error handling robusto
- ✅ SQLite metadata persistence
- 🚧 Transição para Kubernetes
- 🚧 PostgreSQL migration
- 🚧 Customer validation (landing page)
- 📋 Load testing
- 📋 Production deployment

---

## Contribuir

Este é um projeto académico em evolução. Contribuições, sugestões e feedback são bem-vindos!

### Para a Fase 1 (Monitorização)
- Melhorias no simulador IoT
- Novos flows Node-RED
- Dashboards adicionais
- Documentação adicional

### Para a Fase 2 (Plataforma)
- Testing e QA
- Documentação de API
- Casos de uso reais
- Feedback sobre pricing

---

## Licença

Projeto desenvolvido para fins académicos. A Fase 2 (plataforma comercial) está em processo de definição de licenciamento.

---

## Contacto

Para questões sobre o projeto académico (Fase 1), consulte o repositório GitHub.  
Para questões sobre a plataforma comercial (Fase 2), contacte via Issues ou Discussions.

---

**Última atualização**: Dezembro 2024  
**Versão**: 2.0 (Fase 1 completa + Fase 2 MVP)