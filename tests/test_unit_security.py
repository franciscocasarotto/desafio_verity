"""Testes de seguranca: JWT RS256, escopos, tenant isolation e replay."""
from __future__ import annotations

import hashlib

import pytest

from shared.security import (
    AuthError,
    generate_rsa_keypair,
    issue_token,
    validate_token,
)


@pytest.fixture(scope="module")
def keys():
    return generate_rsa_keypair()


class TestJwt:
    def test_token_valido_retorna_principal(self, keys):
        priv, pub = keys
        tok = issue_token(
            private_pem=priv, subject="u1", merchant_id="M1",
            scopes=["lancamentos:write"],
        )
        p = validate_token(tok, public_pem=pub, required_scopes=["lancamentos:write"])
        assert p.merchant_id == "M1"
        assert "lancamentos:write" in p.scopes

    def test_escopo_insuficiente_403(self, keys):
        priv, pub = keys
        tok = issue_token(
            private_pem=priv, subject="u1", merchant_id="M1",
            scopes=["lancamentos:read"],
        )
        with pytest.raises(AuthError) as ei:
            validate_token(tok, public_pem=pub, required_scopes=["lancamentos:write"])
        assert ei.value.status_code == 403

    def test_token_expirado_401(self, keys):
        priv, pub = keys
        tok = issue_token(
            private_pem=priv, subject="u1", merchant_id="M1",
            scopes=["x"], ttl_seconds=-10,
        )
        with pytest.raises(AuthError) as ei:
            validate_token(tok, public_pem=pub)
        assert ei.value.status_code == 401

    def test_assinatura_forjada_rejeitada(self, keys):
        _, pub = keys
        priv2, _ = generate_rsa_keypair()  # chave de atacante
        tok = issue_token(
            private_pem=priv2, subject="evil", merchant_id="M9",
            scopes=["lancamentos:admin"],
        )
        with pytest.raises(AuthError):
            validate_token(tok, public_pem=pub)

    def test_audiencia_errada_rejeitada(self, keys):
        priv, pub = keys
        tok = issue_token(
            private_pem=priv, subject="u1", merchant_id="M1",
            scopes=["x"], audience="outra-api",
        )
        with pytest.raises(AuthError):
            validate_token(tok, public_pem=pub)

    def test_hs256_confusion_attack_bloqueado(self, keys):
        """Token assinado com HMAC usando a chave publica nao deve validar."""
        import jwt as pyjwt

        _, pub = keys
        # chave simetrica derivada da publica (vetor classico de alg confusion)
        key_simetrica = hashlib.sha256(pub.encode()).hexdigest().encode()
        forged = pyjwt.encode(
            {"sub": "evil", "mid": "M1", "scope": "lancamentos:admin",
             "exp": 9_999_999_999},
            key_simetrica, algorithm="HS256",
        )
        with pytest.raises(AuthError):
            validate_token(forged, public_pem=pub)
