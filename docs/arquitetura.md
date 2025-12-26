# Arquitetura Técnica do Projeto

A arquitetura técnica do **ProjetoISIv1** suporta todo o ciclo de recolha, transformação e visualização dos dados industriais.

---

## Componentes Principais

### 1. Publisher (Simulador MQTT em Python)

- Gera dados de produção, stock, paragens e defeitos.
- Publica mensagens MQTT em tópicos por estação.

### 2. Broker MQTT — Eclipse Mosquitto

- Atua como intermediário entre sensores (publishers) e Node-RED (subscriber).
- Porta padrão: `1883`.

### 3. Node-RED (ETL)

- Recebe dados MQTT.
- Processa e acumula valores.
- Guarda resultados em **SQLite3**.
- Envia relatórios e aciona scripts Python.

### 4. Base de Dados SQLite3

- Armazena dados acumulados e históricos.
- Tabelas: `estacoes`, `dados_acumulados`, `relatorios`, `produtos`.

### 5. Enriquecimento via API

- Obtém **preços das peças** e cruza com dados de produção.
- Utiliza **expressões regulares (Regex)** para filtrar os produtos relevantes.

### 6. Python Reporting

- Gera relatórios automáticos sobre margens e desempenho.
- Envia por email.

### 7. Dashboard (React + Material UI)

- Exibe produção, paragens e eficiência em tempo real.
- Interface moderna criada com UI Builder.

---

## Fluxo Global de Dados

```mermaid
graph TD
  A[Sensores Python] --> B[Broker MQTT (Mosquitto)]
  B --> C[Node-RED ETL]
  C --> D[SQLite3]
  D --> E[API Preços]
  D --> F[Python Reporting]
  F --> G[Email Automático]
  D --> H[Dashboard React]
```
