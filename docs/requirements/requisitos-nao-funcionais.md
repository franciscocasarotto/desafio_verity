## Requisitos Não-Funcionais (RNF)

### Criticidade (do enunciado do desafio)
| ID | Requisito | Meta | Como atendemos |
|----|-----------|------|----------------|
| RNF-CRIT-01 | Lançamentos NÃO pode ficar indisponível se consolidado cair | 100% uptime SL | Arquitetura assíncrona via Redis — lançamentos grava e retorna 201 sem esperar consolidado |
| RNF-CRIT-02 | Pico de 50 req/s no consolidado com máx. 5% perda | ≤ 5% perda | Redis Streams com consumer groups (at-least-once delivery) + DLQ |

### Desempenho
| ID | Requisito | Meta |
|----|-----------|------|
| RNF03 | Latência p95 criação lançamento | ≤ 200ms |
| RNF04 | Latência p95 consulta consolidado | ≤ 150ms (cache Redis) |
| RNF05 | Throughput mínimo | 100 req/s por serviço |

### Escalabilidade
| ID | Requisito | Meta |
|----|-----------|------|
| RNF06 | Escalonamento horizontal sem downtime | 1→N réplicas via HPA |
| RNF07 | Cache consolidado TTL 5min | Hit ratio ≥ 80% |

### Disponibilidade & Resiliência
| ID | Requisito | Meta |
|----|-----------|------|
| RNF08 | SLA disponibilidade | 99.5% mensal |
| RNF09 | RPO | ≤ 5 min |
| RNF10 | RTO | ≤ 15 min |
| RNF11 | Circuit breaker entre serviços | Timeout 3s, retry exponencial |

### Segurança
| ID | Requisito | Meta |
|----|-----------|------|
| RNF12 | JWT com expiração 15min | OWASP Top 10 |
| RNF13 | Rede interna isolada (Docker) | Zero Trust |
| RNF14 | Criptografia repouso AES-256 | LGPD |
| RNF15 | Rate limiting 60 req/min | Anti-abuso |

### Observabilidade
| ID | Requisito | Meta |
|----|-----------|------|
| RNF16 | Healthcheck /health e /ready | 100% serviços |
| RNF17 | Métricas Prometheus | /metrics exposto |
| RNF18 | Trace distribuído OpenTelemetry | correlation_id |

### Manutenibilidade
| ID | Requisito | Meta |
|----|-----------|------|
| RNF19 | Cobertura testes ≥ 85% | pytest --cov |
| RNF20 | ADR para cada decisão crítica | 100% |
