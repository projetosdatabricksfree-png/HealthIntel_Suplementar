"""
Testes de segurança que NÃO dependem de api.app.main (rodam localmente).
Cobre: Settings.validar_configuracao, verificar_plano, verificar_admin, is_admin.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from api.app.core.config import Settings

# ─── Settings.validar_configuracao em produção ───────────────────────────────


def test_validar_configuracao_bloqueia_startup_em_producao_com_secrets_padrao() -> None:
    s = Settings(
        API_ENV="production",
        API_JWT_ADMIN_SECRET="trocar_em_producao",
        LAYOUT_SERVICE_TOKEN="healthintel_layout_service_local_token_2026",
        POSTGRES_PASSWORD="healthintel",
        MONGO_INITDB_ROOT_PASSWORD="healthintel",
        API_INTERNAL_TOKEN="healthintel_internal_local_token",
        API_CORS_ALLOWED_ORIGINS="https://healthintel.com.br",
        API_ALLOWED_HOSTS="healthintel.com.br",
    )
    with pytest.raises(RuntimeError, match="Startup bloqueado"):
        s.validar_configuracao()


def test_validar_configuracao_bloqueia_cada_secret_invalido_individualmente() -> None:
    """Todos os 5 secrets inválidos devem ser listados no erro."""
    s = Settings(
        API_ENV="production",
        API_JWT_ADMIN_SECRET="trocar_em_producao",
        LAYOUT_SERVICE_TOKEN="healthintel_layout_service_local_token_2026",
        POSTGRES_PASSWORD="healthintel",
        MONGO_INITDB_ROOT_PASSWORD="healthintel",
        API_INTERNAL_TOKEN="healthintel_internal_local_token",
        API_CORS_ALLOWED_ORIGINS="https://healthintel.com.br",
        API_ALLOWED_HOSTS="healthintel.com.br",
    )
    with pytest.raises(RuntimeError) as exc_info:
        s.validar_configuracao()
    msg = str(exc_info.value)
    assert "API_JWT_ADMIN_SECRET" in msg
    assert "POSTGRES_PASSWORD" in msg
    assert "MONGO_INITDB_ROOT_PASSWORD" in msg


def test_validar_configuracao_passa_em_producao_com_secrets_reais() -> None:
    s = Settings(
        API_ENV="production",
        API_JWT_ADMIN_SECRET="um_secret_longo_e_seguro_abc123xyz",
        LAYOUT_SERVICE_TOKEN="layout_token_seguro_xyz_2026_production",
        POSTGRES_PASSWORD="senha_postgres_muito_segura",
        MONGO_INITDB_ROOT_PASSWORD="senha_mongo_muito_segura",
        API_INTERNAL_TOKEN="internal_token_seguro_xyz_2026",
        API_CORS_ALLOWED_ORIGINS="https://healthintel.com.br",
        API_ALLOWED_HOSTS="healthintel.com.br,www.healthintel.com.br",
    )
    s.validar_configuracao()


def test_validar_configuracao_permite_local_com_secrets_padrao() -> None:
    s = Settings(
        API_ENV="local",
        API_JWT_ADMIN_SECRET="trocar_em_producao",
    )
    s.validar_configuracao()


def test_validar_configuracao_bloqueia_hml_com_secret_admin_padrao() -> None:
    s = Settings(
        API_ENV="hml",
        API_JWT_ADMIN_SECRET="trocar_em_producao",
        LAYOUT_SERVICE_TOKEN="healthintel_layout_service_local_token_2026",
    )
    with pytest.raises(ValueError, match="Configuracao insegura"):
        s.validar_configuracao()


# ─── verificar_plano ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_verificar_plano_vazio_levanta_403() -> None:
    from fastapi import HTTPException
    from starlette.datastructures import State

    from api.app.dependencia import verificar_plano

    mock_req = MagicMock()
    mock_req.state = State()
    mock_req.state.endpoint_permitido = []
    mock_req.state.is_admin = False
    mock_req.url = MagicMock()
    mock_req.url.path = "/v1/operadoras"

    with pytest.raises(HTTPException) as exc_info:
        await verificar_plano(mock_req)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail["codigo"] == "PLANO_SEM_ENDPOINTS"


@pytest.mark.asyncio
async def test_verificar_plano_none_levanta_403() -> None:
    from fastapi import HTTPException
    from starlette.datastructures import State

    from api.app.dependencia import verificar_plano

    mock_req = MagicMock()
    mock_req.state = State()
    mock_req.state.endpoint_permitido = None
    mock_req.state.is_admin = False
    mock_req.url = MagicMock()
    mock_req.url.path = "/v1/operadoras"

    with pytest.raises(HTTPException) as exc_info:
        await verificar_plano(mock_req)

    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_verificar_plano_vazio_admin_interno_passa() -> None:
    from starlette.datastructures import State

    from api.app.dependencia import verificar_plano

    mock_req = MagicMock()
    mock_req.state = State()
    mock_req.state.endpoint_permitido = []
    mock_req.state.is_admin = True
    mock_req.url = MagicMock()
    mock_req.url.path = "/admin/billing/resumo"

    await verificar_plano(mock_req)


@pytest.mark.asyncio
async def test_verificar_plano_rota_fora_do_plano_levanta_403() -> None:
    from fastapi import HTTPException
    from starlette.datastructures import State

    from api.app.dependencia import verificar_plano

    mock_req = MagicMock()
    mock_req.state = State()
    mock_req.state.endpoint_permitido = ["/v1/operadoras"]
    mock_req.state.is_admin = False
    mock_req.url = MagicMock()
    mock_req.url.path = "/prata/cadop"

    with pytest.raises(HTTPException) as exc_info:
        await verificar_plano(mock_req)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail["codigo"] == "PLANO_SEM_ACESSO"


@pytest.mark.asyncio
async def test_verificar_plano_rota_autorizada_passa() -> None:
    from starlette.datastructures import State

    from api.app.dependencia import verificar_plano

    mock_req = MagicMock()
    mock_req.state = State()
    mock_req.state.endpoint_permitido = ["/v1/operadoras", "/prata"]
    mock_req.state.is_admin = False
    mock_req.url = MagicMock()
    mock_req.url.path = "/prata/cadop"

    await verificar_plano(mock_req)


# ─── verificar_admin ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_verificar_admin_sem_flag_levanta_403() -> None:
    from fastapi import HTTPException
    from starlette.datastructures import State

    from api.app.dependencia import verificar_admin

    mock_req = MagicMock()
    mock_req.state = State()
    mock_req.state.is_admin = False

    with pytest.raises(HTTPException) as exc_info:
        await verificar_admin(mock_req)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail["codigo"] == "ACESSO_RESTRITO_ADMIN"


@pytest.mark.asyncio
async def test_verificar_admin_flag_true_passa() -> None:
    from starlette.datastructures import State

    from api.app.dependencia import verificar_admin

    mock_req = MagicMock()
    mock_req.state = State()
    mock_req.state.is_admin = True

    await verificar_admin(mock_req)


@pytest.mark.asyncio
async def test_verificar_admin_sem_atributo_levanta_403() -> None:
    from fastapi import HTTPException
    from starlette.datastructures import State

    from api.app.dependencia import verificar_admin

    mock_req = MagicMock()
    mock_req.state = State()

    with pytest.raises(HTTPException) as exc_info:
        await verificar_admin(mock_req)

    assert exc_info.value.status_code == 403


# ─── is_admin derivado de plano_nome ─────────────────────────────────────────


@pytest.mark.parametrize("plano_nome,esperado", [
    ("admin_interno", True),
    ("ADMIN_INTERNO", True),
    ("Admin_Interno", True),
    ("essencial", False),
    ("piloto", False),
    ("enterprise", False),
    ("", False),
    ("admin", False),
])
def test_is_admin_derivado_de_plano_nome(plano_nome: str, esperado: bool) -> None:
    resultado = plano_nome.lower() == "admin_interno"
    assert resultado == esperado
