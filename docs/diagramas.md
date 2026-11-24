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

---

## 2. Mapa de Capacidades de Negócios

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


---

## 1. Domínio DDD (Bounded Contexts)

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
