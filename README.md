# Desafio Verity — Arquitetura de Soluções

> Controle de fluxo de caixa diário com consolidação de saldo para comerciantes.

## 🎯 Entrega de Valor
O comerciante obtém **visibilidade em tempo real** dos seus lançamentos financeiros 
e **saldo consolidado diário** com latência <150ms, permitindo decisões rápidas 
sobre liquidez.

## 🏗️ Arquitetura
- **Padrão**: Hexagonal (Ports & Adapters) com 2 serviços desacoplados
- **Comunicação**: Event-driven via Redis Streams (at-least-once)
- **Persistência**: PostgreSQL (ACID) + Redis (cache TTL 5min)
- **Segurança**: JWT, rede interna isolada, rate limiting

📎 Detalhes em [`docs/architecture/arquitetura-alvo.md`](docs/architecture/arquitetura-alvo.md)

## 🚀 Como Executar Localmente

### Pré-requisitos
- Docker + Docker Compose
- Python 3.11+ (para desenvolvimento/testes)

### 1. Clonar e configurar
```bash
git clone https://github.com/franciscocasarotto/desafio_verity.git
cd desafio_verity
cp .env.example .env