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
