# Estimativa de Custos e FinOps

## Premissas de Infraestrutura Híbrida
- **Cenário:** Ambiente híbrido (On-premises + Multi-cloud).
- **On-Premises (Azure Stack HCI / VMware):** Utilizado para persistência de dados (PostgreSQL) e processamento de regras de negócio críticas, aproveitando investimento já amortizado (Capex) e garantindo soberania de dados.
- **Nuvem (Azure / GCP):** Utilizada para a camada de apresentação e APIs (Container Apps / AKS / GKE), permitindo escalabilidade horizontal sob demanda (Opex) em dias de pico de lançamentos.

## Estratégia de Otimização de Custos (FinOps)
1. **Bursting Controlado:** Manter 1 réplica dos serviços no on-premises e configurar HPA (Horizontal Pod Autoscaler) para escalar até 5 réplicas na nuvem (Azure/GCP) apenas durante o horário comercial.
2. **Gerenciamento de Identidade Unificado:** Utilizar o Azure Entra ID (Active Directory) como provedor de identidade central, federado com o GCP, eliminando a necessidade de gerenciar múltiplos diretórios e reduzindo overhead operacional.
3. **Cache Distribuído:** Utilizar instâncias do Redis gerenciadas (Azure Cache for Redis ou Memorystore no GCP) com políticas de evicção para evitar custos de armazenamento desnecessários.

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

## Estimativa On-Premise 
- **Compute/Storage:** Custo marginal zero (aproveitamento de hardware existente).
- **Licenças:** Windows Server / SQL Server (se aplicável) já amortizados.
- **Custo Operacional:** Energia, refrigeração e 0.2 FTE de SRE/DevOps para manutenção.
- **Vantagem:** Soberania de dados e latência próxima de zero para lojas físicas.

## Otimização FinOps
- **Auto-scaling:** Configurar HPA (Horizontal Pod Autoscaler) para escalar para 0 durante a madrugada (fechamento de caixa), reduzindo custos de compute em ~30%.
- **Reserved Instances:** Para ambientes de produção estáveis, comprar RIs de 1 ano para o PostgreSQL reduz o custo em ~40%.
