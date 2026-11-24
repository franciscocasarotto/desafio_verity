# Arquitetura de Transição (Migração de Legado)

## Contexto
Considerando um cenário onde o comerciante utiliza atualmente uma planilha Excel complexa ou um sistema monolítico legado on-premise para controle de caixa, a migração direta (Big Bang) apresenta riscos inaceitáveis de parada operacional.

## Estratégia: Padrão Strangler Fig (Estrangulamento)
A migração será feita de forma incremental, roteando o tráfego gradualmente do legado para a nova arquitetura de microsserviços, até que o legado possa ser descomissionado com segurança.

### Fase 1: Coexistência e API Gateway (Semanas 1-2)
- Implementação de um API Gateway (ex: Kong, Azure API Management ou Nginx) na frente do legado.
- Todo o tráfego de leitura e escrita continua indo para o legado.
- **Objetivo:** Estabelecer o ponto de controle e observabilidade sem alterar o legado.

### Fase 2: Migração do Domínio de Lançamentos (Semanas 3-4)
- O novo serviço `lancamentos` é ativado.
- O API Gateway é reconfigurado: requisições `POST /lancamentos` são roteadas para o novo microsserviço.
- **Sincronização Dual-Write (Temporária):** Um worker assíncrono espelha os novos lançamentos para o banco legado para garantir fallback em caso de falha crítica do novo sistema.

### Fase 3: Migração do Domínio de Consolidado (Semanas 5-6)
- O novo serviço `consolidado` assume as requisições de leitura e relatórios (`GET /consolidado`).
- O legado é usado apenas como "archive" (arquivo morto) para consultas históricas de anos anteriores.

### Fase 4: Descomissionamento (Semana 7)
- O código legado é desligado.
- A infraestrutura do legado é desprovisionada (gerando economia imediata - FinOps).
- O API Gateway é simplificado, removendo as rotas de fallback.

## Matriz de Riscos da Transição
| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Perda de dados na dual-write | Baixa | Alto | Validação de checksum e retry com dead-letter queue (DLQ). |
| Degradação de performance no Gateway | Média | Médio | Cache agressivo no Redis para rotas de leitura (GET). |


