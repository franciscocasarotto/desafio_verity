# Arquitetura Alvo — Desafio Verity

## Diagrama C4 — Container (Mermaid, renderiza no GitHub)

```mermaid
graph TB
    subgraph Clientes
        UI[Web/Mobile App Comerciante]
    end
    subgraph Edge
        GW[API Gateway - Rate Limit, JWT, CORS]
    end
    subgraph Aplicacao
        SL[Serviço Lançamentos<br/>FastAPI Hexagonal]
        SC[Serviço Consolidado<br/>FastAPI Hexagonal]
    end
    subgraph Mensageria
        RS[(Redis Streams<br/>lancamentos.events)]
    end
    subgraph Dados
        PG[(PostgreSQL<br/>schema: financeiro)]
        RC[(Redis Cache<br/>consolidado TTL 5min)]
    end

    UI -->|HTTPS + JWT| GW
    GW --> SL
    GW --> SC
    SL --> PG
    SL -->|publish| RS
    RS -->|consume group| SC
    SC --> PG
    SC --> RC
    SC -.->|cache read| RC

    style SL fill:#4CAF50,color:#fff
    style SC fill:#2196F3,color:#fff
    style RS fill:#FF9800,color:#fff
