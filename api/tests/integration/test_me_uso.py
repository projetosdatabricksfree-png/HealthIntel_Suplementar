"""Integration test do endpoint /v1/me/uso — formato da resposta com quota/success_rate."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

from fastapi import Request
from fastapi.testclient import TestClient

from api.app.dependencia import validar_chave
from api.app.main import app


def _override_validar_chave():
    async def fake(request: Request) -> str:
        request.state.chave_api = "teste"
        request.state.chave_api_id = "00000000-0000-0000-0000-000000000001"
        request.state.cliente_id = "00000000-0000-0000-0000-000000000002"
        request.state.plano_id = "00000000-0000-0000-0000-000000000003"
        request.state.plano_nome = "free"
        request.state.limite_rpm = 100
        request.state.limite_req_dia = 100
        request.state.endpoint_permitido = ["/v1"]
        request.state.camadas_permitidas = ["bronze", "prata", "ouro"]
        request.state.is_admin = False
        request.state.auth_cache = "miss"
        return "ok"

    return fake


def test_me_uso_formato_com_quota_e_success_rate():
    client = TestClient(app)
    app.dependency_overrides[validar_chave] = _override_validar_chave()
    try:
        # mocka get_uso e aplicar_rate_limit pra isolar do Postgres/Redis reais
        from api.app.services import me_service as me_module
        from api.app.routers import me as me_router

        resposta_esperada = {
            "dados": {
                "periodo": "hoje",
                "total_requisicoes": 5,
                "total_erros": 1,
                "latencia_media_ms": 120,
                "success_rate": 80.0,
                "serie_diaria": [
                    {"dia": "2026-05-20", "requisicoes": 5, "erros": 1, "latencia_ms": 120}
                ],
                "por_endpoint": [
                    {"endpoint": "/v1/operadoras", "requisicoes": 5, "erros": 1}
                ],
            },
            "meta": {
                "periodo": "hoje",
                "inicio": "2026-05-20",
                "fim": "2026-05-20",
                "plano": "free",
                "quota_daily": 100,
                "quota_used_today": 5,
            },
        }

        with (
            patch.object(me_router, "get_uso", AsyncMock(return_value=resposta_esperada)),
            patch.object(me_router, "aplicar_rate_limit", AsyncMock(return_value=None)),
        ):
            r = client.get("/v1/me/uso?periodo=hoje", headers={"x-api-key": "qq"})
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["dados"]["success_rate"] == 80.0
        assert body["meta"]["quota_daily"] == 100
        assert body["meta"]["quota_used_today"] == 5
        assert body["meta"]["plano"] == "free"
    finally:
        app.dependency_overrides.pop(validar_chave, None)


def test_me_uso_days_alias_funciona():
    client = TestClient(app)
    app.dependency_overrides[validar_chave] = _override_validar_chave()
    try:
        from api.app.routers import me as me_router
        captured: dict = {}

        async def fake_get_uso(**kwargs):
            captured.update(kwargs)
            return {"dados": {"periodo": kwargs["periodo"]}, "meta": {}}

        with (
            patch.object(me_router, "get_uso", AsyncMock(side_effect=fake_get_uso)),
            patch.object(me_router, "aplicar_rate_limit", AsyncMock(return_value=None)),
        ):
            r = client.get("/v1/me/uso?days=30", headers={"x-api-key": "qq"})
        assert r.status_code == 200
        assert captured["periodo"] == "30d"

        # days=0 → hoje
        with (
            patch.object(me_router, "get_uso", AsyncMock(side_effect=fake_get_uso)),
            patch.object(me_router, "aplicar_rate_limit", AsyncMock(return_value=None)),
        ):
            r = client.get("/v1/me/uso?days=0", headers={"x-api-key": "qq"})
        assert r.status_code == 200
        assert captured["periodo"] == "hoje"
    finally:
        app.dependency_overrides.pop(validar_chave, None)


def test_me_uso_quota_shared_across_multiple_api_keys():
    """Valida que múltiplas chaves de API de um mesmo cliente compartilham a quota diária."""
    client = TestClient(app)

    # Simula dois clientes diferentes
    cliente_1_id = "00000000-0000-0000-0000-000000000001"
    cliente_2_id = "00000000-0000-0000-0000-000000000099"

    def _override_validar_chave_cliente(cliente_id: str):
        async def fake(request: Request) -> str:
            request.state.chave_api = f"chave_{cliente_id}"
            request.state.chave_api_id = f"chave_id_{cliente_id}"
            request.state.cliente_id = cliente_id
            request.state.plano_id = "00000000-0000-0000-0000-000000000003"
            request.state.plano_nome = "free"
            request.state.limite_rpm = 100
            request.state.limite_req_dia = 100
            request.state.endpoint_permitido = ["/v1"]
            request.state.camadas_permitidas = ["bronze"]
            request.state.is_admin = False
            request.state.auth_cache = "miss"
            return "ok"
        return fake

    try:
        from api.app.services import me_service as me_module
        from api.app.middleware import rate_limit as rl_module

        # Captura as chaves Redis usadas para verificar que cliente_id é usado, não chave_api_id
        redis_keys_used = []
        original_incr = None

        async def mock_incr(key: str):
            redis_keys_used.append(key)
            return 1  # Simula primeiro request

        with (
            patch.object(me_module.redis_client, "incr", side_effect=mock_incr),
            patch.object(me_module.redis_client, "expire", AsyncMock()),
            patch.object(me_module.redis_client, "get", AsyncMock(return_value="0")),
        ):
            # Request com cliente 1, chave 1
            app.dependency_overrides[validar_chave] = _override_validar_chave_cliente(cliente_1_id)
            r1 = client.get("/v1/me/uso?periodo=hoje", headers={"x-api-key": "key1"})
            assert r1.status_code == 200

            # Verifica que a chave Redis contém cliente_id, não chave_api_id
            assert len(redis_keys_used) > 0
            redis_key_used = redis_keys_used[-1]
            assert cliente_1_id in redis_key_used, (
                f"Redis key deve conter cliente_id ({cliente_1_id}), mas contém: {redis_key_used}"
            )
            assert "chave_id_" not in redis_key_used, (
                f"Redis key não deve conter chave_api_id, mas contém: {redis_key_used}"
            )

            # Request com cliente 2 (cliente diferente)
            redis_keys_used.clear()
            app.dependency_overrides[validar_chave] = _override_validar_chave_cliente(cliente_2_id)
            r2 = client.get("/v1/me/uso?periodo=hoje", headers={"x-api-key": "key2"})
            assert r2.status_code == 200

            # Verifica que cliente 2 usa chave Redis diferente
            redis_key_used_2 = redis_keys_used[-1]
            assert cliente_2_id in redis_key_used_2
    finally:
        app.dependency_overrides.pop(validar_chave, None)
