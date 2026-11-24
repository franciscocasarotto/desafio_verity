# Desafio Verity — Arquitetura de Soluções

> Controle de fluxo de caixa diário com consolidação de saldo para comerciantes.
>  Arquitetura híbrida: On-premises (VMware/Azure Stack HCI) + Multi-cloud (Azure + GCP).


##  Entrega de Valor
O comerciante obtém **visibilidade em tempo real** dos seus lançamentos financeiros 
e **saldo consolidado diário** com latência <150ms, permitindo decisões rápidas 
sobre liquidez.

##  Arquitetura
- **Integração Assíncrona:** Redis Streams com consumer groups (at-least-once)
- **Resiliência:** Healthchecks, restart automático, rede interna isolada
- **Segurança:** JWT, princípio do menor privilégio, validação rigorosa (Pydantic)
- **Portabilidade Híbrida:** Containers executáveis em VMware, Azure AKS ou GCP GKE
- **FinOps:** Comparativo Azure vs. GCP em BRL (região Brasil)
-  **Portabilidade Híbrida (Multi-Cloud/On-Prem):** A solução é agnóstica à infraestrutura, sendo executável via containers em ambientes on-premises (VMware, Azure Stack HCI) ou orquestrada em nuvem (Azure AKS, Google GKE), garantindo soberania de dados e elasticidade conforme a necessidade do negócio.

##  Requisitos Diferenciais 

Além da implementação funcional, este repositório entrega artefatos de nível corporativo para garantir a viabilidade, segurança e operação da solução em produção:

-  [Arquitetura de Transição (Migração de Legado)](docs/diferenciais/arquitetura-transicao.md) - Estratégia Strangler Fig e mitigação de riscos.
-  [Estimativa de Custos e FinOps](docs/diferenciais/estimativa-custos.md) - Comparativo Cloud vs. On-Premise/Híbrido.
-  [Monitoramento e Observabilidade](docs/diferenciais/monitoramento-observabilidade.md) - Os 3 pilares e integração com ITSM/ServiceNow.
-  [Segurança para Integração de Serviços](docs/diferenciais/seguranca-integracao.md) - Zero Trust, OAuth2, DevSecOps e OWASP.

 Detalhes em [`docs/architecture/arquitetura-alvo.md`](docs/architecture/arquitetura-alvo.md)

##  Como Executar Localmente

### Pré-requisitos
- Docker + Docker Compose
- Python 3.11+ (para desenvolvimento/testes)

### 1. Clonar e configurar
```bash
git clone https://github.com/franciscocasarotto/desafio_verity.git
cd desafio_verity
docker compose up --build -d

