
# ADR-0001: Python 3.11 + FastAPI

## Status: Aceito

## Contexto
Precisamos de uma stack que permita modelar domínio com rigor, ter alta produtividade 
de testes e ser familiar ao time.

## Decisão
Adotar Python 3.11 com FastAPI.

## Justificativa Técnica
| Critério | FastAPI | Alternativas |
|----------|---------|--------------|
| Performance (async) | ~40k req/s | Flask ~10k |
| Validação de domínio | Pydantic v2 nativo | Manual |
| OpenAPI auto-gerado | Sim | Não |
| Curva de aprendizado | Baixa | — |
| Ecossistema de testes | pytest maduro | — |

## Consequências
✅ Tipagem forte no domínio via Pydantic

✅ Documentação Swagger automática

✅ Async I/O nativo para alta concorrência

⚠️ GIL do Python limita CPU-bound (mitigado com workers)
