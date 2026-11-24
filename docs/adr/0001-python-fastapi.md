
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
