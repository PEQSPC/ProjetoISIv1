# Contexto e Evolução do Projeto

Esta página explica a jornada do ProjetoISIv1 desde um trabalho académico até uma potencial plataforma comercial.

---

## Fase 1: Trabalho Académico ISI (Out-Dez 2024)

### Objetivo Original

Aplicar conceitos de **Integração de Sistemas de Informação** num cenário prático de monitorização industrial, focando em processos ETL e comunicação IoT.

### Cenário Implementado

Sistema de monitorização de linha de produção com 3 estações que reportam:
- Produção (peças fabricadas)
- Stock (inventário atual)
- Paragens (tempo de inatividade)
- Defeitos (peças com problemas)

### Arquitetura Fase 1

```
Sensores Simulados (Python MQTT)
         ↓
  Broker MQTT (Mosquitto)
         ↓
  Node-RED (ETL Pipeline)
         ↓
    SQLite Database
         ↓
  Dashboard React + Relatórios Email
```

### Componentes Desenvolvidos

1. **Simulador IoT** - Gera dados sintéticos de sensores via MQTT
2. **Node-RED Flows** - Processa dados (adiciona timestamps, acumula métricas)
3. **Integração API** - Enriquece dados com preços de peças externas
4. **Base de Dados** - Armazena histórico de produção
5. **Relatórios Automáticos** - Python scripts enviam emails com KPIs
6. **Dashboard Web** - Visualização em tempo real (React + Material-UI)

### Aprendizagens Chave

**Técnicas**:
- Comunicação MQTT em ambiente industrial
- Padrão publish-subscribe para desacoplamento
- ETL com Node-RED (Extract-Transform-Load)
- Sidecar pattern para isolamento de simulações
- Persistência de dados em SQLite

**Conceituais**:
- IoT testing requer simuladores robustos
- Existe gap no mercado de simulação IoT acessível
- Arquitetura local funciona mas não escala para produção
- Necessidade de multi-tenancy e isolamento

### Limitações Identificadas

- SQLite não adequado para produção multi-utilizador
- Docker local não permite acesso remoto/partilhado
- Falta de autenticação e gestão de utilizadores
- Impossível escalar para múltiplos clientes simultâneos
- Sem API REST para gestão programática

---

## Transição: Da Monitorização à Simulação

### Insight Crítico

Durante o desenvolvimento, percebemos:

> "Se conseguimos **simular sensores** para testar nosso sistema de monitorização, outros programadores também precisam dessa capacidade. Mas pagar €500+/mês por IoTIFY ou Bevywise não faz sentido para startups."

### Oportunidade de Mercado

**Problema Real**: Programadores precisam testar apps IoT sem comprar hardware.  
**Soluções Existentes**: Caras (€500+/mês) ou complexas (AWS IoT Device Simulator).  
**Nossa Proposta**: Simulação IoT simples e acessível, pay-as-you-go.

**Mercado**: €714B de IoT em 2025, startups e consultoras são target inicial.

---

## Fase 2: IoT Simulator Platform (Jan 2025+)

### Visão

Plataforma SaaS que permite criar sensores IoT virtuais via API REST, eliminando necessidade de hardware para testes e desenvolvimento.

### Transformações Necessárias

| Aspecto | Fase 1 (Académico) | Fase 2 (Comercial) |
|---------|-------------------|-------------------|
| **Deploy** | Docker local | Kubernetes cloud |
| **DB** | SQLite | PostgreSQL |
| **API** | Inexistente | FastAPI REST |
| **Auth** | Nenhuma | JWT tokens |
| **Preço** | Gratuito | Pay-as-you-go |
| **Multi-tenant** | Não | Sim (pods isolados) |
| **Escala** | 1 utilizador | Centenas |

### Nova Arquitetura (Fase 2)

```
User Request → FastAPI
              ↓
         PostgreSQL (metadata)
              ↓
    Kubernetes Orchestrator
              ↓
   [Pod 1]  [Pod 2]  [Pod N]
   MQTT+Sim MQTT+Sim MQTT+Sim
              ↓
    User Application (test)
```

**Conceito-chave**: Cada simulação corre num pod isolado com MQTT broker + simulador próprios.

### Funcionalidades Planeadas

**MVP (3 meses)**:
- Criar/parar simulações via API
- Configurar sensores (tipo, frequência, dados)
- MQTT isolado por simulação
- Monitorização básica de recursos
- Pay-as-you-go €0.10/hora

**Pós-MVP**:
- Templates de sensores pré-configurados
- Webhooks para eventos
- Simulação de cenários complexos
- Dashboard de gestão de simulações
- Integrações (Azure IoT Hub, AWS IoT Core)

### Roadmap Técnico

Ver detalhes completos em [Fase 2 Roadmap](fase-2/roadmap-Iot-Simulator-Platform.md).

**Q1 2025**: MVP funcional, validação de clientes (10 early adopters)  
**Q2 2025**: Beta pública, landing page, primeiros clientes pagantes  
**Q3 2025**: Produção estável, features avançadas  
**Q4 2025**: Escala para 100+ utilizadores

---

## Como a Fase 1 Informou a Fase 2

### Validações Técnicas

1. **Sidecar pattern funciona** - Cada simulação isolada num container
2. **MQTT é protocolo certo** - Amplamente adotado em IoT
3. **Simplicidade vende** - Configuração JSON simples é suficiente
4. **Cleanup automático é crítico** - Simulações devem expirar automaticamente

### Decisões Arquiteturais

Da experiência Fase 1, decidimos:

- **Kubernetes em vez de Docker Compose** - Melhor orquestração
- **PostgreSQL em vez de SQLite** - Suporta concorrência
- **FastAPI em vez de Node-RED** - Mais controlo programático
- **Redis para rate limiting** - Evitar abuso da API
- **Prometheus/Grafana** - Monitorização desde o início

### Lições de Produto

**O que funcionou**:
- Configuração via JSON é intuitiva
- Dados sintéticos realistas são valiosos
- Visualização em tempo real é esperada

**O que faltou**:
- Gestão de múltiplas simulações
- Autenticação e billing
- API para automação
- Templates reutilizáveis

---

## Estado Atual (Dez 2024)

### Fase 1: ✅ Completa

- Código funcional e documentado
- Apresentação académica aprovada
- Repositório público disponível

### Fase 2: 🚧 Em Desenvolvimento

**Completado**:
- Pesquisa de mercado (€714B TAM, gap identificado)
- Arquitetura técnica definida
- MVP com FastAPI + Docker funcionando
- Error handling robusto implementado

**Em Progresso**:
- Transição para Kubernetes
- Sistema de billing
- Landing page para validação

**Próximos Passos**:
- Entrevistas com potenciais clientes
- Load testing e isolamento
- Deploy em cloud provider
- Beta privada com early adopters

---

## Recursos Relacionados

**Fase 1**:
- [Arquitetura Técnica](arquitetura.md)
- [Node-RED Flows](etl-processos.md)
- [Dashboard](dashboard.md)

**Fase 2**:
- [IoT Simulator Platform Roadmap](fase-2/roadmap-Iot-Simulator-Platform.md)
- Repositório API (em construção)
- Landing Page (em construção)

---

## Conclusão

O ProjetoISIv1 começou como exploração académica de ETL e IoT, mas revelou uma oportunidade real de mercado. A experiência técnica da Fase 1 validou conceitos fundamentais que agora evoluem para uma plataforma comercial viável.

**Fase 1 ensinou-nos** como construir sistemas IoT integrados.  
**Fase 2 aplica esse conhecimento** para resolver um problema real de mercado.

Esta documentação serve ambas as fases, mantendo o histórico académico enquanto suporta o desenvolvimento comercial.