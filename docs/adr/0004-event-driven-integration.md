# ADR-0004: Integração orientada a eventos via Redis Streams

## Status: Aceito

## Contexto
Os serviços precisam se comunicar sem acoplamento síncrono. Se o serviço de 
consolidado cair, os lançamentos não podem ser perdidos.

## Decisão
Redis Streams com consumer groups (at-least-once delivery).

## Justificativa
| Critério | Redis Streams | RabbitMQ | Kafka |
|----------|---------------|----------|-------|
| Latência | <1ms | ~5ms | ~10ms |
| Complexidade operacional | Baixa | Média | Alta |
| Persistência de eventos | Sim | Sim | Sim |
| Adequado ao escopo | ✅ | ✅ | ❌ overkill |

## Consequências
✅ Desacoplamento temporal (SL não depende de SC estar online)
✅ Replays possíveis (offset por consumer group)
⚠️ Exige idempotência no SC (chave: `lancamento_id + operation`)