# Monitoramento e Observabilidade

A arquitetura adota os **Três Pilares da Observabilidade** para garantir que a equipe de operações (NOC/SRE) e o negócio tenham visibilidade total.

## 1. Métricas (Metrics)
- **Infraestrutura:** CPU, Memória, IOPS do PostgreSQL, Hit Ratio do Redis.
- **Aplicação (RED Method):** 
  - *Rate:* Requisições por segundo (ex: picos de lançamentos no fim do dia).
  - *Errors:* Taxa de erros HTTP 5xx e 4xx.
  - *Duration:* Latência p95 e p99 das APIs.
- **Negócio:** Volume financeiro total processado por hora, número de lançamentos por categoria.

## 2. Logs (Logs)
- **Padrão:** Logs estruturados em JSON (via `loguru` ou `structlog` em Python).
- **Correlação:** Todo log contém um `trace_id` e `span_id` para rastrear a requisição do API Gateway até o banco de dados.
- **Níveis:** `INFO` para operações de negócio, `WARN` para retries, `ERROR` para falhas críticas.
- **Ferramenta Sugerida:** ELK Stack (Elasticsearch, Logstash, Kibana) ou Loki + Grafana.

## 3. Rastreamento Distribuído (Traces)
- **Padrão:** OpenTelemetry (OTel).
- **Implementação:** Instrumentação automática no FastAPI e no driver do PostgreSQL.
- **Backend:** Jaeger ou Zipkin para visualizar o fluxo da requisição e identificar gargalos (ex: query lenta no banco).

## Alertas Proativos (ITSM / ServiceNow)
- **Crítico:** Latência p95 > 1s por mais de 5 minutos -> Abre Incidente P1 no ServiceNow automaticamente via webhook.
- **Aviso:** Uso de CPU > 80% -> Abre Requisição de Mudança (RFC) para escalar horizontalmente.

## 4. Diagrama dos 3 Pilares da Observabilidade

```mermaid
graph TB
    subgraph "📊 Observabilidade"
        subgraph "Pilar 1: Métricas"
            M1[RED Method<br/>Rate, Errors, Duration]
            M2[Métricas de Negócio<br/>Volume financeiro/hora]
        end
        
        subgraph "Pilar 2: Logs"
            L1[Logs Estruturados JSON]
            L2[Correlação via trace_id]
        end
        
        subgraph "Pilar 3: Traces"
            T1[OpenTelemetry]
            T2[Jaeger/Zipkin]
        end
    end
    
    subgraph "🔔 Alertas ITSM"
        S1[ServiceNow<br/>Incidentes P1]
        S2[Webhooks automáticos]
    end
    
    M1 --> S1
    L1 --> S1
    T1 --> S2
    
    style M1 fill:#10b981,color:#fff
    style L1 fill:#3b82f6,color:#fff
    style T1 fill:#8b5cf6,color:#fff
    style S1 fill:#ef4444,color:#fff  