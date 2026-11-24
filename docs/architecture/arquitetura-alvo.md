# Arquitetura Alvo — Desafio Verity

## Visão Geral
                ┌─────────────────────────────────────────┐
                │            CLIENT (Comerciante)         │
                └────────────────────┬────────────────────┘
                                     │ HTTPS + JWT
                                     ▼
                ┌─────────────────────────────────────────┐
                │         API GATEWAY / REVERSE PROXY     │
                │     (Rate limiting, Auth, Logging)      │
                └─────┬───────────────────────────┬───────┘
                      │                           │
                      ▼                           ▼
          ┌──────────────────────┐    ┌──────────────────────┐
          │  SERVIÇO LANCAMENTOS │    │  SERVIÇO CONSOLIDADO │
          │  (FastAPI/Hexagonal) │    │  (FastAPI/Hexagonal) │
          └──────────┬───────────┘    └──────────┬───────────┘
                     │                           │
                     │ publica evento            │ consome evento
                     ▼                           ▼
          ┌──────────────────────────────────────────────┐
          │         REDIS STREAMS (Message Broker)       │
          │         canal: lancamentos.events            │
          └──────────────────────────────────────────────┘
                     │                           │
                     ▼                           ▼
          ┌──────────────────────┐    ┌──────────────────────┐
          │   PostgreSQL (SL)    │    │  PostgreSQL (SC)     │
          │   schema: lancamentos│    │  schema: consolidado │
          └──────────────────────┘    └──────────────────────┘
                     │                           │
                     └──────────┬────────────────┘
                                ▼
                     ┌──────────────────────┐
                     │   REDIS (Cache)      │
                     │   TTL 5min           │
                     └──────────────────────┘
                     
## Padrão Arquitetural Escolhido: **Hexagonal (Ports & Adapters)**

Cada serviço segue a estrutura:
src/

├── domain/ # Entidades + regras puras (sem dependências externas)

├── application/ # Casos de uso + ports (interfaces)

├── infrastructure/ # Adapters (DB, Redis, HTTP, eventos)

└── presentation/ # Controllers (FastAPI routers)

## Contexto de Infraestrutura Híbrida
A arquitetura foi desenhada considerando um ambiente híbrido corporativo:
- **On-Premises (VMware / Azure Stack HCI):**
  
  Ideal para o banco de dados PostgreSQL e dados sensíveis que exigem baixa latência e conformidade rígida de soberania de dados (Data Residency).
- **Nuvem Pública (Azure / GCP):**
  
  Ideal para os serviços de API (Lançamentos e Consolidado) que exigem escalabilidade elástica (bursting) em dias de pico, utilizando AKS (Azure Kubernetes Service) ou GKE (Google Kubernetes Engine).
- **Conectividade:**
  
  Integração segura entre os ambientes via Azure ExpressRoute ou Google Cloud Interconnect, com DNS privado e resolução de nomes unificada.




## Justificativa da Escolha
- **Por que não monolito?**

   Dois serviços com responsabilidades distintas e cadências diferentes (escrita vs. agregação). Monolito acoplaria deploy e escalabilidade.
- **Por que não microsserviços puros?**

   Over-engineering para o escopo. Dois serviços é o mínimo viável que atende o requisito.
- **Por que Hexagonal?**

  Permite testar domínio sem banco, trocar PostgreSQL por outro sem tocar regras de negócio, e isolar a fonte de dados do caso de uso.

## Fluxo Principal (Happy Path)
1. Comerciante envia `POST /lancamentos` com JWT.
2. Serviço SL valida, persiste em PostgreSQL, publica evento em Redis Streams.
3. Serviço SC consome evento, recalcula saldo do dia, atualiza cache Redis.
4. Comerciante consulta `GET /consolidado/2026-11-24` e recebe saldo em <150ms (cache hit).

## Fluxo de Falha (Resiliência)
- Se SC estiver indisponível, eventos ficam em Redis Streams (at-least-once).
- SC reprocessa ao voltar (consumer group com offset persistente).
- Circuit breaker no SC: se SL falhar ao consultar, usa cache de 5min.
