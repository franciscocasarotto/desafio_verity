# Requisitos Funcionais (RF)

## Serviço de Lançamentos (SL)
| ID | Requisito | Prioridade |
|----|-----------|------------|
| RF01 | Criar lançamento com tipo, valor, categoria, data, descrição | Alta |
| RF02 | Validar valor > 0 e data ≤ hoje | Alta |
| RF03 | Listar lançamentos por período e categoria | Média |
| RF04 | Atualizar lançamento preservando histórico | Alta |
| RF05 | Excluir (soft delete) lançamento | Média |
| RF06 | Emitir evento LancamentoRegistrado | Alta |
| RF07 | Autenticar comerciante via JWT | Alta |


## Serviço de Consolidado (SC)
| ID | Requisito | Prioridade |
|----|-----------|------------|
| RF08 | Consumir eventos e recalcular saldo diário | Alta |
| RF09 | GET /consolidado/{data} retorna saldo consolidado | Alta |
| RF10 | GET /consolidado?inicio=&fim= retorna série | Média |
| RF11 | Reprocessar dia (idempotência) | Alta |
| RF12 | Exportar relatório JSON/CSV | Baixa |
