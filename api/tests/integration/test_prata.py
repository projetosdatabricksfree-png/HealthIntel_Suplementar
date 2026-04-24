import asyncio

from fastapi import Request
from fastapi.testclient import TestClient

from api.app.main import app
from api.app.middleware.autenticacao import validar_api_key

client = TestClient(app)


def _payload(dataset: str = "cadop") -> dict:
    return {
        "dados": [{"dataset": dataset, "competencia": "202501", "versao_dataset": "v1"}],
        "meta": {
            "fonte": dataset,
            "competencia": "202501",
            "versao_dataset": "v1",
            "qualidade": {
                "taxa_aprovacao": 1.0,
                "registros_quarentena": 0,
                "motivos_rejeicao": [],
            },
            "aviso_qualidade": None,
            "total": 1,
            "pagina": 1,
            "por_pagina": 1,
            "cache": "miss",
        },
    }


def _fake_auth(camadas: list[str]):
    async def fake_auth(request: Request, x_api_key: str | None = None):
        request.state.chave_api_id = "prata-test"
        request.state.cliente_id = "cliente-test"
        request.state.plano_id = "plano-test"
        request.state.limite_rpm = 1000
        request.state.endpoint_permitido = ["/v1"]
        request.state.camadas_permitidas = camadas
        return "ok"

    return fake_auth


async def _fake_log_uso(*args, **kwargs):
    return None


def _instalar_auth(monkeypatch, camadas: list[str] | None = None) -> None:
    app.dependency_overrides[validar_api_key] = _fake_auth(camadas or ["bronze", "prata", "ouro"])
    monkeypatch.setattr("api.app.middleware.log_requisicao.registrar_log_uso", _fake_log_uso)


def test_prata_quarentena_resumo_retorna_payload(monkeypatch) -> None:
    async def fake_service(*args, **kwargs):
        payload = _payload("quarentena")
        payload["dados"] = [
            {
                "dataset": "cadop",
                "arquivo_origem": "cadop_demo.csv",
                "competencia": "202501",
                "hash_arquivo": "hash",
                "total_registros": 2,
                "primeiro_registro_em": "2026-04-22T00:00:00Z",
                "ultimo_registro_em": "2026-04-22T00:00:00Z",
                "status_quarentena": ["pendente"],
            }
        ]
        return payload

    _instalar_auth(monkeypatch)
    monkeypatch.setattr("api.app.routers.prata.buscar_quarentena_resumo", fake_service)
    try:
        response = client.get(
            "/v1/prata/quarentena/resumo",
            headers={"X-API-Key": "ok"},
            params={"competencia": "202501"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["dados"][0]["dataset"] == "cadop"


def test_prata_cnes_e_tiss_retorna_payload(monkeypatch) -> None:
    chamadas: list[str] = []

    async def fake_service(dataset: str, **kwargs):
        chamadas.append(dataset)
        return _payload(dataset)

    _instalar_auth(monkeypatch)
    monkeypatch.setattr("api.app.routers.prata.buscar_prata", fake_service)
    try:
        urls = [
            "/v1/prata/cnes/municipio?competencia=202501&cd_municipio=3550308",
            "/v1/prata/cnes/rede-gap?competencia=202501&cd_municipio=3550308",
            "/v1/prata/tiss/procedimento?competencia=2025T1&registro_ans=123456",
        ]
        responses = [client.get(url, headers={"X-API-Key": "ok"}) for url in urls]
    finally:
        app.dependency_overrides.clear()

    assert [response.status_code for response in responses] == [200, 200, 200]
    assert chamadas == ["cnes_municipio", "cnes_rede_gap", "tiss_procedimento"]


def test_prata_quarentena_dataset_exige_plano_prata(monkeypatch) -> None:
    _instalar_auth(monkeypatch, camadas=["bronze"])
    try:
        response = client.get("/v1/prata/quarentena/cadop", headers={"X-API-Key": "ok"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 403


def test_prata_aviso_qualidade_presente_quando_taxa_baixa(monkeypatch) -> None:
    async def fake_cache(*args, **kwargs):
        return None

    async def fake_save(*args, **kwargs):
        return None

    class FakeResult:
        def __init__(self, rows=None, scalar=None):
            self._rows = rows or []
            self._scalar = scalar

        def scalar_one(self):
            return self._scalar

        def mappings(self):
            return self

        def all(self):
            return self._rows

        def first(self):
            return {"registros_quarentena": 1, "motivos_rejeicao": ["layout"]}

    class FakeSession:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def execute(self, statement, params=None):
            sql = str(statement)
            if "select count(*) from api_ans.api_prata_cadop" in sql:
                return FakeResult(scalar=1)
            if "from api_ans.api_prata_cadop" in sql:
                return FakeResult(rows=[{"competencia": "202501", "versao_dataset": "v1"}])
            return FakeResult()

    monkeypatch.setattr("api.app.services.prata._obter_cache", fake_cache)
    monkeypatch.setattr("api.app.services.prata._salvar_cache", fake_save)
    monkeypatch.setattr("api.app.services.prata.SessionLocal", lambda: FakeSession())

    from api.app.services.prata import buscar_prata

    payload = asyncio.run(buscar_prata("cadop", competencia="202501"))

    assert payload["meta"]["qualidade"]["taxa_aprovacao"] == 0.5
    assert payload["meta"]["aviso_qualidade"] is not None
