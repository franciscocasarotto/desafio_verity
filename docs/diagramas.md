# 📊 Diagramas Gráficos — Desafio Verity

Este documento contém a representação visual completa da arquitetura, processos e dados do projeto.

> 💡 **Dica:** No GitHub, os diagramas Mermaid são renderizados automaticamente.

---

## 1. Domínio DDD (Bounded Contexts)

```mermaid
graph TB
    subgraph "Domínio Core: Gestão Financeira"
        subgraph "BC: Lançamentos"
            L[Lançamento]
            C[Categoria]
            CT[Conta]
            L -->|pertence a| C
            L -->|vinculado a| CT
        end
        
        subgraph "BC: Consolidado"
            CD[ConsolidadoDiario]
            S[Saldo]
            CD -->|calcula| S
        end
    end
    
    subgraph "Domínios de Suporte"
        IA[Identidade & Acesso]
        N[Notificação]
        A[Auditoria]
    end
    
    L -->|evento| CD
    IA -->|autentica| L
    L -->|registra| A
    CD -->|alerta| N
    
    style L fill:#10b981,color:#fff
    style CD fill:#3b82f6,color:#fff
    style S fill:#3b82f6,color:#fff
```

---

## 2. Mapa de Capacidades de Negócio

```mermaid
graph LR
    subgraph "Capacidades de Negócio"
        C1[C1. Capturar Lançamentos]
        C2[C2. Classificar por Categoria]
        C3[C3. Consultar Saldo Diário]
        C4[C4. Exportar Relatório]
        C5[C5. Corrigir com Auditoria]
    end
    
    subgraph "Serviços"
        SL[Serviço Lançamentos]
        SC[Serviço Consolidado]
    end
    
    C1 --> SL
    C2 --> SL
    C5 --> SL
    C3 --> SC
    C4 --> SC
    
    style C1 fill:#10b981,color:#fff
    style C2 fill:#10b981,color:#fff
    style C5 fill:#10b981,color:#fff
    style C3 fill:#3b82f6,color:#fff
    style C4 fill:#3b82f6,color:#fff
```

---

## 3. C4 — Nível de Contexto

```mermaid
graph TB
    subgraph "Usuários"
        COM[Comerciante<br/>Web/Mobile App]
    end
    
    subgraph "Sistema Verity"
        GW[API Gateway<br/>Autenticação + Rate Limit]
        SL[Serviço Lançamentos<br/>FastAPI]
        SC[Serviço Consolidado<br/>FastAPI]
    end
    
    subgraph "Sistemas Externos"
        PG[(PostgreSQL<br/>Persistência)]
        RD[(Redis<br/>Cache + Mensageria)]
    end
    
    COM -->|HTTPS + JWT| GW
    GW -->|roteia| SL
    GW -->|roteia| SC
    SL -->|grava| PG
    SL -->|publica evento| RD
    RD -->|consome| SC
    SC -->|consulta| PG
    SC -->|cache| RD
    
    style COM fill:#8b5cf6,color:#fff
    style GW fill:#06b6d4,color:#fff
    style SL fill:#10b981,color:#fff
    style SC fill:#3b82f6,color:#fff
    style PG fill:#f59e0b,color:#fff
    style RD fill:#f59e0b,color:#fff
```

---

## 4. C4 — Nível de Container

```mermaid
graph TB
    subgraph "Cliente"
        UI[Aplicação Web/Mobile]
    end
    
    subgraph "API Gateway"
        NGINX[Nginx / Kong<br/>TLS + JWT + Rate Limit]
    end
    
    subgraph "Serviço Lançamentos"
        API1[FastAPI App]
        DOM1[Domain Layer]
        APP1[Application Layer]
        INF1[Infrastructure Layer]
    end
    
    subgraph "Serviço Consolidado"
        API2[FastAPI App]
        DOM2[Domain Layer]
        APP2[Application Layer]
        INF2[Infrastructure Layer]
    end
    
    subgraph "Dados"
        PG[(PostgreSQL 15)]
        RD[(Redis 7)]
    end
    
    UI -->|HTTPS| NGINX
    NGINX -->|/lancamentos| API1
    NGINX -->|/consolidado| API2
    
    API1 --> DOM1 --> APP1 --> INF1
    INF1 --> PG
    INF1 --> RD
    
    API2 --> DOM2 --> APP2 --> INF2
    INF2 --> PG
    INF2 --> RD
    
    style UI fill:#8b5cf6,color:#fff
    style NGINX fill:#06b6d4,color:#fff
    style API1 fill:#10b981,color:#fff
    style API2 fill:#3b82f6,color:#fff
    style PG fill:#f59e0b,color:#fff
    style RD fill:#f59e0b,color:#fff
```

---

## 5. Sequência — Fluxo Principal (Happy Path)

```mermaid
sequenceDiagram
    participant C as Comerciante
    participant GW as API Gateway
    participant SL as Serviço Lançamentos
    participant RD as Redis Streams
    participant SC as Serviço Consolidado
    participant PG as PostgreSQL
    
    C->>GW: POST /lancamentos (JWT + JSON)
    GW->>SL: Valida JWT + Rate Limit
    SL->>SL: Valida domínio (Pydantic)
    SL->>PG: INSERT lancamento
    PG-->>SL: OK (201)
    SL->>RD: Publish LancamentoRegistrado
    SL-->>GW: 201 Created
    GW-->>C: Response JSON
    
    Note over SC: Processamento Assíncrono
    
    RD->>SC: Consume Event
    SC->>PG: SELECT lançamentos do dia
    PG-->>SC: Lista de lançamentos
    SC->>SC: Calcula saldo (Σ créditos - Σ débitos)
    SC->>PG: UPSERT consolidado_diario
    SC->>RD: Cache resultado (TTL 5min)
    
    C->>GW: GET /consolidado/2026-11-24
    GW->>SC: Roteia requisição
    SC->>RD: Check cache
    alt Cache Hit
        RD-->>SC: Saldo cacheado
    else Cache Miss
        SC->>PG: SELECT consolidado
        PG-->>SC: Saldo do banco
    end
    SC-->>GW: Response JSON
    GW-->>C: 200 OK
```

---

## 6. Sequência — Cenário de Falha (Resiliência)

```mermaid
sequenceDiagram
    participant C as Comerciante
    participant SL as Serviço Lançamentos
    participant RD as Redis Streams
    participant SC as Serviço Consolidado (OFFLINE)
    
    C->>SL: POST /lancamentos
    SL->>SL: Valida e persiste
    SL->>RD: Publish evento
    SL-->>C: 201 Created ✅
    
    Note over SC: ⚠️ Serviço Down (Falha)
    
    RD->>RD: Evento em fila (at-least-once delivery)
    
    Note over SC: Serviço volta ao ar
    
    RD->>SC: Replays eventos pendentes
    SC->>SC: Processa e recalcula
    SC->>RD: Atualiza cache
    
    Note over C: Nenhum dado perdido! RNF-CRIT-01 atendido
```

---

## 7. Fluxograma de Processo de Negócio

```mermaid
graph TD
    A[Comerciante realiza operação] --> B{Tipo de operação?}
    B -->|Venda/Receita| C[Crédito]
    B -->|Compra/Despesa| D[Débito]
    
    C --> E[Registrar lançamento]
    D --> E
    
    E --> F{Validações de Domínio}
    F -->|Valor > 0| G[OK]
    F -->|Valor ≤ 0| H[Rejeita: Valor inválido]
    F -->|Data ≤ hoje| G
    F -->|Data futura| I[Rejeita: Data inválida]
    
    G --> J[Persistir no PostgreSQL]
    J --> K[Publicar evento no Redis]
    K --> L[Retornar 201 Created]
    
    L --> M[Serviço Consolidado consome evento]
    M --> N[Recalcular saldo do dia]
    N --> O[Atualizar cache Redis]
    
    H --> P[Retornar 422 Unprocessable]
    I --> P
    
    style A fill:#8b5cf6,color:#fff
    style C fill:#10b981,color:#fff
    style D fill:#ef4444,color:#fff
    style L fill:#10b981,color:#fff
    style O fill:#3b82f6,color:#fff
```

---

## 8. Diagrama de Implantação (Deploy Híbrido)

```mermaid
graph TB
    subgraph "On-Premises (VMware / Azure Stack HCI)"
        PG[(PostgreSQL<br/>Dados sensíveis - LGPD)]
        FW[Firewall Corporativo]
    end
    
    subgraph "Azure (AKS / Container Apps)"
        GW1[API Gateway]
        SL1[Serviço Lançamentos<br/>Réplica 1]
        SL2[Serviço Lançamentos<br/>Réplica 2]
        ER[ExpressRoute]
    end
    
    subgraph "GCP (GKE / Cloud Run)"
        SC1[Serviço Consolidado<br/>Batch madrugada]
        CI[Cloud Interconnect]
    end
    
    subgraph "Internet"
        USR[Comerciante<br/>Web/Mobile]
    end
    
    USR -->|HTTPS| GW1
    GW1 --> SL1
    GW1 --> SL2
    SL1 -->|VPN| PG
    SL2 -->|VPN| PG
    ER <-->|Rede privada| CI
    SL1 -->|Redis Streams| SC1
    SC1 -->|VPN| PG
    
    style PG fill:#f59e0b,color:#fff
    style GW1 fill:#06b6d4,color:#fff
    style SL1 fill:#10b981,color:#fff
    style SL2 fill:#10b981,color:#fff
    style SC1 fill:#3b82f6,color:#fff
```

---

## 9. Diagrama de Estados — Ciclo de Vida do Lançamento

```mermaid
stateDiagram-v2
    [*] --> Criado: POST /lancamentos
    Criado --> Validando: Pydantic valida
    Validando --> Persistido: Validação OK
    Validando --> Rejeitado: Validação falhou
    Persistido --> Publicado: Evento Redis
    Publicado --> Consolidado: SC processa
    Consolidado --> [*]: Saldo atualizado
    
    Rejeitado --> [*]: 422 Unprocessable
    
    style Criado fill:#8b5cf6,color:#fff
    style Persistido fill:#10b981,color:#fff
    style Publicado fill:#3b82f6,color:#fff
    style Consolidado fill:#10b981,color:#fff
    style Rejeitado fill:#ef4444,color:#fff
```

---

## 10. Diagrama ER (Entidade-Relacionamento)

```mermaid
erDiagram
    LANCAMENTO ||--o{ CATEGORIA : "pertence a"
    LANCAMENTO ||--o| CONTA : "vinculado a"
    LANCAMENTO ||--o| CONSOLIDADO_DIARIO : "compõe"
    
    LANCAMENTO {
        uuid id PK
        enum tipo "DEBITO|CREDITO"
        decimal valor
        string categoria
        date data
        string descricao
        datetime criado_em
        datetime atualizado_em
    }
    
    CATEGORIA {
        int id PK
        string nome
        string tipo "RECEITA|DESPESA"
    }
    
    CONTA {
        uuid id PK
        string nome
        string tipo "CORRENTE|POUPANCA"
    }
    
    CONSOLIDADO_DIARIO {
        date data PK
        decimal total_creditos
        decimal total_debitos
        decimal saldo
        datetime atualizado_em
    }
```

---

## 📋 Resumo dos Diagramas

| # | Diagrama | Tipo | Descrição |
|---|----------|------|-----------|
| 1 | **Domínio DDD** | Graph | Bounded contexts e entidades do domínio |
| 2 | **Mapa de Capacidades** | Graph | Capacidades de negócio mapeadas para serviços |
| 3 | **C4 — Contexto** | Graph | Visão macro do sistema e atores externos |
| 4 | **C4 — Container** | Graph | Componentes internos e comunicação |
| 5 | **Sequência — Fluxo Principal** | Sequence | Happy path completo da requisição |
| 6 | **Sequência — Cenário de Falha** | Sequence | Resiliência quando consolidado está offline |
| 7 | **Fluxograma de Negócio** | Flowchart | Processo de registro e consolidação |
| 8 | **Implantação Híbrida** | Graph | Deploy em On-premises + Azure + GCP |
| 9 | **Estados do Lançamento** | State | Ciclo de vida completo da entidade |
| 10 | **Diagrama ER** | ER | Modelo de dados relacional |

---

*Documento elaborado por **Francisco Casarotto** — Arquiteto de Soluções*  
*Última atualização: Novembro/2026*
