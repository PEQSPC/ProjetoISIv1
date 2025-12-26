# ProjetoISIv1 - Monitorização Industrial com ETL e IoT

[![Documentation](https://img.shields.io/badge/docs-MkDocs-blue)](https://www.mkdocs.org/)
[![Python](https://img.shields.io/badge/Python-3.10+-green.svg)](https://www.python.org/)
[![Node.js](https://img.shields.io/badge/Node.js-18+-green.svg)](https://nodejs.org/)

Este repositório contém o **Trabalho Prático I** da unidade curricular **Integração de Sistemas de Informação (ISI)** - Licenciatura em Engenharia de Sistemas Informáticos (LESI-IPCA) - Ano letivo 2025/26.

## Sobre o Projeto

O **ProjetoISIv1** demonstra a aplicação prática de ferramentas de **ETL (Extract, Transform, Load)** em processos de integração de dados no contexto de monitorização industrial com sensores IoT. O objetivo principal é centralizar, processar e visualizar dados de produção industrial em tempo real.

### Principais Funcionalidades

- Recolha automática de dados via sensores MQTT simulados
- Processamento ETL em tempo real com Node-RED
- Armazenamento persistente em SQLite3
- Enriquecimento de dados via integração com API externa
- Geração automática de relatórios e envio por email
- Dashboard web com visualização em tempo real (React + Material UI)
- Simulador IoT configurável para múltiplos dispositivos

## Estrutura do Projeto

```
ProjetoISIv1/
├── api/                    # API REST para gestão de simulações
├── docs/                   # Documentação completa (MkDocs)
├── mqtt-simulator-master/  # Simulador MQTT IoT
├── node-red/              # Fluxos ETL Node-RED
├── send-email/            # Sistema de relatórios por email
└── mkdocs.yml             # Configuração MkDocs
```

## Documentação

Toda a documentação técnica detalhada está disponível através do **MkDocs**. A documentação inclui:

- Arquitetura do sistema
- Processos ETL
- Configuração de componentes
- Guias de instalação
- Troubleshooting
- Fase 2 - IoT Simulator Platform

### Aceder à Documentação

1. **Instalar dependências MkDocs:**

```bash
# Criar ambiente virtual Python
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

2. **Servir a documentação localmente:**

```bash
mkdocs serve
```

A documentação estará disponível em `http://localhost:8000`

3. **Gerar documentação estática:**

```bash
mkdocs build
```

**Nota:** A biblioteca `mkdocs-pdf-export-plugin` requer dependências do sistema Linux para geração de PDFs. Consulte a [documentação oficial](https://mkdocs-to-pdf.readthedocs.io/en/stable/) para mais informações.

## Quick Start

### Pré-requisitos

- Python 3.10+
- Node.js 18+
- Mosquitto MQTT Broker
- SQLite3

### Instalação Rápida

1. **Clonar o repositório:**

```bash
git clone https://github.com/PEQSPC/ProjetoISIv1.git
cd ProjetoISIv1
```

2. **Configurar componentes:**

Consulte a [documentação de instalação](docs/instalacao.md) para instruções detalhadas de cada componente.

3. **Iniciar o sistema:**

```bash
# Iniciar Mosquitto MQTT Broker
mosquitto -c mosquitto.conf

# Iniciar Node-RED
node-red

# Iniciar simulador IoT
python3 mqtt-simulator-master/mqtt-simulator/main.py

# Iniciar API (Fase 2)
cd api
uvicorn main:app --reload --port 8000
```

## Autores

**Equipa PEQSPC**
Licenciatura em Engenharia de Sistemas Informáticos (LESI)
Instituto Politécnico do Cávado e do Ave (IPCA)

## Repositório

[https://github.com/PEQSPC/ProjetoISIv1](https://github.com/PEQSPC/ProjetoISIv1)

## Licença

Este projeto foi desenvolvido para fins académicos no âmbito da unidade curricular de Integração de Sistemas de Informação (ISI).

---

**Nota:** Para informações detalhadas sobre configuração, arquitetura e utilização, consulte a documentação completa em MkDocs.
