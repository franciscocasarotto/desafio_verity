# Estimativa de Custos e FinOps

## Premissas de Infraestrutura Híbrida
- **Cenário:** Ambiente híbrido (On-premises + Multi-cloud).
- **Região de Hospedagem:** Brasil Sul (Azure) e São Paulo (GCP) para garantir baixa latência (<20ms) e conformidade com a LGPD (soberania de dados).
- **On-Premises (Azure Stack HCI / VMware):** Utilizado para persistência de dados (PostgreSQL) e processamento de regras de negócio críticas, aproveitando investimento já amortizado (Capex).
- **Nuvem (Azure / GCP):** Utilizada para a camada de apresentação e APIs, permitindo escalabilidade horizontal sob demanda (Opex) em dias de pico.
- *Nota: Valores estimados em Reais (BRL), considerando alíquotas padrão de ICMS e sem descontos de compromisso de longo prazo (Pay-as-you-go).*

---

## 1. Estimativa de Custos: Microsoft Azure (Região Brasil Sul)
*Cenário: 2 instâncias de API, 1 banco de dados gerenciado, cache e monitoramento básico.*

| Recurso | Especificação | Custo Mensal Estimado (BRL) |
|---------|---------------|-----------------------------|
| **Compute** | Azure Container Apps (2 instâncias, 0.5 vCPU, 1GB RAM) | R$ 180,00 |
| **Database** | Azure Database for PostgreSQL - Flexible Server (Burstable B1ms) | R$ 280,00 |
| **Cache** | Azure Cache for Redis (Basic C0 - 250MB) | R$ 95,00 |
| **Networking** | Azure API Management (Tier Consumption) + Load Balancer Básico | R$ 150,00 |
| **Observability** | Azure Monitor + Log Analytics (até 5GB de ingestão/dia) | R$ 100,00 |
| **Storage** | Blob Storage (LRS, ~10GB para backups e logs) | R$ 20,00 |
| **Total Azure** | | **~ R$ 825,00 / mês** |

---

## 2. Estimativa de Custos: Google Cloud Platform (Região São Paulo)
*Cenário equivalente ao Azure, utilizando serviços serverless e gerenciados do GCP.*

| Recurso | Especificação | Custo Mensal Estimado (BRL) |
|---------|---------------|-----------------------------|
| **Compute** | Cloud Run (2 serviços, 0.5 vCPU, 1GB RAM, escala a zero) | R$ 120,00 |
| **Database** | Cloud SQL for PostgreSQL (db-g1-small: 1 vCPU, 1.7GB RAM) | R$ 350,00 |
| **Cache** | Memorystore for Redis (Basic, 1GB) | R$ 150,00 |
| **Networking** | Cloud Load Balancing + API Gateway | R$ 120,00 |
| **Observability** | Cloud Logging & Monitoring (5GB/dia - aproveitando Free Tier) | R$ 80,00 |
| **Storage** | Cloud Storage (Standard, ~10GB) | R$ 15,00 |
| **Total GCP** | | **~ R$ 835,00 / mês** |

---

## 3. Estimativa On-Premise (Datacenter Corporativo)
- **Compute/Storage:** Custo marginal zero para esta carga específica (aproveitamento de capacidade ociosa do cluster VMware/Azure Stack HCI existente).
- **Licenças:** Microsoft Windows Server / SQL Server (se aplicável) já amortizados no Capex anual.
- **Custo Operacional (Opex):** Energia, refrigeração e alocação parcial de ~0.1 FTE de SRE/DevOps para manutenção.
- **Vantagem Estratégica:** Soberania total dos dados, latência próxima de zero para PDVs em lojas físicas e isolamento de rede física.

---

## 4. Estratégias de Otimização de Custos (FinOps)

Para garantir que a arquitetura não apenas funcione, mas seja financeiramente eficiente, as seguintes práticas serão aplicadas:

1. **Bursting Controlado e Scale-to-Zero:** Utilizar modelos serverless (Azure Container Apps ou GCP Cloud Run) que escalam para zero instâncias durante a madrugada (fechamento de caixa), reduzindo custos de computação em até 40%.
2. **Descontos por Compromisso (Commitment Discounts):** Para o banco de dados (que é um recurso de estado e não pode escalar para zero), adquirir *Reserved Instances* (Azure) ou *Committed Use Discounts* (GCP) de 1 ano, gerando uma economia imediata de ~35% a 40% no valor do PostgreSQL/Cloud SQL.
3. **Spot/Preemptible Instances para Processamento Assíncrono:** Se o serviço de `consolidado` for migrado para máquinas virtuais no futuro, utilizar instâncias spot (até 70% mais baratas) é viável, pois a arquitetura é tolerante a falhas e pode reprocessar a fila sem impacto ao usuário final.
4. **Governança e Tagging:** Implementar política obrigatória de *Resource Tagging* (ex: `Environment=Prod`, `Project=Verity`, `CostCenter=Financeiro`) para habilitar relatórios de *Showback/Chargeback* precisos e evitar "gastos fantasmas" (Zombie Resources).
