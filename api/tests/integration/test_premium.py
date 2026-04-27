from fastapi import Request
from fastapi.testclient import TestClient

from api.app.main import app
from api.app.middleware.autenticacao import validar_api_key

client = TestClient(app)


def _fake_auth(camadas: list[str]):
    async def fake_auth(request: Request, x_api_key: str | None = None):
        request.state.chave_api_id = "premium-test"
        request.state.cliente_id = "cliente-premium"
        request.state.plano_id = "plano-premium"
        request.state.limite_rpm = 1000
        request.state.endpoint_permitido = ["/v1"]
        request.state.camadas_permitidas = camadas
        return "ok"

    return fake_auth


def _payload_operadora() -> dict:
    return {
        "dados": [
            {
                "competencia": "202501",
                "registro_ans": "123456",
                "razao_social": "OPERADORA TESTE",
                "nome_fantasia": "OPERADORA TESTE",
                "modalidade": "MEDICINA_DE_GRUPO",
                "uf": "SP",
                "qt_beneficiarios": 1000,
                "variacao_12m_pct": 0.1,
                "score_total": 88.0,
                "componente_core": 90.0,
                "componente_regulatorio": 80.0,
                "componente_financeiro": 85.0,
                "componente_rede": 87.0,
                "componente_estrutural": 92.0,
                "versao_metodologia": "score_v3",
                "cnpj_normalizado": "11222333000181",
                "registro_ans_formato_valido": True,
                "cnpj_digito_valido": True,
                "documento_quality_status": "VALIDO",
                "motivo_invalidade_documento": None,
                "quality_score_documental": 100.0,
            }
        ],
        "meta": {
            "fonte": "api_premium_operadora_360_validado",
            "competencia": "202501",
            "versao_dataset": "operadora_360_validado_v1",
            "total": 1,
            "pagina": 1,
            "por_pagina": 50,
            "cache": "miss",
        },
    }


def _payload_cnes() -> dict:
    return {
        "dados": [
            {
                "competencia": "202501",
                "cnes": "1234567",
                "cnes_normalizado": "1234567",
                "cnpj_normalizado": "11222333000181",
                "razao_social": "ESTABELECIMENTO TESTE",
                "nome_fantasia": "ESTABELECIMENTO TESTE",
                "sg_uf": "SP",
                "cd_municipio": "3550308",
                "nm_municipio": "SAO PAULO",
                "tipo_unidade": "HOSPITAL",
                "tipo_unidade_desc": "Hospital",
                "cnes_formato_valido": True,
                "cnpj_digito_valido": True,
                "documento_quality_status": "VALIDO",
                "motivo_invalidade_documento": None,
                "quality_score_cnes": 100.0,
            }
        ],
        "meta": {
            "fonte": "api_premium_cnes_estabelecimento_validado",
            "competencia": "202501",
            "versao_dataset": "cnes_estabelecimento_validado_v1",
            "total": 1,
            "pagina": 1,
            "por_pagina": 50,
            "cache": "miss",
        },
    }


def _payload_quality() -> dict:
    return {
        "dados": [
            {
                "fonte_documento": "operadora",
                "documento_quality_status": "VALIDO",
                "total_registro": 10,
                "total_fonte": 10,
                "total_valido": 10,
                "total_invalido": 0,
                "taxa_valido": 1.0,
                "quality_score_documental": 100.0,
            }
        ],
        "meta": {
            "fonte": "api_premium_quality_dataset",
            "competencia": "todas",
            "versao_dataset": "quality_dataset_v1",
            "total": 1,
            "pagina": 1,
            "por_pagina": 50,
            "cache": "miss",
        },
    }


async def _fake_log_uso(*args, **kwargs):
    return None


def test_premium_endpoints_retornam_envelope(monkeypatch) -> None:
    async def fake_service(dataset: str, **kwargs):
        if dataset == "operadora_360_validado":
            return _payload_operadora()
        if dataset == "cnes_estabelecimento_validado":
            return _payload_cnes()
        return _payload_quality()

    app.dependency_overrides[validar_api_key] = _fake_auth(["ouro", "prata", "premium"])
    monkeypatch.setattr("api.app.routers.premium.buscar_premium", fake_service)
    monkeypatch.setattr("api.app.middleware.log_requisicao.registrar_log_uso", _fake_log_uso)
    try:
        responses = [
            client.get(
                "/v1/premium/operadoras?competencia=202501",
                headers={"X-API-Key": "ok"},
            ),
            client.get(
                "/v1/premium/cnes/estabelecimentos?competencia=202501",
                headers={"X-API-Key": "ok"},
            ),
            client.get("/v1/premium/quality/datasets", headers={"X-API-Key": "ok"}),
        ]
    finally:
        app.dependency_overrides.clear()

    assert [response.status_code for response in responses] == [200, 200, 200]
    assert responses[0].json()["meta"]["fonte"] == "api_premium_operadora_360_validado"
    assert responses[1].json()["dados"][0]["documento_quality_status"] == "VALIDO"
    assert responses[2].json()["dados"][0]["quality_score_documental"] == 100.0


def test_premium_bloqueia_plano_sem_camada(monkeypatch) -> None:
    app.dependency_overrides[validar_api_key] = _fake_auth(["ouro", "prata"])
    monkeypatch.setattr("api.app.middleware.log_requisicao.registrar_log_uso", _fake_log_uso)
    try:
        response = client.get(
            "/v1/premium/operadoras?competencia=202501",
            headers={"X-API-Key": "ok"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 403
