# Critérios de Segurança para Consumo e Integração

A exposição das APIs (internas e externas) segue o modelo **Zero Trust** e as diretrizes da OWASP API Security Top 10.

## 1. Autenticação e Autorização
- **Protocolo:** OAuth 2.0 com OpenID Connect (OIDC).
- **Tokens:** JWT (JSON Web Tokens) com tempo de vida curto (15 minutos) e Refresh Tokens seguros.
- **Escopos (Scopes):** 
  - `lancamentos:write` (apenas PDVs e gerentes).
  - `consolidado:read` (dashboards e contadores).
- **RBAC:** Integração com o Active Directory (Azure AD / Entra ID) para gestão centralizada de identidades.

## 2. Proteção de Tráfego e Rede
- **Criptografia em Trânsito:** TLS 1.3 obrigatório em todos os endpoints públicos.
- **Criptografia em Repouso:** TDE (Transparent Data Encryption) no PostgreSQL e criptografia AES-256 no Redis.
- **Isolamento de Rede:** O banco de dados e o Redis residem em sub-redes privadas (sem IP público), acessíveis apenas via VNet/Peering.

## 3. Prevenção de Abuso (Rate Limiting & Throttling)
- **Limites:** 
  - 100 requisições/minuto por usuário (evita scraping e ataques de força bruta).
  - 10 requisições/segundo para criação de lançamentos (proteção contra picos maliciosos).
- **WAF (Web Application Firewall):** Proteção contra SQL Injection, XSS e DDoS na borda da rede.

## 4. Segurança no Ciclo de Vida (DevSecOps)
- **SAST/DAST:** Varredura de código (SonarQube) e testes de penetração automatizados (OWASP ZAP) no pipeline de CI/CD.
- **Gestão de Secrets:** Nenhuma credencial é hardcoded. Uso de Azure Key Vault ou HashiCorp Vault para injeção de secrets em runtime.
- **Supply Chain:** Assinatura de imagens Docker (Cosign/Notary) para garantir que apenas imagens verificadas rodem em produção.
