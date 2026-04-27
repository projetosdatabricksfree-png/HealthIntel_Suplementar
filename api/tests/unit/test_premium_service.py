import asyncio

from api.app.services import premium as service


def test_premium_datasets_leem_apenas_api_ans_api_premium() -> None:
    for cfg in service.PREMIUM_DATASETS.values():
        assert cfg["tabela"].startswith("api_ans.api_premium_")


def test_buscar_premium_quality_dataset_envelopa_resultado(monkeypatch) -> None:
    async def fake_cache(_chave: str):
        return None

    async def fake_save(*_args, **_kwargs):
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

    class FakeSession:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def execute(self, statement, params=None):
            sql = str(statement)
            assert "api_ans.api_premium_quality_dataset" in sql
            if "count(*)" in sql:
                return FakeResult(scalar=1)
            return FakeResult(
                rows=[
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
                ]
            )

    monkeypatch.setattr(service, "_obter_cache", fake_cache)
    monkeypatch.setattr(service, "_salvar_cache", fake_save)
    monkeypatch.setattr(service, "SessionLocal", lambda: FakeSession())

    payload = asyncio.run(
        service.buscar_premium(
            "quality_dataset",
            filtros={"fonte_documento": "operadora"},
        )
    )

    assert payload["dados"][0]["fonte_documento"] == "operadora"
    assert payload["meta"]["fonte"] == "api_premium_quality_dataset"
    assert payload["meta"]["total"] == 1
