

# ADR-0001: Python 3.11 + FastAPI
## Status: Aceito
## Contexto
Stack precisa modelar domínio financeiro com rigor, alta produtividade de testes e familiaridade do time.

## Decisão
Python 3.11 + FastAPI + Pydantic v2.

## Justificativa
| Critério | FastAPI | Flask | Django |
|----------|---------|-------|--------|
| Performance async | ~40k req/s | ~10k | ~15k |
| Validação domínio | Pydantic nativo | Manual | DRF |
| OpenAPI auto | Sim | Não | Não |
| Curva aprendizado | Baixa | Baixa | Média |

## Consequências
✅ Tipagem forte no domínio
✅ Swagger auto-gerado (demonstra API pronta para consumo)
✅ Async nativo para alta concorrência
⚠️ GIL limita CPU-bound (mitigado com workers)

```markdown

## Diagrama Comparativo de Performance

```mermaid
graph LR
    subgraph "Performance (req/s)"
        F[FastAPI<br/>~40.000 req/s]
        DJ[Django<br/>~15.000 req/s]
        FL[Flask<br/>~10.000 req/s]
    end
    
    F -->|✅ Escolhido| DEC[Decisão]
    DJ -->|❌ Rejeitado| DEC
    FL -->|❌ Rejeitado| DEC
    
    style F fill:#10b981,color:#fff
    style DJ fill:#ef4444,color:#fff
    style FL fill:#ef4444,color:#fff
    style DEC fill:#3b82f6,color:#fff