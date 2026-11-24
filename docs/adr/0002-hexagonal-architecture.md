# ADR-0002: Arquitetura Hexagonal (Ports & Adapters)

## Status: Aceito
## Contexto
Domínio financeiro crítico com regras que mudam frequentemente.

## Decisão
Hexagonal em ambos os serviços.

## Trade-offs
| Padrão | Prós | Contras | Decisão |
|--------|------|---------|---------|
| Monolito MVC | Simples | Acoplamento | ❌ |
| Microsserviços puros | Escalável | Overhead | ❌ |
| **Hexagonal** | **Testável, isolado** | Boilerplate | **✅** |
| CQRS puro | Separação leitura/escrita | Complexidade | ❌ |

## Consequências
✅ Testes unitários sem mock de banco
✅ PostgreSQL trocável por SQLite em testes
✅ Adapters de eventos isolados (Redis → Kafka sem tocar domínio)
⚠️ Exige disciplina para não vazar dependências ao domínio
