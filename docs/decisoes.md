# Decisões técnicas

Aqui explico o porquê das escolhas principais. Mais importante que a tecnologia em si é o raciocínio por trás dela.

---

## 1. Por que mensageria assíncrona (e não REST síncrono)?

**Contexto:** o enunciado deixa claro que o serviço de lançamentos precisa continuar funcionando mesmo se o consolidado cair.

**Decisão:** RabbitMQ entre os serviços. O lançamentos publica um evento `LancamentoCriado` e responde imediatamente ao usuário. O consolidado consome no seu ritmo.

**Trade-offs:**
- ✅ Isolamento total de falhas (atende o requisito principal)
- ✅ Picos de 50 req/s são absorvidos pela fila
- ✅ DLQ para mensagens que falharem
- ❌ Consistência eventual no consolidado (aceitável para relatório diário)
- ❌ Complexidade operacional do broker

**Alternativas consideradas:**
- REST síncrono: descartado porque viola o requisito de isolamento.
- Kafka: overkill para o volume. RabbitMQ resolve bem e roda on-prem sem problema.
- Polling no banco: anti-pattern, gera carga desnecessária.

---

## 2. Por que CQRS no consolidado?

**Contexto:** o consolidado é leitura intensiva (50 req/s) e escrita esporádica (só quando chega evento novo).

**Decisão:** separar o modelo de escrita (PostgreSQL transacional dos lançamentos) do modelo de leitura (tabela de projeção `consolidado_diario` + Redis na frente).

**Trade-offs:**
- ✅ Consultas em < 10ms com cache
- ✅ Escala leitura e escrita independentemente
- ❌ Lag de alguns segundos entre lançamento e consolidado (aceitável)

---

## 3. Por que Python + FastAPI?

Linguagem que domino, ecossistema maduro, performance mais que suficiente para 50 req/s. Para volume muito maior (>10k req/s) eu consideraria Go, mas aqui seria overkill.

FastAPI pela validação automática com Pydantic, documentação OpenAPI de graça e suporte nativo a async (importante para I/O bound como banco e mensageria).

---

## 4. Por que PostgreSQL e não MySQL?

Para dados financeiros, ACID é inegociável. PostgreSQL tem features melhores (JSONB, partitioning, replicações mais flexíveis) e é a escolha padrão em projetos que eu já vi em ambientes enterprise.

---

## 5. Distribuição híbrida (On-prem + Azure + GCP)

Achei importante considerar o ambiente real de vocês. Minha proposta:

- **On-prem**: carga estável e dados sensíveis (lançamentos + DB transacional). Custo marginal baixo aproveitando hardware já amortizado.
- **Azure**: carga elástica (consolidado, cache, mensageria). Escala nos picos sem custo fixo.
- **GCP**: DR do consolidado e analytics futuro (BigQuery). Evita lock-in em um único cloud provider.

Kubernetes em todos os lados, gerenciado via Azure Arc. Terraform como IaC.

---

## 6. Estratégia de migração (se houver legado)

Se existir um sistema legado, usaria **Strangler Fig Pattern**: API Gateway roteando gradualmente as funcionalidades para os novos serviços, mantendo o legado ativo até a substituição completa. Migração big bang é pedir para ter problema.

---

## O que eu faria com mais tempo

- Event Sourcing completo (audit trail imutável)
- Outbox pattern para garantir entrega de eventos (hoje o publish pode falhar silenciosamente)
- Testes de carga com Locust para validar os 50 req/s
- Service mesh (Istio) para mTLS e observabilidade avançada
- Multi-tenancy se o sistema for virar SaaS