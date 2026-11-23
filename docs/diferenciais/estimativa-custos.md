# Estimativa de Custos e FinOps

## Premissas
- **Cenário:** Pequeno/Médio comerciante com pico de 100 transações/segundo.
- **Modelo Híbrido:** A arquitetura suporta tanto Cloud (Azure/AWS) quanto On-Premise (via Azure Stack HCI / VMware, perfil da organização).

## Estimativa Cloud (Azure - Região East US)
| Recurso | Especificação | Custo Mensal Estimado (USD) |
|---------|---------------|-----------------------------|
| **Compute** | Azure Container Apps (2 instâncias, 0.5 vCPU, 1GB RAM) | $ 45,00 |
| **Database** | Azure Database for PostgreSQL - Flexible Server (Burstable B1ms) | $ 35,00 |
| **Cache** | Azure Cache for Redis (Basic C0) | $ 16,00 |
| **Networking** | API Management (Consumption Tier) + Load Balancer | $ 25,00 |
| **Observability** | Azure Monitor + Log Analytics (5GB ingestão/dia) | $ 40,00 |
| **Storage** | Blob Storage (Backups e logs) | $ 5,00 |
| **Total Cloud** | | **~ $ 166,00 / mês** |

## Estimativa On-Premise / Híbrido (Azure Stack HCI)
- **Compute/Storage:** Custo marginal zero (aproveitamento de hardware existente).
- **Licenças:** Windows Server / SQL Server (se aplicável) já amortizados.
- **Custo Operacional:** Energia, refrigeração e 0.2 FTE de SRE/DevOps para manutenção.
- **Vantagem:** Soberania de dados e latência próxima de zero para lojas físicas.

## Otimização FinOps
- **Auto-scaling:** Configurar HPA (Horizontal Pod Autoscaler) para escalar para 0 durante a madrugada (fechamento de caixa), reduzindo custos de compute em ~30%.
- **Reserved Instances:** Para ambientes de produção estáveis, comprar RIs de 1 ano para o PostgreSQL reduz o custo em ~40%.
