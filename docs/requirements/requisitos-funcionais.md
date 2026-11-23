# Requisitos Funcionais (RF)

## Serviço de Lançamentos (SL)
| ID   | Requisito | Prioridade |
|------|-----------|------------|
| RF01 | O sistema deve permitir criar um lançamento com tipo (débito/crédito), valor, categoria, data e descrição. | Alta |
| RF02 | O sistema deve validar que valor > 0 e data ≤ hoje. | Alta |
| RF03 | O sistema deve permitir listar lançamentos por período e categoria. | Média |
| RF04 | O sistema deve permitir atualizar um lançamento preservando histórico de alterações (audit trail). | Alta |
| RF05 | O sistema deve permitir excluir (soft delete) um lançamento. | Média |
| RF06 | O sistema deve emitir evento `LancamentoRegistrado` quando um lançamento for criado/alterado/excluído. | Alta |
| RF07 | O sistema deve autenticar o comerciante via token JWT antes de qualquer operação. | Alta |

## Serviço de Consolidado (SC)
| ID   | Requisito | Prioridade |
|------|-----------|------------|
| RF08 | O sistema deve consumir eventos `LancamentoRegistrado` e recalcular o saldo do dia correspondente. | Alta |
| RF09 | O sistema deve expor endpoint `GET /consolidado/{data}` retornando saldo, total de créditos e débitos. | Alta |
| RF10 | O sistema deve expor endpoint `GET /consolidado?inicio=YYYY-MM-DD&fim=YYYY-MM-DD` retornando série diária. | Média |
| RF11 | O sistema deve permitir reprocessar um dia (idempotência). | Alta |
| RF12 | O sistema deve exportar relatório diário em JSON e CSV. | Baixa |