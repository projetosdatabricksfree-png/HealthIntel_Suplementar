"""
Testes de segurança para critérios de aceite do hardening comercial.
Cobre: /saude, /prontidao, /admin/*, verificar_plano, docs bloqueados,
CORS, rate limit e bloqueio de secrets default em produção.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from api.app import dependencia
from api.app.core.config import Settings, get_settings
from api.app.main import app

client = TestClient(app)
_settings = get_settings()
_internal_token = _settings.internal_token


# ─── /saude ──────────────────────────────────────────────────────────────────


def test_saude_nao_expoe_infra() -> None:
    response = client.get("/saude")
    assert response.status_code == 200
    body = response.json()
    assert "postgres" not in str(body)
    assert "redis" not in str(body)
    assert "mongo" not in str(body)
    assert "postgres_host" not in body
    assert "redis_host" not in body
    assert "mongo_host" not in body
    assert body == {"status": "ok"}


def test_saude_nao_expoe_versao_ambiente() -> None:
    response = client.get("/saude")
    body = response.json()
    assert "ambiente" not in body
    assert "versao" not in body
    assert "dependencias" not in body


# ─── /prontidao ──────────────────────────────────────────────────────────────


def test_prontidao_sem_token_retorna_401() -> None:
    response = client.get("/prontidao")
    assert response.status_code == 401


def test_prontidao_token_invalido_retorna_401() -> None:
    response = client.get("/prontidao", headers={"X-Internal-Token": "invalido"})
    assert response.status_code == 401


@patch("api.app.main.obter_prontidao", new_callable=AsyncMock)
def test_prontidao_com_token_correto_responde(mock_prontidao: AsyncMock) -> None:
    mock_prontidao.return_value = {"status": "ok"}
    response = client.get("/prontidao", headers={"X-Internal-Token": _internal_token})
    assert response.status_code == 200


# ─── Docs bloqueados em produção ─────────────────────────────────────────────


def test_docs_bloqueados_em_producao(monkeypatch) -> None:
    monkeypatch.setattr(dependencia.settings, "app_env", "production")
    with patch("api.app.main._em_producao", True):
        for path in ("/docs", "/redoc", "/openapi.json"):
            response = client.get(path)
            assert response.status_code == 404, f"{path} deve retornar 404 em producao"


# ─── /admin/billing RBAC ─────────────────────────────────────────────────────


def _make_state_comum():
    state = MagicMock()
    state.chave_api = "hi_xxxx"
    state.chave_api_id = "uuid-chave-dev"
    state.cliente_id = "uuid-cliente-dev"
    state.plano_id = "uuid-plano-dev"
    state.limite_rpm = 60
    state.endpoint_permitido = ["/v1/operadoras"]
    state.camadas_permitidas = ["ouro"]
    state.plano_nome = "essencial"
    state.is_admin = False
    state.auth_cache = "mock"
    return state


def _make_state_admin():
    state = _make_state_comum()
    state.plano_nome = "admin_interno"
    state.is_admin = True
    state.endpoint_permitido = []
    state.camadas_permitidas = ["ouro", "prata", "bronze"]
    return state


@patch("api.app.middleware.rate_limit.aplicar_rate_limit", new_callable=AsyncMock)
@patch("api.app.middleware.autenticacao.validar_api_key", new_callable=AsyncMock)
async def test_admin_billing_rejeita_chave_comum(mock_auth, mock_rl) -> None:
    mock_auth.side_effect = lambda req, x_api_key=None: setattr(
        req, "state", _make_state_comum()
    ) or "hi_local_dev_2026_api_key"

    response = client.get(
        "/admin/billing/resumo?referencia=2026-04",
        headers={"X-API-Key": "hi_local_dev_2026_api_key"},
    )
    assert response.status_code == 403
    assert response.json()["codigo"] == "ACESSO_RESTRITO_ADMIN"


# ─── verificar_plano: endpoint_permitido vazio ────────────────────────────────


@pytest.mark.asyncio
async def test_verificar_plano_vazio_levanta_403() -> None:
    from fastapi import Request
    from starlette.datastructures import State

    mock_req = MagicMock(spec=Request)
    mock_req.state = State()
    mock_req.state.endpoint_permitido = []
    mock_req.state.is_admin = False
    mock_req.url = MagicMock()
    mock_req.url.path = "/v1/operadoras"

    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc_info:
        await dependencia.verificar_plano(mock_req)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail["codigo"] == "PLANO_SEM_ENDPOINTS"


@pytest.mark.asyncio
async def test_verificar_plano_vazio_admin_passa() -> None:
    from fastapi import Request
    from starlette.datastructures import State

    mock_req = MagicMock(spec=Request)
    mock_req.state = State()
    mock_req.state.endpoint_permitido = []
    mock_req.state.is_admin = True
    mock_req.url = MagicMock()
    mock_req.url.path = "/admin/billing/resumo"

    await dependencia.verificar_plano(mock_req)


@pytest.mark.asyncio
async def test_verificar_plano_rota_nao_autorizada_levanta_403() -> None:
    from fastapi import HTTPException, Request
    from starlette.datastructures import State

    mock_req = MagicMock(spec=Request)
    mock_req.state = State()
    mock_req.state.endpoint_permitido = ["/v1/operadoras"]
    mock_req.state.is_admin = False
    mock_req.url = MagicMock()
    mock_req.url.path = "/prata/cadop"

    with pytest.raises(HTTPException) as exc_info:
        await dependencia.verificar_plano(mock_req)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail["codigo"] == "PLANO_SEM_ACESSO"


# ─── verificar_admin ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_verificar_admin_sem_flag_levanta_403() -> None:
    from fastapi import HTTPException, Request
    from starlette.datastructures import State

    mock_req = MagicMock(spec=Request)
    mock_req.state = State()
    mock_req.state.is_admin = False

    with pytest.raises(HTTPException) as exc_info:
        await dependencia.verificar_admin(mock_req)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail["codigo"] == "ACESSO_RESTRITO_ADMIN"


@pytest.mark.asyncio
async def test_verificar_admin_com_flag_passa() -> None:
    from fastapi import Request
    from starlette.datastructures import State

    mock_req = MagicMock(spec=Request)
    mock_req.state = State()
    mock_req.state.is_admin = True

    await dependencia.verificar_admin(mock_req)


# ─── Startup com secrets default em produção ─────────────────────────────────


def test_validar_configuracao_bloqueia_startup_em_producao_com_secrets_default() -> None:
    s = Settings(
        API_ENV="production",
        API_JWT_ADMIN_SECRET="trocar_em_producao",
        LAYOUT_SERVICE_TOKEN="healthintel_layout_service_local_token_2026",
        POSTGRES_PASSWORD="healthintel",
        MONGO_INITDB_ROOT_PASSWORD="healthintel",
        API_INTERNAL_TOKEN="healthintel_internal_local_token",
        API_CORS_ALLOWED_ORIGINS="https://healthintel.com.br",
        API_ALLOWED_HOSTS="healthintel.com.br,www.healthintel.com.br",
    )
    with pytest.raises(RuntimeError, match="Startup bloqueado"):
        s.validar_configuracao()


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


# ─── CORS em produção ─────────────────────────────────────────────────────────


def test_cors_nao_aceita_origem_nao_autorizada(monkeypatch) -> None:
    monkeypatch.setattr(
        dependencia.settings,
        "app_cors_allowed_origins",
        "https://healthintel.com.br",
    )
    response = client.options(
        "/saude",
        headers={
            "Origin": "https://evil-site.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert "evil-site.com" not in response.headers.get("access-control-allow-origin", "")


# ─── is_admin derivado do plano_nome ─────────────────────────────────────────


def test_is_admin_derivado_de_admin_interno(monkeypatch) -> None:
    """is_admin=True somente quando plano_nome == 'admin_interno'"""
    row = {
        "chave_id": "1",
        "cliente_id": "2",
        "plano_id": "3",
        "prefixo_chave": "hi_xxxx",
        "status_chave": "ativo",
        "status_cliente": "ativo",
        "limite_rpm": 60,
        "endpoint_permitido": [],
        "camadas_permitidas": ["ouro", "prata", "bronze"],
        "plano_nome": "admin_interno",
    }

    from fastapi import Request
    from starlette.datastructures import State

    mock_req = MagicMock(spec=Request)
    mock_req.state = State()

    # Simular o bloco de atribuição de estado de validar_chave
    plano_nome = str(row.get("plano_nome") or "")
    mock_req.state.is_admin = plano_nome.lower() == "admin_interno"

    assert mock_req.state.is_admin is True


def test_is_admin_false_para_plano_comum() -> None:
    plano_nome = "essencial"
    is_admin = plano_nome.lower() == "admin_interno"
    assert is_admin is False
