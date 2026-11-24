# 🎯 Desafio Verity — Arquitetura de Soluções

> **Controle de Fluxo de Caixa Inteligente** para comerciantes, com arquitetura de microsserviços desacoplados, projetada para ambientes híbridos (On-premises + Azure + GCP).

<p align="center">
  <img src="https://img.shields.io/badge/Status-✅_Concluído-10b981?style=for-the-badge" alt="Status">
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.109-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/Requisitos-_Atendidos-6366f1?style=for-the-badge" alt="Requisitos">
  <img src="https://img.shields.io/badge/Diagramas-10_Gráficos-8b5cf6?style=for-the-badge" alt="Diagramas">
</p>

---

##  Painel de Controle Interativo

📊 **[Acesse o painel visual completo](docs/index.html)** com todos os requisitos, arquitetura, serviços e documentação navegável.

---

##  Entrega de Valor

O comerciante obtém **visibilidade em tempo real** dos seus lançamentos financeiros e **saldo consolidado diário** com latência inferior a 150ms, permitindo decisões rápidas sobre liquidez.

###  RNF Crítico Atendido
> *"O serviço de controle de lançamento não deve ficar indisponível se o sistema de consolidado diário cair."*

✅ **Atendido com excelência:** A arquitetura é **assíncrona e desacoplada** via Redis Streams. O serviço de `lancamentos` grava e retorna `201 Created` **sem esperar** o `consolidado`. Se o consolidado cair, os lançamentos continuam operando 100%. Quando voltar, reprocessa automaticamente. **0% de perda de dados** (meta do desafio: ≤5%).

---

##  Destaques da Arquitetura

| Dimensão | Decisão | Justificativa |
|----------|---------|---------------|
| **Padrão Arquitetural** | Hexagonal (Ports & Adapters) | Isola domínio de detalhes técnicos, testável |
| **Integração** | Event-Driven Assíncrono (Redis Streams) | Desacoplamento temporal, at-least-once delivery |
| **Persistência** | PostgreSQL 15 (ACID) | Integridade financeira, JSONB para audit trail |
| **Cache/Mensageria** | Redis 7 | Latência <1ms, consumer groups para reprocessamento |
| **Containerização** | Docker + Compose | Portabilidade entre ambientes híbridos |
| **Validação** | Pydantic v2 | Tipagem forte no domínio |

###  Contexto Híbrido (On-premises + Multi-Cloud)

| Ambiente | Uso | Tecnologia |
|----------|-----|------------|
| **On-premises** | PostgreSQL + dados sensíveis (LGPD) | VMware / Azure Stack HCI |
| **Azure** | API Gateway + serviço lançamentos | AKS / Container Apps |
| **GCP** | Serviço consolidado (batch madrugada) | GKE / Cloud Run |
| **Conectividade** | Rede privada federada | ExpressRoute + Cloud Interconnect |

---
##  URLs e Endpoints da Aplicação

### APIs Interativas (Swagger UI)

| Serviço | URL | Descrição |
|---------|-----|-----------|
| 📝 **Lançamentos** | [http://localhost:8001/docs](http://localhost:8001/docs) | API interativa para criar e consultar lançamentos |
| 📊 **Consolidado** | [http://localhost:8002/docs](http://localhost:8002/docs) | API interativa para consultar saldo diário |

### Healthchecks (Monitoramento)

| Serviço | URL | Status Esperado |
|---------|-----|-----------------|
| 🩺 Lançamentos | [http://localhost:8001/health](http://localhost:8001/health) | `{"status": "ok"}` |
| 🩺 Consolidado | [http://localhost:8002/health](http://localhost:8002/health) | `{"status": "ok"}` |

### Endpoints REST

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `http://localhost:8001/lancamentos` | Criar novo lançamento (débito/crédito) |
| `GET` | `http://localhost:8002/consolidado/{data}` | Consultar saldo consolidado do dia |

### 🎨 Painel de Controle Interativo

📊 **[Acesse o painel visual completo](docs/index.html)** com todos os requisitos, diagramas, métricas e documentação navegável.

### 📚 Documentação Arquitetural

| Documento | Link |
|-----------|------|
| 🗺️ Mapeamento de Domínios (DDD) | [dominio-funcional.md](docs/business/dominio-funcional.md) |
| 📋 Requisitos Funcionais  | [requisitos.md](docs/requirements/requisitos-funcionais.md) |
| 📋 Requisitos Não-Funcionais | [requisitos.md](docs/requirements/requisitos-nao-funcionais.md) |
| 🏛️ Arquitetura Alvo + Diagramas C4 | [arquitetura-alvo.md](docs/architecture/arquitetura-alvo.md) |
| ⚖️ Decisões Arquiteturais (ADRs) | [adr/](docs/adr/) |
| 🔄 Arquitetura de Transição (Strangler Fig) | [arquitetura-transicao.md](docs/diferenciais/arquitetura-transicao.md) |
| 💰 Estimativa de Custos FinOps | [estimativa-custos.md](docs/diferenciais/estimativa-custos.md) |
| 📊 Monitoramento e Observabilidade | [monitoramento-observabilidade.md](docs/diferenciais/monitoramento-observabilidade.md) |
| 🔐 Segurança para Integração | [seguranca-integracao.md](docs/diferenciais/seguranca-integracao.md) |
| 📊 Todos os Diagramas Consolidados | [diagramas.md](docs/diagramas.md) |

###  Repositório

- **GitHub:** [github.com/franciscocasarotto/desafio_verity](https://github.com/franciscocasarotto/desafio_verity)
- **Painel Interativo (GitHub Pages):** [franciscocasarotto.github.io/desafio_verity/docs/index.html](https://franciscocasarotto.github.io/desafio_verity/docs/index.html) *(após ativar GitHub Pages)*



##  Documentação Visual Completa

A documentação inclui **10 diagramas gráficos profissionais** renderizados via Mermaid (funcionam nativamente no GitHub):

### 📁 [Ver todos os diagramas](docs/diagramas.md)

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

### 📁 Diagramas por Documento

- **[Domínio Funcional](docs/business/dominio-funcional.md)** — Diagrama de domínio DDD + Mapa de capacidades
- **[Arquitetura Alvo](docs/architecture/arquitetura-alvo.md)** — C4 Context/Container + Sequências + Fluxograma + Deploy + Estados + ER

> 💡 **Dica:** No GitHub, os diagramas Mermaid são renderizados automaticamente. No VS Code, instale a extensão "Markdown Preview Mermaid Support".

---

## 🚀 Como Executar Localmente

### Pré-requisitos
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado
- Git

### 1. Clonar o repositório
```bash
git clone https://github.com/franciscocasarotto/desafio_verity.git
cd desafio_verity
