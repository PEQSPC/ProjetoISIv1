# ProjetoISIv1 — Monitorização Industrial com ETL e IoT

Para entender todos os detalhes técnicos e de configuração do projeto, lê toda a documentação disponível no site gerado pelo **MkDocs**.

---

## Introdução

O **ProjetoISIv1** é um trabalho prático da Unidade Curricular **Integração de Sistemas de Informação (ISI)** — Licenciatura em Engenharia de Sistemas Informáticos (2025/26).  
O objetivo principal é aplicar e experimentar **ferramentas de ETL (Extract, Transform, Load)** em processos de integração de dados no contexto de **monitorização industrial com sensores IoT**.

---

## Problema

A recolha de dados das estações de produção era feita manualmente e de forma isolada, o que impedia:

- A **monitorização em tempo real**;
- A identificação de **anomalias**;
- A integração e análise de métricas de **produção, paragem, stock e defeitos**.

---

## Objetivos

- Centralizar dados de produção, stock e paragens num repositório único;  
- Automatizar a recolha de dados via **sensores MQTT**;  
- Normalizar e validar dados antes do armazenamento;  
- Enriquecer as leituras com **dados externos via API**;  
- Gerar relatórios automáticos e enviar por email;  
- Visualizar indicadores em tempo real com **React + UI Builder + Grafana**.

---

## Estrutura da Documentação

- [Arquitetura Técnica](arquitetura.md)
- [Processos ETL](etl-processos.md)
- [Integração com API](api-integracao.md)
- [Base de Dados](base-de-dados.md)
- [Simulador de Sensores](simulador/how_to_use_simulator.md)
- [Dashboard](dashboard.md)
- [Relatórios e Emails](relatorios-emails.md)
- [Instalação](instalacao.md)
- [Conclusão](conclusao.md)
- [Fase-2](fase-2/roadmap-Iot-Simulator-Platform.md)

## Sobre o Projeto

- **Nome dos Autores:** PEQSPC
- **Curso e unidade curricular** LESI-IPCA ISI(Integracao de Sistemas de Informaçao)
- **Ano letivo (2025/26)**
- **Link para o repositório Git** [Github](https://github.com/PEQSPC/ProjetoISIv1)
