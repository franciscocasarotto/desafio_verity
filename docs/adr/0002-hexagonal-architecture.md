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

```markdown

## Diagrama da Arquitetura Hexagonal

```mermaid
graph TB
    subgraph "🌐 Camada Externa (Adapters)"
        HTTP[HTTP/FastAPI]
        DB[PostgreSQL]
        EVT[Redis Streams]
    end
    
    subgraph "🔌 Ports (Interfaces)"
        PORT_IN[Input Ports<br/>Use Cases]
        PORT_OUT[Output Ports<br/>Repositories]
    end
    
    subgraph "🎯 Domain (Core)"
        ENT[Entities]
        RULES[Business Rules]
    end
    
    HTTP --> PORT_IN
    PORT_IN --> ENT
    ENT --> RULES
    RULES --> PORT_OUT
    PORT_OUT --> DB
    PORT_OUT --> EVT
    
    style ENT fill:#10b981,color:#fff
    style RULES fill:#10b981,color:#fff
    style PORT_IN fill:#3b82f6,color:#fff
    style PORT_OUT fill:#3b82f6,color:#fff
    style HTTP fill:#8b5cf6,color:#fff
    style DB fill:#f59e0b,color:#fff
    style EVT fill:#f59e0b,color:#fff