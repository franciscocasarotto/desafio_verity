# Requisitos Não-Funcionais (RNF)

## Desempenho
| ID    | Requisito | Meta |
|-------|-----------|------|
| RNF01 | Latência p95 de criação de lançamento | ≤ 200ms |
| RNF02 | Latência p95 de consulta de consolidado | ≤ 150ms (cache Redis) |
| RNF03 | Throughput mínimo | 100 req/s por serviço |

## Escalabilidade
| ID    | Requisito | Meta |
|-------|-----------|------|
| RNF04 | Escalonamento horizontal sem downtime | 1→N réplicas |
| RNF05 | Cache de consolidado com TTL de 5min | Hit ratio ≥ 80% |

## Disponibilidade & Resiliência
| ID    | Requisito | Meta |
|-------|-----------|------|
| RNF06 | SLA de disponibilidade | 99.5% mensal |
| RNF07 | Recovery Point Objective (RPO) | ≤ 5 min |
| RNF08 | Recovery Time Objective (RTO) | ≤ 15 min |
| RNF09 | Circuit breaker para comunicação entre serviços | Timeout 3s, retry exponencial |

## Segurança
| ID    | Requisito | Meta |
|-------|-----------|------|
| RNF10 | Autenticação JWT com expiração de 15min | OWASP Top 10 |
| RNF11 | Comunicação interna via rede isolada (Docker internal) | Zero trust |
| RNF12 | Dados em repouso criptografados (PostgreSQL) | AES-256 |
| RNF13 | Rate limiting por IP | 60 req/min |
| RNF14 | Logs estruturados sem dados sensíveis (PII) | LGPD |

## Observabilidade
| ID    | Requisito | Meta |
|-------|-----------|------|
| RNF15 | Healthcheck em todos os serviços | `/health` e `/ready` |
| RNF16 | Métricas Prometheus expostas | `/metrics` |
| RNF17 | Trace distribuído (OpenTelemetry) | Correlation ID por request |

## Manutenibilidade
| ID    | Requisito | Meta |
|-------|-----------|------|
| RNF18 | Cobertura de testes ≥ 85% | pytest --cov |
| RNF19 | Documentação ADR para cada decisão | 100% decisões críticas |