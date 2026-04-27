from fastapi import Request
from fastapi.testclient import TestClient

from api.app.main import app
from api.app.middleware.autenticacao import validar_api_key

client = TestClient(app)


def _fake_auth(camadas: list[str], cliente_id: str | None = "cliente-teste"):
    async def fake_auth(request: Request, x_api_key: str | None = None):
        request.state.chave_api_id = "regressao-fase5"
        request.state.cliente_id = cliente_id
        request.state.plano_id = "plano-teste"
        request.state.limite_rpm = 1000
        request.state.endpoint_permitido = ["/v1"]
        request.state.camadas_permitidas = camadas
        return "ok"
    return fake_auth


async def _fake_log_uso(*args, **kwargs):
    return None


PREMIUM_PUBLICOS = [
    "/v1/premium/operadoras?competencia=202501",
    "/v1/premium/cnes/estabelecimentos?competencia=202501",
    "/v1/premium/tiss/procedimentos?trimestre=2025T1",
    "/v1/premium/tuss/procedimentos",
    "/v1/premium/mdm/operadoras",
    "/v1/premium/mdm/prestadores",
    "/v1/premium/quality/datasets",
]

PREMIUM_PRIVADOS = [
    "/v1/premium/contratos",
    "/v1/premium/subfaturas",
]

LEGADOS = [
    "/v1/operadora/360",
    "/v1/saude",
    "/v1/prata/cadop?competencia=202501",
    "/v1/bronze/sib/operadora?competencia=202501&registro_ans=123456",
]


async def _mock_premium(dataset, **kw) -> dict:
    return {
        "dados": [],
        "meta": {
            "fonte": "mock",
            "competencia": "202501",
            "versao_dataset": "mock_v1",
            "total": 0,
            "pagina": 1,
            "por_pagina": 50,
            "cache": "miss",
        },
    }


def test_premium_publicos_respondem_200(monkeypatch) -> None:
    """Endpoints premium públicos respondem 200 com plano premium."""
    app.dependency_overrides[validar_api_key] = _fake_auth(["ouro", "prata", "bronze", "premium"])
    monkeypatch.setattr(
        "api.app.routers.premium.buscar_premium", _mock_premium
    )
    monkeypatch.setattr("api.app.middleware.log_requisicao.registrar_log_uso", _fake_log_uso)
    try:
        for endpoint in PREMIUM_PUBLICOS:
            response = client.get(endpoint, headers={"X-API-Key": "ok"})
            assert response.status_code == 200, f"{endpoint} retornou {response.status_code}"
            json_data = response.json()
            assert "dados" in json_data
            assert "meta" in json_data
    finally:
        app.dependency_overrides.clear()


def test_premium_privados_com_tenant_respondem_200(monkeypatch) -> None:
    """Endpoints premium privados respondem 200 com tenant autenticado."""
    app.dependency_overrides[validar_api_key] = _fake_auth(
        ["ouro", "prata", "bronze", "premium"], "cliente-teste"
    )
    monkeypatch.setattr(
        "api.app.routers.premium.buscar_premium", _mock_premium
    )
    monkeypatch.setattr("api.app.middleware.log_requisicao.registrar_log_uso", _fake_log_uso)
    try:
        for endpoint in PREMIUM_PRIVADOS:
            response = client.get(endpoint, headers={"X-API-Key": "ok"})
            assert response.status_code == 200, f"{endpoint} retornou {response.status_code}"
    finally:
        app.dependency_overrides.clear()


def test_premium_privados_sem_tenant_retornam_403(monkeypatch) -> None:
    """Endpoints premium privados sem tenant retornam 403."""
    app.dependency_overrides[validar_api_key] = _fake_auth(
        ["ouro", "prata", "bronze", "premium"], None
    )
    monkeypatch.setattr("api.app.middleware.log_requisicao.registrar_log_uso", _fake_log_uso)
    try:
        for endpoint in PREMIUM_PRIVADOS:
            response = client.get(endpoint, headers={"X-API-Key": "ok"})
            assert response.status_code == 403, f"{endpoint} retornou {response.status_code}"
    finally:
        app.dependency_overrides.clear()


def test_nao_premium_retorna_403(monkeypatch) -> None:
    """Plano sem camada premium recebe 403 em /v1/premium/*."""
    app.dependency_overrides[validar_api_key] = _fake_auth(["ouro"])
    monkeypatch.setattr("api.app.middleware.log_requisicao.registrar_log_uso", _fake_log_uso)
    try:
        response = client.get(PREMIUM_PUBLICOS[0], headers={"X-API-Key": "ok"})
        assert response.status_code == 403
    finally:
        app.dependency_overrides.clear()


def test_endpoints_legados_preservados(monkeypatch) -> None:
    """Endpoints legados continuam respondendo (não quebrados pelo premium)."""
    app.dependency_overrides[validar_api_key] = _fake_auth(["ouro"])
    monkeypatch.setattr("api.app.middleware.log_requisicao.registrar_log_uso", _fake_log_uso)
    try:
        for endpoint in LEGADOS:
            response = client.get(endpoint, headers={"X-API-Key": "ok"})
            # Aceitamos 200, 404, ou 403 — mas NUNCA 500
            assert response.status_code != 500, (
                f"Endpoint legado {endpoint} retornou 500"
            )
    finally:
        app.dependency_overrides.clear()


def test_premium_envelope_possui_paginacao(monkeypatch) -> None:
    """Resposta premium possui paginação."""
    payload = {
        "dados": [{"competencia": "202501", "registro_ans": "123456",
                    "razao_social": None, "nome_fantasia": None, "modalidade": None,
                    "uf": None, "qt_beneficiarios": None, "variacao_12m_pct": None,
                    "score_total": None, "componente_core": None,
                    "componente_regulatorio": None, "componente_financeiro": None,
                    "componente_rede": None, "componente_estrutural": None,
                    "versao_metodologia": None, "cnpj_normalizado": "11222333000181",
                    "registro_ans_formato_valido": True, "cnpj_digito_valido": True,
                    "documento_quality_status": "VALIDO",
                    "motivo_invalidade_documento": None, "quality_score_documental": 100.0}],
        "meta": {"fonte": "mock", "competencia": "202501", "versao_dataset": "v1",
                 "total": 1, "pagina": 1, "por_pagina": 50, "cache": "miss"},
    }
    app.dependency_overrides[validar_api_key] = _fake_auth(["ouro", "prata", "bronze", "premium"])
    async def _mock_premium_paginacao(dataset, **kw):
        return payload
    monkeypatch.setattr(
        "api.app.routers.premium.buscar_premium", _mock_premium_paginacao
    )
    monkeypatch.setattr("api.app.middleware.log_requisicao.registrar_log_uso", _fake_log_uso)
    try:
        response = client.get(PREMIUM_PUBLICOS[0], headers={"X-API-Key": "ok"})
        meta = response.json()["meta"]
        assert meta["pagina"] >= 1
        assert meta["por_pagina"] >= 1
    finally:
        app.dependency_overrides.clear()