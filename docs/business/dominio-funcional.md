# Mapeamento de Domínios Funcionais e Capacidades de Negócio

## 1. Contexto de Negócio
O comerciante opera no domínio de **Gestão Financeira Operacional**, decomposto em 
dois bounded contexts (DDD):

### Sub-domínio 1: Registro de Lançamentos (Core)
- **Responsabilidade:** Capturar, validar e persistir transações financeiras.
- **Entidades:** Lancamento, Categoria, Conta
- **Regras de Negócio:**
  - Valor deve ser > 0
  - Tipo ∈ {DEBITO, CREDITO}
  - Data não pode ser futura
  - Descrição obrigatória
- **Idioma Ubíquo:** Débito, Crédito, Lançamento, Categoria

### Sub-domínio 2: Consolidação Diária (Core)
- **Responsabilidade:** Agregar lançamentos e calcular saldos por dia.
- **Entidades:** ConsolidadoDiario, Saldo
- **Regras de Negócio:**
  - Saldo = Σ Créditos − Σ Débitos do dia
  - Consolidação é idempotente por data
  - Recálculo automático quando lançamento é alterado

## 2. Mapa de Capacidades de Negócio (Business Capabilities)

| Capacidade | Descrição | Valor Gerado | Serviço Responsável |
|------------|-----------|--------------|---------------------|
| C1. Capturar lançamentos | Registro de débitos/créditos | Visibilidade em tempo real | lancamentos |
| C2. Classificar por categoria | Tagging financeiro | Análise granular | lancamentos |
| C3. Consultar saldo diário | Consolidação automática | Decisão de liquidez | consolidado |
| C4. Exportar relatório | JSON/CSV para contador | Conformidade fiscal | consolidado |
| C5. Corrigir com auditoria | Soft-delete + histórico | Integridade de dados | lancamentos |

## 3. Domínios de Suporte (Supporting Domains)
| Domínio | Tipo | Papel |
|---------|------|-------|
| Identidade & Acesso | Supporting | Autenticação JWT do comerciante |
| Notificação | Generic | Alertas de fechamento diário |
| Auditoria | Supporting | Trilha de alterações financeiras |
