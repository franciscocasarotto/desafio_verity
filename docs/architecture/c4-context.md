# C4 — Context Diagram

```mermaid
graph TB
    Comerciante([Comerciante])
    SL[Sistema de Controle<br/>de Lançamentos]
    SC[Sistema de<br/>Consolidação Diária]
    
    Comerciante -->|Cria/consulta lançamentos| SL
    Comerciante -->|Consulta saldo diário| SC
    SL -.->|Eventos de lançamento| SC

    
