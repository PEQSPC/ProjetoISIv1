# ProjetoISIv1 - Monitorização Industrial com ETL e IoT

Bem-vindo à documentação do **ProjetoISIv1**, um sistema de monitorização industrial que evoluiu para uma plataforma de simulação IoT.

---

## Sobre o Projeto

Este projeto nasceu como trabalho prático da UC de **Integração de Sistemas de Informação (ISI)** da LESI-IPCA e cresceu para algo maior.

### Fase 1: Trabalho Académico (Out-Dez 2024)
Sistema de monitorização industrial com recolha automática de dados de estações de produção via MQTT, processamento ETL em Node-RED, e visualização em tempo real.

**Objetivo**: Aplicar conceitos de integração de sistemas e ETL num contexto industrial prático.

### Fase 2: Plataforma IoT Simulator (Jan 2025+)
Evolução para uma plataforma comercial que permite a programadores testar aplicações IoT sem hardware físico, criando sensores virtuais sob demanda.

**Objetivo**: Validar viabilidade comercial de uma solução SaaS para simulação IoT.

**Lê mais**: [Contexto e Evolução do Projeto](projeto-contexto.md)

---

## Stack Tecnológica

**Backend**: Python, Node-RED, SQLite, Mosquitto MQTT  
**Frontend**: React, Material-UI  
**DevOps**: Docker, FastAPI (Fase 2)

---

## Estrutura da Documentação

### Conceito e Arquitetura
- [Contexto do Projeto](projeto-contexto.md) - Evolução Fase 1 → Fase 2
- [Arquitetura Técnica](arquitetura.md) - Componentes e fluxo de dados
- [Processos ETL](etl-processos.md) - Pipeline de dados

### Dados e Integrações
- [Base de Dados](base-de-dados.md) - Schema e queries principais
- [Integração API](api-integracao.md) - Preços de peças em tempo real
- [Azure IoT Hub](azure-iot-integracao.md) - Telemetria para cloud
- [Relatórios e Emails](relatorios-emails.md) - Automação de relatórios

### Implementação
- [Instalação](instalacao.md) - Setup do ambiente
- [Dashboard](dashboard.md) - Interface de visualização
- [Troubleshooting](troubleshooting.md) - Problemas comuns

### Futuro
- [Fase 2 - IoT Simulator Platform](fase-2/roadmap-Iot-Simulator-Platform.md) - Roadmap comercial

---

## Quick Start

```bash
# 1. Clonar repositório
git clone https://github.com/PEQSPC/ProjetoISIv1
cd ProjetoISIv1

# 2. Iniciar broker MQTT
mosquitto -c mosquitto.conf

# 3. Iniciar Node-RED
node-red

# 4. Executar simulador
python simulador/mqtt_publisher.py

# 5. Ver dashboard
cd dashboard && npm start
```

Detalhes completos em [Instalação](instalacao.md).

---

## O Problema Resolvido

**Antes**: Recolha manual de dados, sem visão integrada, dificuldade em identificar problemas.

**Depois**: Monitorização automática em tempo real, alertas automáticos, relatórios por email, dashboard interativo.

**Métricas**: Produção, paragens, stock, defeitos, eficiência (OEE).

---

## Navegação Recomendada

**Novo no projeto?**
1. [Contexto do Projeto](projeto-contexto.md) - Entende a visão
2. [Instalação](instalacao.md) - Configura o ambiente
3. [Dashboard](dashboard.md) - Vê os dados ao vivo

**Implementador técnico?**
1. [Arquitetura](arquitetura.md) - Compreende o sistema
2. [ETL](etl-processos.md) - Fluxos de processamento
3. [Base de Dados](base-de-dados.md) - Modelo de dados

**Interessado no futuro?**
1. [Fase 2 Roadmap](fase-2/roadmap-Iot-Simulator-Platform.md) - Plataforma comercial

---

## Informação do Projeto

**Instituição**: IPCA - Instituto Politécnico do Cávado e do Ave  
**Curso**: Licenciatura em Engenharia de Sistemas Informáticos (LESI)  
**UC**: Integração de Sistemas de Informação (ISI)  
**Ano Letivo**: 2024/25  
**Equipa**: PEQSPC  
**Repositório**: [github.com/PEQSPC/ProjetoISIv1](https://github.com/PEQSPC/ProjetoISIv1)

---

**Nota**: Esta documentação cobre ambas as fases do projeto. Para detalhes da Fase 2 (plataforma comercial), consulta o [roadmap específico](fase-2/roadmap-Iot-Simulator-Platform.md).