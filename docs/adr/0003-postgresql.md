# ADR-0003: PostgreSQL como banco relacional

## Status: Aceito

## Contexto
Dados financeiros exigem ACID, transações e integridade referencial.

## Decisão
PostgreSQL 15.

## Justificativa
- **ACID completo** — essencial para lançamentos financeiros
- **JSONB** — permite armazenar metadados flexíveis (audit trail)
- **Particionamento por data** — escala para anos de histórico
- **Trigger/Listen-Notify** — base para eventos de consolidação
- **Custo zero** — open source, alinhado a ambientes on-premise (perfil do arquiteto)

## Alternativas rejeitadas
- MongoDB: falta transações multi-document robustas
- MySQL: menos recursos de JSONB e particionamento nativo