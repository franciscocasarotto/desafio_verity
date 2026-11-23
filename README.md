# Desafio Técnico - Solutions Architect

## 📋 Visão Geral

Este repositório contém a solução arquitetural completa para um sistema de controle de fluxo de caixa, desenvolvido como parte do processo seletivo para a posição de Solutions Architect.

A solução foi desenhada considerando um **ambiente corporativo híbrido e multi-cloud** (On-Premises, Azure e GCP), priorizando:
- Soberania de dados e conformidade
- Escalabilidade elástica para picos de carga
- Otimização de custos (FINOPS)
- Resiliência e alta disponibilidade
- Segurança em múltiplas camadas (Defense in Depth)

## 🏗️ Arquitetura

### Diagrama de Contexto (C4 - Level 1)

```mermaid
graph TB
    User[Comerciante] -->|HTTPS| APIGW[API Gateway]
    APIGW --> SVC1[Serviço de Lançamentos]
    APIGW --> SVC2[Serviço de Consolidado]
    
    SVC1 --> DB1[(PostgreSQL<br/>On-Premises)]
    SVC2 --> DB2[(PostgreSQL<br/>Azure)]
    SVC2 --> CACHE[(Redis Cache<br/>Azure)]
    
    SVC1 -.->|Publica Eventos| MQ[RabbitMQ<br/>Azure]
    MQ -.->|Consome Eventos| SVC2
    
    SVC2 -.->|DR / Analytics| GCP[GCP<br/>BigQuery]
    
    style DB1 fill:#ff9999
    style DB2 fill:#99ccff
    style GCP fill:#ffcc99
