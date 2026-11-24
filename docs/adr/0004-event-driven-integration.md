# ADR-0004: Integração Assíncrona Event-Driven

## Status: Aceito
## Contexto
RNF-CRIT-01: lançamentos NÃO pode ficar indisponível se consolidado cair.

## Decisão
Comunicação via Redis Streams (at-least-once) com consumer groups.

## Justificativa
| Critério | Redis Streams | RabbitMQ | Kafka |
|----------|---------------|----------|-------|
| Latência | <1ms | ~5ms | ~10ms |
| Complexidade | Baixa | Média | Alta |
| Replay | Sim (offset) | Sim | Sim |
| Adequado escopo | ✅ | ✅ | ❌ |

## Consequências
✅ Desacoplamento temporal (SL não depende de SC online)
✅ Reprocessamento automático ao SC voltar
✅ Atende RNF-CRIT-02 (≤5% perda) via DLQ
⚠️ Exige idempotência no SC (chave: lancamento_id + operation)
