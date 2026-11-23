# ADR-0002: Arquitetura Hexagonal (Ports & Adapters)

## Status: Aceito

## Contexto
O domínio financeiro é crítico e muda com frequência (novas regras de consolidação, 
novas categorias). Precisamos isolar regras de negócio de detalhes técnicos.

## Decisão
Adotar arquitetura hexagonal em ambos os serviços.

## Trade-offs Analisados
| Padrão | Prós | Contras | Decisão |
|--------|------|---------|---------|
| Monolito MVC | Simples | Acoplamento, difícil testar domínio | ❌ |
| Microsserviços | Escalável | Overhead operacional excessivo para 2 serviços | ❌ |
| **Hexagonal** | **Testável, substitui DB, isola domínio** | **Mais boilerplate** | **✅** |
| CQRS puro | Separação leitura/escrita | Complexidade desnecessária | ❌ |

## Consequências
✅ Testes unitários do domínio sem mock de banco
✅ PostgreSQL pode ser trocado por SQLite em testes
✅ Adapters de eventos isolados (troca Redis → Kafka sem tocar domínio)
⚠️ Exige disciplina para não vazar dependências ao domínio