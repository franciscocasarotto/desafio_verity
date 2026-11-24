# Arquitetura Alvo — Desafio Verity

## Diagrama C4 — Container (Mermaid, renderiza no GitHub)

## 1. Visão Geral da Solução
A arquitetura alvo foi desenhada seguindo o padrão **Hexagonal (Ports & Adapters)** com integração **Event-Driven Assíncrona**. Esta decisão garante o atendimento ao requisito não-funcional crítico: *o serviço de lançamentos não pode ficar indisponível se o consolidado cair*.

## 2. Diagramas Arquiteturais
Todos os diagramas detalhados (C4, Sequência, Fluxograma, Deploy, Estados e ER) estão consolidados no documento:
👉 **[Ver todos os diagramas gráficos](../diagramas.md)**

## 3. Decisões Arquiteturais Chave (Resumo dos ADRs)
1. **Python + FastAPI:** Performance async, validação nativa com Pydantic v2.
2. **Arquitetura Hexagonal:** Isolamento total das regras de negócio dos detalhes de infraestrutura.
3. **PostgreSQL + Redis:** ACID para transações financeiras + mensageria de baixa latência.
4. **Event-Driven Assíncrono:** Redis Streams com consumer groups para desacoplamento temporal e reprocessamento (at-least-once).

## 4. Contexto de Infraestrutura Híbrida
A solução é agnóstica à infraestrutura, mas otimizada para o cenário híbrido da organização:
- **On-premises (VMware/Azure Stack HCI):** PostgreSQL (dados sensíveis/LGPD) e Redis local.
- **Azure (AKS/Container Apps):** API Gateway e Serviço de Lançamentos (alta disponibilidade).
- **GCP (GKE/Cloud Run):** Serviço de Consolidado (processamento batch com preemptible VMs).
- **Conectividade:** ExpressRoute + Cloud Interconnect com DNS privado federado.

```mermaid
graph TB
    subgraph Clientes
        UI[Web/Mobile App Comerciante]
    end
    subgraph Edge
        GW[API Gateway - Rate Limit, JWT, CORS]
    end
    subgraph Aplicacao
        SL[Serviço Lançamentos<br/>FastAPI Hexagonal]
        SC[Serviço Consolidado<br/>FastAPI Hexagonal]
    end
    subgraph Mensageria
        RS[(Redis Streams<br/>lancamentos.events)]
    end
    subgraph Dados
        PG[(PostgreSQL<br/>schema: financeiro)]
        RC[(Redis Cache<br/>consolidado TTL 5min)]
    end

    UI -->|HTTPS + JWT| GW
    GW --> SL
    GW --> SC
    SL --> PG
    SL -->|publish| RS
    RS -->|consume group| SC
    SC --> PG
    SC --> RC
    SC -.->|cache read| RC

    style SL fill:#4CAF50,color:#fff
    style SC fill:#2196F3,color:#fff
    style RS fill:#FF9800,color:#fff
