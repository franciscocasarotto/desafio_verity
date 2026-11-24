# 📊 Diagramas Gráficos — Desafio Verity

Este documento contém a representação visual completa da arquitetura, processos e dados do projeto, renderizados via Mermaid.

> 💡 **Dica:** No GitHub, os diagramas Mermaid são renderizados automaticamente. No VS Code, instale a extensão "Markdown Preview Mermaid Support".

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
