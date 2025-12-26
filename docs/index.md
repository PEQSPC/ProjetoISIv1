# ProjetoISIv1 - Monitorização Industrial com ETL e IoT

Bem-vindo à documentação técnica do **ProjetoISIv1**, um sistema completo de monitorização industrial utilizando tecnologias de IoT, ETL e visualização de dados em tempo real.

---

## Introdução

O **ProjetoISIv1** é um trabalho prático desenvolvido no âmbito da Unidade Curricular **Integração de Sistemas de Informação (ISI)** da Licenciatura em Engenharia de Sistemas Informáticos (LESI-IPCA), ano letivo 2025/26.

### Objetivo Principal

Aplicar e experimentar **ferramentas de ETL (Extract, Transform, Load)** em processos de integração de dados no contexto de **monitorização industrial com sensores IoT**, demonstrando a integração prática de sistemas heterogéneos para recolha, processamento e visualização de dados de produção.

---

## Contexto e Problema

### Desafio Identificado

A recolha de dados das estações de produção industrial apresentava limitações significativas:

- **Recolha manual e isolada** de dados de cada estação
- **Ausência de monitorização em tempo real** dos processos produtivos
- **Dificuldade na identificação de anomalias** e gargalos de produção
- **Falta de integração** entre métricas de produção, paragem, stock e defeitos
- **Impossibilidade de análise centralizada** e geração de relatórios automáticos

### Solução Proposta

Desenvolvimento de um sistema integrado que:

1. Centraliza a recolha de dados através de sensores IoT
2. Processa e transforma dados em tempo real
3. Armazena informação de forma estruturada
4. Enriquece dados com fontes externas
5. Gera relatórios e visualizações automáticas

---

## Objetivos do Projeto

### Objetivos Técnicos

- **Centralização de Dados**: Criar um repositório único para dados de produção, stock e paragens
- **Automação da Recolha**: Implementar recolha automática via sensores MQTT
- **Processamento ETL**: Normalizar, validar e transformar dados antes do armazenamento
- **Enriquecimento de Dados**: Integrar dados externos via API REST
- **Geração de Relatórios**: Criar relatórios automáticos e envio por email
- **Visualização em Tempo Real**: Desenvolver dashboard web interativo

### Competências Desenvolvidas

- Configuração e utilização de brokers MQTT
- Desenvolvimento de fluxos ETL com Node-RED
- Integração de APIs REST
- Modelação e gestão de bases de dados
- Desenvolvimento de interfaces web com React
- Automação de processos com Python

---

## Estrutura da Documentação

Esta documentação está organizada nas seguintes secções:

### Documentação Técnica

| Secção | Descrição |
|--------|-----------|
| [Arquitetura Técnica](arquitetura.md) | Visão geral dos componentes e fluxo de dados |
| [Processos ETL](etl-processos.md) | Detalhes dos processos de extração, transformação e carregamento |
| [Base de Dados](base-de-dados.md) | Estrutura e modelação da base de dados SQLite |
| [Integração com API](api-integracao.md) | Integração com APIs externas para enriquecimento de dados |

### Guias Práticos

| Secção | Descrição |
|--------|-----------|
| [Instalação](instalacao.md) | Instruções detalhadas de instalação e configuração |
| [Simulador de Sensores](simulador/how_to_use_simulator.md) | Como configurar e utilizar o simulador IoT |
| [Dashboard](dashboard.md) | Informação sobre o dashboard de visualização |
| [Relatórios e Emails](relatorios-emails.md) | Sistema de geração e envio de relatórios |

### Recursos Adicionais

| Secção | Descrição |
|--------|-----------|
| [Troubleshooting](troubleshooting.md) | Resolução de problemas comuns |
| [Conclusão](conclusao.md) | Resultados e trabalhos futuros |
| [Fase 2 - IoT Simulator Platform](fase-2/roadmap-Iot-Simulator-Platform.md) | Roadmap e melhorias futuras |

---

## Stack Tecnológica

O projeto utiliza as seguintes tecnologias:

### Backend e Processamento

- **Python 3.10+**: Scripts de simulação, integração e automação
- **Node-RED**: Motor ETL para processamento de dados
- **SQLite3**: Base de dados relacional
- **Mosquitto MQTT**: Broker de mensagens IoT

### Frontend e Visualização

- **React 18+**: Framework de desenvolvimento web
- **Material-UI**: Biblioteca de componentes UI
- **Grafana**: Visualização de dados (opcional)

### DevOps e Ferramentas

- **Docker**: Containerização de serviços
- **MkDocs**: Geração de documentação
- **Git**: Controlo de versões

---

## Sobre o Projeto

**Autores**: Equipa PEQSPC
**Curso**: Licenciatura em Engenharia de Sistemas Informáticos (LESI)
**Instituição**: Instituto Politécnico do Cávado e do Ave (IPCA)
**Unidade Curricular**: Integração de Sistemas de Informação (ISI)
**Ano Letivo**: 2025/26
**Repositório**: [https://github.com/PEQSPC/ProjetoISIv1](https://github.com/PEQSPC/ProjetoISIv1)

---

## Navegação Rápida

Recomendamos seguir a documentação pela seguinte ordem:

1. **Começar**: [Arquitetura Técnica](arquitetura.md) - Compreender a visão geral do sistema
2. **Instalar**: [Instalação](instalacao.md) - Configurar o ambiente de desenvolvimento
3. **Configurar**: [Simulador de Sensores](simulador/how_to_use_simulator.md) - Executar o simulador IoT
4. **Explorar**: [Dashboard](dashboard.md) - Visualizar dados em tempo real
5. **Aprofundar**: [Processos ETL](etl-processos.md) - Entender o processamento de dados

---

**Nota**: Esta documentação é mantida atualizada com as últimas alterações do projeto. Para questões ou sugestões, consulte o repositório GitHub.
