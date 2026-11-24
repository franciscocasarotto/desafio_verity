# 💰 Estimativa de Custos e FinOps — Desafio Verity

> **Contexto:** Análise financeira e técnica para o projeto **Desafio Verity** (Controle de Fluxo de Caixa), considerando ambiente híbrido corporativo (On-premises VMware/Azure Stack HCI + Multi-Cloud Azure + GCP) e conformidade com LGPD.

---

## 📋 Índice

1. [Visão Executiva](#1-visão-executiva)
2. [Premissas do Cenário](#2-premissas-do-cenário)
3. [Comparativo de Provedores](#3-comparativo-de-provedores)
4. [Estimativa Azure (Brasil)](#5-estimativa-azure-brasil)
5. [Estimativa GCP (Brasil)](#6-estimativa-gcp-brasil)
6. [Comparativo Direto](#7-comparativo-direto)
7. [TCO — Total Cost of Ownership (3 anos)](#8-tco--total-cost-of-ownership-3-anos)
8. [Performance por Provedor](#9-performance-por-provedor)
9. [Segurança e Compliance LGPD](#10-segurança-e-compliance-lgpd)
10. [DevOps e Kubernetes](#11-devops-e-kubernetes)
11. [Integração On-Prem e ITSM](#12-integração-on-prem-e-itsm)
12. [Lock-in e Portabilidade](#13-lock-in-e-portabilidade)
13. [Matriz de Decisão Ponderada](#14-matriz-de-decisão-ponderada)
14. [Recomendação Arquitetural](#15-recomendação-arquitetural)
15. [Estratégias FinOps](#16-estratégias-finops)
16. [Cenário On-Premises](#17-cenário-on-premises)
17. [Roadmap Multi-Cloud](#18-roadmap-multi-cloud)
18. [Referências](#19-referências)

---

## 1. Visão Executiva

| Métrica | Azure | GCP | Híbrido (Recomendado) |
|---------|-------|-----|----------------------|
| **Custo Mensal (Pay-as-you-go)** | R$ 825,00 | R$ 835,00 | R$ 612,00 |
| **Custo Mensal (com FinOps)** | R$ 577,00 | R$ 501,00 | R$ 428,00 |
| **TCO 3 anos (com FinOps)** | R$ 20.772,00 | R$ 18.036,00 | **R$ 15.408,00** |
| **Economia vs. Pay-as-you-go** | 30% | 40% | **49%** |

> 🎯 **Conclusão:** A arquitetura híbrida (On-prem + Azure + GCP) com estratégias FinOps ativas oferece o melhor equilíbrio entre **custo, performance, conformidade LGPD e resiliência operacional**.

---

## 2. Premissas do Cenário

| Parâmetro | Valor | Justificativa |
|-----------|-------|---------------|
| **Carga de trabalho** | Pico de 50 req/s no consolidado | Requisito não-funcional crítico do desafio |
| **Região** | São Paulo, Brasil | Conformidade LGPD + latência baixa para PDVs |
| **Moeda** | BRL (R$) | Faturamento local, sem exposição cambial |
| **Modelo de cobrança** | Pay-as-you-go (base) + FinOps (otimizado) | Flexibilidade inicial, otimização progressiva |
| **Ambiente** | Híbrido (On-prem + Azure + GCP) | Perfil corporativo da organização |
| **SLA alvo** | 99.5% mensal | Alinhado com RNF08 do projeto |
| **Horizonte de análise** | 36 meses (3 anos) | Ciclo típico de decisão de arquitetura |
| **Impostos** | ICMS ~18% (SP) + PIS/COFINS | Valores já inclusos nas estimativas |

---

## 3. Comparativo de Provedores

| Dimensão | Microsoft Azure | Google Cloud Platform |
|----------|-----------------|----------------------|
| **Posição de mercado** | #2 mundial (foco enterprise) | #3 mundial (foco data/AI) |
| **Região Brasil** | Brazil South (São Paulo) | southamerica-east1 (São Paulo) |
| **Zonas de disponibilidade** | 3 AZs | 3 zonas |
| **SLA padrão** | 99.9% - 99.99% | 99.9% - 99.95% |
| **Integração on-prem** | Azure Arc + Stack HCI (nativa) | Anthos + Distributed Cloud |
| **Identidade** | Microsoft Entra ID (Azure AD) | Google Cloud Identity |
| **Foco estratégico** | Enterprise, Híbrido, SAP, M365 | Data, AI/ML, Kubernetes, Open Source |
| **Suporte em português** | ✅ Nativo | ✅ Nativo |
| **Parceiros no Brasil** | Ampla rede (Accenture, Avanade) | Rede menor (Cloud Solutions) |

---


## 4. Estimativa Azure (Brasil)

> **Região:** Brazil South (São Paulo) | **Moeda:** BRL | **Modelo:** Pay-as-you-go

| Recurso | Especificação | Custo Mensal (R$) |
|---------|---------------|-------------------|
| **Compute** | Container Apps (2 instâncias, 0.5 vCPU, 1GB RAM) | R$ 180,00 |
| **Database** | PostgreSQL Flexible (Burstable B1ms, 20GB) | R$ 280,00 |
| **Cache** | Cache for Redis (Basic C0, 250MB) | R$ 95,00 |
| **Networking** | API Management (Consumption) + Load Balancer | R$ 150,00 |
| **Observability** | Azure Monitor + Log Analytics (5GB/dia) | R$ 100,00 |
| **Storage** | Blob Storage LRS (~10GB backups/logs) | R$ 20,00 |
| **TOTAL** | | **R$ 825,00/mês** |

### Com FinOps (30% de economia)
- **Reserved Instances** (1 ano): -40% no PostgreSQL
- **Scale-to-Zero** (madrugada): -40% no compute
- **Spot Instances** (batch): -70% no processamento assíncrono
- **Custo otimizado:** ~R$ 577,00/mês

---

## 5. Estimativa GCP (Brasil)

> **Região:** southamerica-east1 (São Paulo) | **Moeda:** BRL | **Modelo:** Pay-as-you-go

| Recurso | Especificação | Custo Mensal (R$) |
|---------|---------------|-------------------|
| **Compute** | Cloud Run (2 serviços, 0.5 vCPU, 1GB RAM, scale-to-zero) | R$ 120,00 |
| **Database** | Cloud SQL (db-g1-small, 1 vCPU, 1.7GB RAM) | R$ 350,00 |
| **Cache** | Memorystore (Basic, 1GB) | R$ 150,00 |
| **Networking** | Cloud Load Balancing + API Gateway | R$ 120,00 |
| **Observability** | Cloud Logging & Monitoring (5GB/dia, free tier) | R$ 80,00 |
| **Storage** | Cloud Storage Standard (~10GB) | R$ 15,00 |
| **TOTAL** | | **R$ 835,00/mês** |

### Com FinOps (40% de economia)
- **Committed Use Discounts** (1 ano): -37% no Cloud SQL
- **Sustained Use Discounts**: automático após 25% de uso mensal
- **Preemptible VMs** (batch): -80% no processamento
- **Custo otimizado:** ~R$ 501,00/mês

---

## 6. Comparativo Direto

| Critério | Azure | GCP | Híbrido |
|----------|-------|-----|---------|
| **Pay-as-you-go** | R$ 825 | R$ 835 | R$ 612 |
| **Com FinOps** | R$ 577 | R$ 501 | **R$ 428** |
| **Melhor para** | Enterprise | Data/AI | **Custo-benefício** |
| **Integração on-prem** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Ecosistema Brasil** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |

---

## 7. TCO — Total Cost of Ownership (3 anos)

### 7.1. TCO Azure (36 meses)

| Item | Ano 1 | Ano 2 | Ano 3 | Total |
|------|-------|-------|-------|-------|
| Pay-as-you-go | R$ 9.900 | R$ 9.900 | R$ 9.900 | R$ 29.700 |
| Com FinOps | R$ 6.924 | R$ 6.924 | R$ 6.924 | **R$ 20.772** |
| Economia | R$ 2.976 | R$ 2.976 | R$ 2.976 | R$ 8.928 |

### 7.2. TCO GCP (36 meses)

| Item | Ano 1 | Ano 2 | Ano 3 | Total |
|------|-------|-------|-------|-------|
| Pay-as-you-go | R$ 10.020 | R$ 10.020 | R$ 10.020 | R$ 30.060 |
| Com FinOps | R$ 6.012 | R$ 6.012 | R$ 6.012 | **R$ 18.036** |
| Economia | R$ 4.008 | R$ 4.008 | R$ 4.008 | R$ 12.024 |

### 7.3. TCO Híbrido (36 meses) — Recomendado

| Item | Ano 1 | Ano 2 | Ano 3 | Total |
|------|-------|-------|-------|-------|
| On-premises (marginal) | R$ 0 | R$ 0 | R$ 0 | R$ 0 |
| Azure (Lançamentos) | R$ 3.462 | R$ 3.462 | R$ 3.462 | R$ 10.386 |
| GCP (Consolidado batch) | R$ 1.674 | R$ 1.674 | R$ 1.674 | R$ 5.022 |
| **TOTAL HÍBRIDO** | **R$ 5.136** | **R$ 5.136** | **R$ 5.136** | **R$ 15.408** |

> 💡 **Economia de 49%** vs. Pay-as-you-go puro em nuvem, aproveitando hardware existente no on-premises.

---

## 8. Performance por Provedor

| Métrica | Azure | GCP | On-Premises |
|---------|-------|-----|-------------|
| **Latência rede interna** | <1ms (AZ) | <1ms (zona) | ~0.1ms |
| **Latência Brasil → API** | 15-30ms | 15-30ms | <5ms |
| **Throughput PostgreSQL** | ~1000 TPS | ~800 TPS | ~1500 TPS |
| **Throughput Redis** | ~100k ops/s | ~100k ops/s | ~150k ops/s |
| **Tempo de boot container** | ~3s | ~2s | ~1s |
| **Atende 50 req/s?** | ✅ Sim | ✅ Sim | ✅ Sim (folga) |

> ✅ **Todos os provedores atendem o RNF-CRIT-02** (50 req/s com ≤5% perda). Nossa meta é **0% perda** via Redis Streams com consumer groups.

---

## 9. Segurança e Compliance LGPD

| Requisito | Azure | GCP | On-Premises |
|-----------|-------|-----|-------------|
| **Certificação LGPD** | ✅ ISO 27001, 27018 | ✅ ISO 27001, 27018 | ✅ Controle total |
| **Dados em repouso** | AES-256 | AES-256 | AES-256 (TDE) |
| **Dados em trânsito** | TLS 1.3 | TLS 1.3 | TLS 1.3 |
| **Soberania de dados** | Região Brasil | Região Brasil | 100% local |
| **Backup criptografado** | ✅ | ✅ | ✅ |
| **Audit trail** | Azure Policy | Cloud Audit Logs | SIEM local |
| **DPO support** | ✅ | ✅ | ✅ |

> 🔐 **Recomendação:** Dados sensíveis (PII de comerciantes) permanecem **on-premises** (PostgreSQL). Apenas dados anonimizados de transações vão para a nuvem.

---

## 10. DevOps e Kubernetes

| Ferramenta | Azure | GCP | On-Premises |
|------------|-------|-----|-------------|
| **Orquestrador** | AKS | GKE | K3s/Rancher |
| **CI/CD nativo** | Azure DevOps | Cloud Build | GitLab CI |
| **Registry** | ACR | GCR | Harbor |
| **GitOps** | Flux/ArgoCD | Anthos Config Mgmt | ArgoCD |
| **IaC** | Bicep/Terraform | Deployment Mgr/Terraform | Terraform/Ansible |
| **Service Mesh** | Istio (AKS) | Anthos Service Mesh | Istio |

### Custo DevOps (mensal estimado)
| Item | Azure | GCP | Híbrido |
|------|-------|-----|---------|
| CI/CD (pipelines) | R$ 50 | R$ 40 | R$ 0 (GitLab self-hosted) |
| Registry (imagens) | R$ 20 | R$ 15 | R$ 0 (Harbor local) |
| **Total DevOps** | **R$ 70** | **R$ 55** | **R$ 0** |

---

## 11. Integração On-Prem e ITSM

### 11.1. Conectividade Híbrida

| Solução | Azure | GCP | Custo Mensal |
|---------|-------|-----|--------------|
| **VPN Site-to-Site** | VPN Gateway | Cloud VPN | R$ 150-300 |
| **Link dedicado** | ExpressRoute | Cloud Interconnect | R$ 2.000-5.000 |
| **SD-WAN** | Azure Virtual WAN | Network Connectivity | R$ 500-1.500 |

> 💡 **Para o Desafio Verity:** VPN Site-to-Site é suficiente (baixo volume de dados, alta criticidade).

### 11.2. Integração com ITSM (ServiceNow)

| Evento | Ação no ServiceNow | Custo |
|--------|-------------------|-------|
| Healthcheck falha > 5min | Abre Incidente P1 | Via MID Server (incluso) |
| CPU > 80% por 10min | Abre RFC de scaling | Webhook (grátis) |
| Deploy em produção | Cria Change Request | REST API (grátis) |
| Vulnerabilidade detectada | Abre Incidente de Segurança | Integration Hub |

> 🔗 **MID Server** do ServiceNow pode rodar on-premises, conectando a nuvem Azure/GCP ao ITSM corporativo sem expor a rede interna.

---

## 12. Lock-in e Portabilidade

| Aspecto | Azure | GCP | Híbrido |
|---------|-------|-----|---------|
| **Vendor lock-in** | Médio | Médio | **Baixo** |
| **Portabilidade de código** | Alta (containers) | Alta (containers) | **Máxima** |
| **Portabilidade de dados** | Média (export) | Média (export) | **Alta** (PostgreSQL padrão) |
| **Multi-cloud nativo** | Azure Arc | Anthos | **Terraform + K8s** |
| **Risco de migração** | 3-6 meses | 3-6 meses | **1-2 meses** |

> 🎯 **Estratégia anti-lock-in:** Usar **Kubernetes + Terraform + PostgreSQL** como camadas de abstração. Trocar de provedor = mudar 2-3 arquivos `.tf`.

---

## 13. Matriz de Decisão Ponderada

| Critério | Peso | Azure (1-5) | GCP (1-5) | Híbrido (1-5) |
|----------|------|-------------|-----------|---------------|
| **Custo** | 25% | 4 | 4 | **5** |
| **Performance** | 20% | 4 | 4 | **5** |
| **Integração on-prem** | 20% | **5** | 3 | **5** |
| **Segurança/LGPD** | 15% | 4 | 4 | **5** |
| **Ecosistema Brasil** | 10% | **5** | 3 | 4 |
| **Portabilidade** | 10% | 3 | 3 | **5** |
| **PONTUAÇÃO FINAL** | 100% | **4.15** | **3.60** | **4.90** |

> 🏆 **Vencedor: Arquitetura Híbrida** com 4.90/5.00 — melhor custo-benefício, performance e conformidade.

---

## 14. Recomendação Arquitetural

### ✅ Arquitetura Recomendada: Híbrida Multi-Cloud

┌─────────────────────────────────────────────────────────┐

│ ON-PREMISES (VMware / Azure Stack HCI) │

│ ┌─────────────────────────────────────────────────┐ │

│ │ PostgreSQL (dados sensíveis, LGPD) │ │

│ │ Redis (cache local, baixa latência) │ │

│ │ HashiCorp Vault (secrets) │ │

│ └─────────────────────────────────────────────────┘ │

└─────────────────────────────────────────────────────────┘

↕ VPN Site-to-Site (ExpressRoute)

┌─────────────────────────────────────────────────────────┐

│ AZURE (Brazil South) │

│ ┌─────────────────────────────────────────────────┐ │

│ │ API Gateway (rate limiting, JWT) │ │

│ │ Serviço Lançamentos (Container Apps/AKS) │ │

│ │ Azure Monitor (observabilidade) │ │

│ └─────────────────────────────────────────────────┘ │

└─────────────────────────────────────────────────────────┘

↕ Cloud Interconnect

┌─────────────────────────────────────────────────────────┐

│ GCP (southamerica-east1) │

│ ┌─────────────────────────────────────────────────┐ │

│ │ Serviço Consolidado (Cloud Run/GKE) │ │

│ │ Batch de madrugada (preemptible VMs) │ │

│ │ Cloud Monitoring │ │

│ └─────────────────────────────────────────────────┘ │

└─────────────────────────────────────────────────────────┘

### Por que essa arquitetura?

1. **Custo otimizado:** Aproveita hardware existente (Capex amortizado)
2. **Performance máxima:** Dados sensíveis com latência <5ms no on-premises
3. **Escalabilidade elástica:** Azure/GCP escalam sob demanda em picos
4. **Conformidade LGPD:** Dados pessoais nunca saem do datacenter corporativo
5. **Resiliência:** Falha em um provedor não derruba o sistema todo
6. **Anti-lock-in:** Kubernetes + Terraform permitem trocar provedor em semanas

---

## 15. Estratégias FinOps

### 15.1. Imediatas (Mês 1-3)

| Estratégia | Economia Estimada | Esforço |
|------------|-------------------|---------|
| **Tagging obrigatório** | Visibilidade 100% | Baixo |
| **Right-sizing** | 15-25% | Médio |
| **Desligar ambientes dev à noite** | 30-40% (dev) | Baixo |
| **Reserved Instances (1 ano)** | 35-40% (DB) | Baixo |

### 15.2. Médio Prazo (Mês 3-12)

| Estratégia | Economia Estimada | Esforço |
|------------|-------------------|---------|
| **Spot/Preemptible VMs** (batch) | 60-80% (batch) | Médio |
| **Scale-to-Zero** (serverless) | 40-50% (compute) | Médio |
| **Committed Use Discounts** (GCP) | 37% (Cloud SQL) | Baixo |
| **Savings Plans** (Azure) | 30-50% (compute) | Baixo |

### 15.3. Longo Prazo (Ano 2-3)

| Estratégia | Economia Estimada | Esforço |
|------------|-------------------|---------|
| **Arquitetura serverless-first** | 50-70% | Alto |
| **Multi-cloud arbitrage** | 10-20% adicional | Alto |
| **FinOps cultural (showback/chargeback)** | 15-25% comportamental | Médio |

---

## 16. Cenário On-Premises

### 16.1. Infraestrutura Existente (Aproveitamento)

| Recurso | Especificação | Custo Marginal |
|---------|---------------|----------------|
| **Compute** | Cluster VMware (8 hosts, 512GB RAM cada) | R$ 0 (Capex amortizado) |
| **Storage** | SAN NetApp (50TB) | R$ 0 (Capex amortizado) |
| **Rede** | Switches Cisco 10GbE | R$ 0 (Capex amortizado) |
| **Energia + Refrigeração** | Datacenter corporativo | ~R$ 200/mês (alocado) |
| **FTE SRE/DevOps** | 0.2 FTE dedicado | ~R$ 4.000/mês (alocado) |

### 16.2. Quando On-Premises é Melhor?

✅ **Use on-premises quando:**
- Dados sensíveis (LGPD, PCI-DSS, saúde)
- Latência crítica (<5ms)
- Carga previsível e estável
- Hardware já amortizado
- Soberania de dados obrigatória

❌ **Use nuvem quando:**
- Picos imprevisíveis (Black Friday)
- Expansão geográfica rápida
- Inovação (AI/ML, serverless)
- Time-to-market crítico

---

## 17. Roadmap Multi-Cloud

### Marcos Principais

| Marco | Data | Entregável |
|-------|------|------------|
| **M1** | Mês 3 | Governança FinOps básica (tagging + dashboards) |
| **M2** | Mês 6 | Produção híbrida ativa (Azure + on-prem) |
| **M3** | Mês 12 | Multi-cloud completo (Azure + GCP + on-prem) |
| **M4** | Mês 18 | Otimização avançada (Spot + Scale-to-Zero) |
| **M5** | Mês 36 | Maturidade FinOps (showback/chargeback) |

### Fases do Roadmap

| Fase | Período | Foco |
|------|---------|------|
| **Fase 1 - Fundação** | Mês 1-6 | Tagging, VPN, Deploy Azure |
| **Fase 2 - Expansão** | Mês 6-12 | Deploy GCP, Reserved Instances, Monitoramento |
| **Fase 3 - Otimização** | Mês 12-24 | Spot Instances, Scale-to-Zero, Arbitrage |
| **Fase 4 - Maturidade** | Mês 24-36 | FinOps cultural, Serverless-first |

---

## 18. Referências

### 18.1. Calculadoras Oficiais
- [Azure Pricing Calculator](https://azure.microsoft.com/pricing/calculator/)
- [GCP Pricing Calculator](https://cloud.google.com/products/calculator)

### 18.2. Frameworks FinOps
- [FinOps Foundation](https://www.finops.org/)
- [Well-Architected Framework (Azure)](https://learn.microsoft.com/azure/well-architected/)
- [Well-Architected Framework (GCP)](https://cloud.google.com/architecture/framework)

### 18.3. Compliance
- [LGPD (Lei 13.709/2018)](http://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm)
- [ISO 27001/27018](https://www.iso.org/isoiec-27001-information-security.html)

### 18.4. Benchmarks de Performance
- [Cloud Performance Benchmark](https://www.cloudharmony.com/)
- [Gartner Magic Quadrant Cloud IaaS](https://www.gartner.com/)

---

## 📊 Resumo Executivo para Decisão

| Critério | Azure | GCP | **Híbrido** |
|----------|-------|-----|-------------|
| **Custo 3 anos (FinOps)** | R$ 20.772 | R$ 18.036 | **R$ 15.408** |
| **Performance** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | **⭐⭐⭐⭐⭐** |
| **Conformidade LGPD** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | **⭐⭐⭐⭐⭐** |
| **Integração on-prem** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | **⭐⭐⭐⭐⭐** |
| **Portabilidade** | ⭐⭐⭐ | ⭐⭐⭐ | **⭐⭐⭐⭐⭐** |
| **Recomendação** | Bom | Bom | **🏆 MELHOR** |

> ✅ **Decisão final:** Arquitetura Híbrida (On-premises + Azure + GCP) com estratégias FinOps ativas, entregando **49% de economia** vs. cloud puro, com máxima conformidade LGPD e resiliência operacional.

---

