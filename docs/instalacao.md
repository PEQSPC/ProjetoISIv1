# ⚙️ Pré-requisitos e Instalação

Esta secção descreve as dependências necessárias e o processo de instalação do sistema de **Monitorização Industrial com IoT e ETL**, incluindo a configuração dos componentes MQTT, Node-RED, SQLite, React UI e automação com Python.

## 🧩 Pré-requisitos

Antes de executar o projeto, certifica-te de que tens as seguintes ferramentas instaladas:

### 🔸 Sistema Base

- **Python 3.10+** — para scripts de simulação, integração com API e envio de emails  
- **Node.js 18+** — para execução da interface React e Node-RED  
- **npm ou yarn** — gestor de pacotes JavaScript  
- **SQLite3** — para armazenamento local dos dados processados  
- **Mosquitto MQTT Broker** — para gerir a comunicação entre sensores (publishers) e consumidores (subscribers)  
- **Git** — para controlo de versões e clonagem do repositório  

### 🔸 Bibliotecas Python

Instala as bibliotecas necessárias:

```bash
pip install paho-mqtt requests smtplib sqlite3
```

### 🔸 Dependências Node.js

```bash
npm install @mui/material @emotion/react @emotion/styled axios
```

### 🔸 Node-RED

Instala o Node-RED globalmente:

```bash
npm install -g node-red
```

Depois, inicia com:

```bash
node-red
```

### 🔸Comandos Git

[Geeks git Commands](https://www.geeksforgeeks.org/git/working-on-git-bash/)

### 🔸Gerar Documentação com MkDocs

```bash
pip install mkdocs mkdocs-material
mkdocs serve
```
