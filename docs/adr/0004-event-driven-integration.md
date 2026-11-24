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


```markdown

## Diagrama de Sequência do Evento Assíncrono

```mermaid
sequenceDiagram
    participant SL as 📝 Lançamentos
    participant RD as ⚡ Redis Streams
    participant SC as 📊 Consolidado
    
    SL->>RD: Publish LancamentoRegistrado
    Note over RD: Evento persistido<br/>(at-least-once)
    RD->>SC: Deliver Event
    SC->>SC: Processar e calcular saldo
    SC->>RD: Ack (confirmar consumo)
    
    Note over SL,SC: Desacoplamento temporal<br/>SL não espera SC