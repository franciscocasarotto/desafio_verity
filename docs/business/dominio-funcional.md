# Domínio Funcional — Controle de Fluxo de Caixa

## Contexto de Negócio
O comerciante opera em um domínio funcional de **Gestão Financeira Operacional**, 
subdividido em duas sub-regiões (bounded contexts):

### Sub-domínio 1: Registro de Lançamentos
- **Responsabilidade**: Capturar, validar e persistir transações financeiras.
- **Entidades**: `Lancamento` (débito/crédito), `Categoria`, `Conta`.
- **Regras de Negócio**:
  - Valor deve ser > 0
  - Tipo ∈ {DEBITO, CREDITO}
  - Data não pode ser futura
  - Descrição obrigatória
- **Idioma Ubíquo**: Débito, Crédito, Lançamento, Categoria.

### Sub-domínio 2: Consolidação Diária
- **Responsabilidade**: Agregar lançamentos e calcular saldos por dia.
- **Entidades**: `ConsolidadoDiario`, `Saldo`.
- **Regras de Negócio**:
  - Saldo = Σ Créditos − Σ Débitos do dia
  - Consolidação é idempotente por data
  - Recálculo automático quando um lançamento é editado/excluído
- **Idioma Ubíquo**: Saldo, Consolidado, Fechamento Diário.

## Domínios Funciais (visão corporativa)
| Domínio | Tipo | Papel |
|---------|------|-------|
| Gestão Financeira | Core | Entrega valor direto ao comerciante |
| Identidade & Acesso | Supporting | Autenticação do comerciante |
| Notificação | Generic | Alertas de fechamento diário |