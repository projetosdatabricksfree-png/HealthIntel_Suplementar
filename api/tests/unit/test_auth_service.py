"""Testes unitários do auth_service — sem tocar banco de dados."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from api.app.core.security import (
    gerar_access_token,
    decodificar_access_token,
    gerar_token_aleatorio,
    hash_senha,
    verificar_senha,
)
from api.app.services.auth_service import AuthError


# ---------------------------------------------------------------------------
# Testes de hash de senha
# ---------------------------------------------------------------------------

def test_hash_senha_nao_plain():
    h = hash_senha("minha_senha_123")
    assert h != "minha_senha_123"
    assert h.startswith("$2b$")


def test_verificar_senha_correta():
    h = hash_senha("correta")
    assert verificar_senha("correta", h) is True


def test_verificar_senha_errada():
    h = hash_senha("correta")
    assert verificar_senha("errada", h) is False


def test_verificar_senha_hash_invalido():
    assert verificar_senha("qualquer", "hash_invalido") is False


# ---------------------------------------------------------------------------
# Testes de JWT
# ---------------------------------------------------------------------------

def test_gerar_access_token_decodifica():
    token = gerar_access_token("uid-123", "cid-456", "owner")
    payload = decodificar_access_token(token)
    assert payload["sub"] == "uid-123"
    assert payload["tenant"] == "cid-456"
    assert payload["role"] == "owner"


def test_token_expirado_levanta_erro():
    import jwt
    from datetime import UTC, datetime, timedelta
    from api.app.core.config import get_settings

    settings = get_settings()
    payload = {
        "sub": "uid",
        "tenant": None,
        "role": "viewer",
        "iat": datetime.now(UTC),
        "exp": datetime.now(UTC) - timedelta(seconds=1),
    }
    token_expirado = jwt.encode(payload, settings.auth_jwt_secret, algorithm=settings.auth_jwt_algo)
    with pytest.raises(jwt.ExpiredSignatureError):
        decodificar_access_token(token_expirado)


def test_token_invalido_levanta_erro():
    import jwt
    with pytest.raises(jwt.InvalidTokenError):
        decodificar_access_token("token.invalido.aqui")


# ---------------------------------------------------------------------------
# Testes de geração de token
# ---------------------------------------------------------------------------

def test_gerar_token_aleatorio_tupla():
    plain, h = gerar_token_aleatorio()
    assert len(plain) > 20
    assert len(h) == 64  # SHA-256 hex


def test_tokens_diferentes():
    t1, _ = gerar_token_aleatorio()
    t2, _ = gerar_token_aleatorio()
    assert t1 != t2


# ---------------------------------------------------------------------------
# Testes de lockout (anti-brute-force)
# ---------------------------------------------------------------------------

def test_auth_error_tem_campos():
    exc = AuthError("CODIGO", "mensagem", 401)
    assert exc.codigo == "CODIGO"
    assert exc.mensagem == "mensagem"
    assert exc.status == 401


@pytest.mark.asyncio
async def test_login_lockout_ativo():
    """Conta com bloqueio ativo deve retornar 429."""
    from datetime import UTC, datetime, timedelta
    from api.app.services import auth_service

    row_mock = {
        "id": "uid-lock",
        "senha_hash": hash_senha("qualquer"),
        "status": "ativo",
        "falhas_login": 0,
        "bloqueado_ate": datetime.now(UTC) + timedelta(minutes=10),
        "email_verificado_em": datetime.now(UTC),
    }

    mock_result = MagicMock()
    mock_result.mappings.return_value.first.return_value = row_mock
    mock_session = AsyncMock()
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)

    with patch("api.app.services.auth_service.SessionLocal", return_value=mock_session):
        with pytest.raises(AuthError) as exc_info:
            await auth_service.login("user@example.com", "pass")
        assert exc_info.value.status == 429
        assert exc_info.value.codigo == "CONTA_BLOQUEADA"


@pytest.mark.asyncio
async def test_login_email_nao_verificado():
    """E-mail pendente deve retornar 403 EMAIL_NAO_VERIFICADO."""
    from api.app.services import auth_service

    row_mock = {
        "id": "uid-pend",
        "senha_hash": hash_senha("senha123"),
        "status": "pendente_email",
        "falhas_login": 0,
        "bloqueado_ate": None,
        "email_verificado_em": None,
    }

    mock_result = MagicMock()
    mock_result.mappings.return_value.first.return_value = row_mock
    mock_session = AsyncMock()
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)

    with patch("api.app.services.auth_service.SessionLocal", return_value=mock_session):
        with pytest.raises(AuthError) as exc_info:
            await auth_service.login("user@example.com", "senha123")
        assert exc_info.value.status == 403
        assert exc_info.value.codigo == "EMAIL_NAO_VERIFICADO"


@pytest.mark.asyncio
async def test_login_email_nao_encontrado_mensagem_generica():
    """E-mail não cadastrado deve retornar 401 com mensagem genérica (anti-enumeração)."""
    from api.app.services import auth_service

    mock_result = MagicMock()
    mock_result.mappings.return_value.first.return_value = None
    mock_session = AsyncMock()
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)

    with patch("api.app.services.auth_service.SessionLocal", return_value=mock_session):
        with pytest.raises(AuthError) as exc_info:
            await auth_service.login("naoexiste@example.com", "qualquer")
        assert exc_info.value.status == 401
        assert exc_info.value.mensagem == "E-mail ou senha incorretos."
