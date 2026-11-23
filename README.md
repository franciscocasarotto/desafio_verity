# Desafio Técnico - Solutions Architect

## Visão Geral

Este repositório contém a solução arquitetural completa para um sistema de controle de fluxo de caixa, desenvolvido como parte do processo seletivo para a posição de Solutions Architect.

A solução foi desenhada considerando um **ambiente corporativo híbrido e multi-cloud** (On-Premises, Azure e GCP), priorizando:
- Soberania de dados e conformidade
- Escalabilidade elástica para picos de carga
- Otimização de custos (FINOPS)
- Resiliência e alta disponibilidade
- Segurança em múltiplas camadas (Defense in Depth)

##  Arquitetura

### Diagrama de Contexto (C4 - Level 1)

             ┌─────────────────┐
             │   Comerciante   │
             └────────┬────────┘
                      │ HTTP
                      ▼
        ┌─────────────────────────┐
        │      API Gateway        │
        │   (auth, rate limit)    │
        └──────┬──────────┬───────┘
               │          │
      ┌────────▼──┐   ┌──▼────────────┐
      │Lançamentos│   │  Consolidado  │
      │  (On-prem)│   │   (Azure)     │
      └─────┬─────┘   └──────▲────────┘
            │                │
            │  publica       │ consome
            ▼                │
      ┌──────────────────────┴─────┐
      │        RabbitMQ            │
      │     (fila durável)         │
      └────────────────────────────┘
            │                │
            ▼                ▼
      ┌──────────┐    ┌──────────┐
      │PostgreSQL│    │ Postgres │
      │ On-prem  │    │ + Redis  │
      └──────────┘    └──────────┘
