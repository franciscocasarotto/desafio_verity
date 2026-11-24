# ADR-0003: PostgreSQL + Redis

## Status: Aceito
## Decisão
PostgreSQL 15 para persistência transacional + Redis 7 para cache e mensageria.

## Justificativa
- **PostgreSQL:** ACID completo (essencial para lançamentos financeiros), JSONB para audit trail, particionamento por data.
- **Redis Streams:** at-least-once delivery, consumer groups, latência <1ms, custo operacional baixo.

## Alternativas rejeitadas
- MongoDB: transações multi-document fracas
- RabbitMQ: complexidade operacional maior para escopo pequeno
- Kafka: overkill para 50 req/s

```markdown

## Diagrama de Fluxo de Dados

```mermaid
graph LR
    subgraph "📝 Escrita (Lançamentos)"
        SL[Serviço Lançamentos]
    end
    
    subgraph "💾 Persistência"
        PG[(PostgreSQL<br/>ACID + JSONB)]
    end
    
    subgraph "⚡ Mensageria"
        RD[(Redis Streams<br/>at-least-once)]
    end
    
    subgraph "📊 Leitura (Consolidado)"
        SC[Serviço Consolidado]
    end
    
    subgraph "🚀 Cache"
        RC[(Redis Cache<br/>TTL 5min)]
    end
    
    SL -->|grava| PG
    SL -->|publica| RD
    RD -->|consome| SC
    SC -->|consulta| PG
    SC -->|cache| RC
    RC -->|serve| SC
    
    style PG fill:#f59e0b,color:#fff
    style RD fill:#ef4444,color:#fff
    style RC fill:#3b82f6,color:#fff