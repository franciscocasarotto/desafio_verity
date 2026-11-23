# C4 — Container Diagram

```mermaid
graph TB
    subgraph Frontend
        UI[Web/Mobile App]
    end
    subgraph Backend
        GW[API Gateway]
        SL[Serviço Lançamentos<br/>FastAPI]
        SC[Serviço Consolidado<br/>FastAPI]
    end
    subgraph Data
        PG1[(PostgreSQL<br/>lancamentos)]
        PG2[(PostgreSQL<br/>consolidado)]
        RS[(Redis Streams<br/>eventos)]
        RC[(Redis Cache<br/>consolidado)]
    end
    
    UI -->|HTTPS| GW
    GW --> SL
    GW --> SC
    SL --> PG1
    SL -->|publish| RS
    RS -->|consume| SC
    SC --> PG2
    SC --> RC
    SC -.->|cache read| RC
