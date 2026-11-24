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

## 5. Gráfico Comparativo de Custos (Azure vs. GCP)

```mermaid
graph LR
    subgraph "💰 Azure — R$ 825/mês"
        A1[Compute: R$ 180]
        A2[Database: R$ 280]
        A3[Cache: R$ 95]
        A4[Networking: R$ 150]
        A5[Observability: R$ 100]
        A6[Storage: R$ 20]
    end
    
    subgraph "💰 GCP — R$ 835/mês"
        G1[Compute: R$ 120]
        G2[Database: R$ 350]
        G3[Cache: R$ 150]
        G4[Networking: R$ 120]
        G5[Observability: R$ 80]
        G6[Storage: R$ 15]
    end
    
    A1 -.->|≈| G1
    A2 -.->|≈| G2
    
    style A1 fill:#06b6d4,color:#fff
    style G1 fill:#4285f4,color:#fff 