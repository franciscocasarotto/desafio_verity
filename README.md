# Desafio Técnico - Solutions Architect

## Visão Geral

Este repositório contém a solução arquitetural completa para um sistema de controle de fluxo de caixa, desenvolvido como parte do processo seletivo para a posição de Solutions Architect.

Sistema de controle de fluxo de caixa para comerciantes, com dois serviços:
- **Lançamentos**: registra débitos e créditos
- **Consolidado**: calcula o saldo diário

## Como rodar local

Com Docker instalado:

```bash
docker-compose up --build

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
