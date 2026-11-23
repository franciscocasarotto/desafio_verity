# Capacidades de Negócio (Business Capabilities)

## Mapa de Capacidades
[Comerciante]
│
├──► C1. Capturar lançamentos financeiros (débito/crédito)
│ └──► Valor: visibilidade em tempo real das operações
│
├──► C2. Classificar lançamentos por categoria
│ └──► Valor: análise granular de despesas/receitas
│
├──► C3. Consultar saldo consolidado diário
│ └──► Valor: decisão rápida sobre liquidez
│
├──► C4. Exportar relatório diário
│ └──► Valor: conformidade com contador/contabilidade
│
└──► C5. Corrigir lançamentos com rastreabilidade
└──► Valor: integridade dos dados financeiros


## Alinhamento com Arquitetura
| Capacidade | Serviço que entrega |
|------------|---------------------|
| C1, C2, C5 | `servicos/lancamentos` |
| C3, C4 | `servicos/consolidado` |