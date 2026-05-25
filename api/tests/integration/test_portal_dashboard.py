"""Integration: /v1/portal/dashboard/uso — autenticado por JWT, derivado de me_service.get_uso()."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

from fastapi import Request
from fastapi.testclient import TestClient

from api.app.dependencia_sessao import obter_usuario_sessao
from api.app.main import app


def _override_sessao(cliente_id: str = "00000000-0000-0000-0000-000000000010"):
    async def fake(request: Request) -> str:
        request.state.usuario_id = "00000000-0000-0000-0000-000000000099"
        request.state.tenant_ativo_id = cliente_id
        request.state.role = "owner"
        return request.state.usuario_id

    return fake


def test_dashboard_uso_exige_jwt():
    client = TestClient(app)
    r = client.get("/v1/portal/dashboard/uso?periodo=hoje")
    assert r.status_code == 401, r.text
    assert r.json()["codigo"] == "TOKEN_AUSENTE"


def test_dashboard_uso_retorna_mesma_estrutura_que_me_uso():
    client = TestClient(app)
    cliente_id = "00000000-0000-0000-0000-000000000010"
    app.dependency_overrides[obter_usuario_sessao] = _override_sessao(cliente_id)
    try:
        from api.app.routers import portal_dashboard as router_mod

        resposta_esperada = {
            "dados": {
                "periodo": "hoje",
                "total_requisicoes": 12,
                "total_erros": 1,
                "latencia_media_ms": 88,
                "success_rate": 91.7,
                "serie_diaria": [
                    {"dia": "2026-05-25", "requisicoes": 12, "erros": 1, "latencia_ms": 88}
                ],
                "por_endpoint": [
                    {"endpoint": "/v1/operadoras", "requisicoes": 12, "erros": 1}
                ],
            },
            "meta": {
                "periodo": "hoje",
                "inicio": "2026-05-25",
                "fim": "2026-05-25",
                "plano": "free",
                "quota_daily": 100,
                "quota_used_today": 12,
            },
        }

        async def fake_plano(cid: str) -> tuple[str, int]:
            assert cid == cliente_id
            return "free", 100

        with (
            patch.object(router_mod, "get_uso", AsyncMock(return_value=resposta_esperada)),
            patch.object(router_mod, "_plano_do_cliente", AsyncMock(side_effect=fake_plano)),
        ):
            r = client.get(
                "/v1/portal/dashboard/uso?periodo=hoje",
                headers={"Authorization": "Bearer fake"},
            )
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["meta"]["quota_used_today"] == 12
        assert body["meta"]["plano"] == "free"
        assert body["dados"]["total_requisicoes"] == 12
    finally:
        app.dependency_overrides.pop(obter_usuario_sessao, None)


def test_dashboard_uso_repassa_cliente_id_do_tenant():
    """Garante que o cliente_id usado em get_uso() vem de request.state.tenant_ativo_id, não de X-API-Key."""
    client = TestClient(app)
    cliente_id = "00000000-0000-0000-0000-000000000042"
    app.dependency_overrides[obter_usuario_sessao] = _override_sessao(cliente_id)
    try:
        from api.app.routers import portal_dashboard as router_mod

        captured: dict = {}

        async def fake_get_uso(**kwargs):
            captured.update(kwargs)
            return {"dados": {}, "meta": {}}

        async def fake_plano(cid: str) -> tuple[str, int]:
            return "pro", 1000

        with (
            patch.object(router_mod, "get_uso", AsyncMock(side_effect=fake_get_uso)),
            patch.object(router_mod, "_plano_do_cliente", AsyncMock(side_effect=fake_plano)),
        ):
            r = client.get(
                "/v1/portal/dashboard/uso?days=30",
                headers={"Authorization": "Bearer fake"},
            )
        assert r.status_code == 200, r.text
        assert captured["cliente_id"] == cliente_id
        assert captured["periodo"] == "30d"
        assert captured["plano_nome"] == "pro"
        assert captured["limite_req_dia"] == 1000
    finally:
        app.dependency_overrides.pop(obter_usuario_sessao, None)


def test_dashboard_uso_falha_sem_tenant_ativo():
    """Sessão JWT sem tenant_ativo_id → 403 SEM_TENANT."""
    client = TestClient(app)

    async def sessao_sem_tenant(request: Request) -> str:
        request.state.usuario_id = "00000000-0000-0000-0000-000000000099"
        request.state.tenant_ativo_id = None
        request.state.role = "owner"
        return request.state.usuario_id

    app.dependency_overrides[obter_usuario_sessao] = sessao_sem_tenant
    try:
        r = client.get(
            "/v1/portal/dashboard/uso?periodo=hoje",
            headers={"Authorization": "Bearer fake"},
        )
        assert r.status_code == 403, r.text
        assert r.json()["codigo"] == "SEM_TENANT"
    finally:
        app.dependency_overrides.pop(obter_usuario_sessao, None)
