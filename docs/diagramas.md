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
