"""Seguranca compartilhada: autenticacao JWT (RS256) e autorizacao por escopo.

Decisoes (ver docs/adr/ADR-005-seguranca.md):
- Autenticacao via OIDC/JWT assinado com RS256 (chave privada no IdP / Azure AD
  ou Keycloak on-prem; servicos validam apenas com a chave publica -> zero
  segredo compartilhado entre servicos).
- Autorizacao granular por escopo (OAuth2 scope-based access control), no estilo
  "principio do menor privilegio".
- Em producao, alem do JWT, o mTLS e aplicado na malha de servico (Istio/Linkerd)
  e as APIs sao expostas apenas atras do API Gateway.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Iterable

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


class AuthError(Exception):
    """Erro de autenticacao/autorizacao (mapeado para HTTP 401/403)."""

    def __init__(self, message: str, status_code: int = 401) -> None:
        super().__init__(message)
        self.status_code = status_code


@dataclass(frozen=True)
class Principal:
    """Identidade autenticada que consome a API."""

    subject: str
    merchant_id: str
    scopes: frozenset[str] = field(default_factory=frozenset)

    def has_scope(self, required: Iterable[str]) -> bool:
        return set(required).issubset(set(self.scopes))


def generate_rsa_keypair() -> tuple[str, str]:
    """Gera par RS256 (uso em dev/testes; em prod a chave vem do cofre/IdP)."""
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    public_pem = key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()
    return private_pem, public_pem


def issue_token(
    *,
    private_pem: str,
    subject: str,
    merchant_id: str,
    scopes: list[str],
    issuer: str = "fluxo-caixa-idp",
    audience: str = "fluxo-caixa-api",
    ttl_seconds: int = 3600,
) -> str:
    now = int(time.time())
    payload = {
        "sub": subject,
        "mid": merchant_id,
        "scope": " ".join(scopes),
        "iss": issuer,
        "aud": audience,
        "iat": now,
        "exp": now + ttl_seconds,
    }
    return jwt.encode(payload, private_pem, algorithm="RS256")


def validate_token(
    token: str,
    *,
    public_pem: str,
    issuer: str = "fluxo-caixa-idp",
    audience: str = "fluxo-caixa-api",
    required_scopes: Iterable[str] = (),
) -> Principal:
    """Valida assinatura, expiracao, emissor, audiencia e escopos exigidos."""
    try:
        claims = jwt.decode(
            token,
            public_pem,
            algorithms=["RS256"],  # lista fechada: bloqueia alg confusion attack
            audience=audience,
            issuer=issuer,
            options={"require": ["exp", "sub"]},
        )
    except jwt.ExpiredSignatureError as exc:
        raise AuthError("token expirado", 401) from exc
    except jwt.InvalidTokenError as exc:
        raise AuthError("token invalido", 401) from exc

    principal = Principal(
        subject=claims["sub"],
        merchant_id=claims.get("mid", ""),
        scopes=frozenset(claims.get("scope", "").split()),
    )
    missing = set(required_scopes) - set(principal.scopes)
    if missing:
        raise AuthError(f"escopos insuficientes: {sorted(missing)}", 403)
    return principal


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
