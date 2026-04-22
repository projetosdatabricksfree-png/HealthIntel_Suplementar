import pytest

from api.app.services import regulatorio as service


@pytest.mark.asyncio
async def test_detalhar_regulatorio_usa_cache(monkeypatch) -> None:
    payload = {"dados": [{"registro_ans": "123456"}], "meta": {"cache": "miss"}}

    async def fake_get(_chave: str) -> dict:
        return payload

    monkeypatch.setattr(service, "_obter_cache", fake_get)

    response = await service.detalhar_regulatorio_operadora("123456")

    assert response["dados"][0]["registro_ans"] == "123456"
    assert response["meta"]["cache"] == "hit"


@pytest.mark.asyncio
async def test_listar_rn623_usa_cache(monkeypatch) -> None:
    payload = {"dados": [{"registro_ans": "123456", "tipo_lista": "excelencia"}], "meta": {}}

    async def fake_get(_chave: str) -> dict:
        return payload

    monkeypatch.setattr(service, "_obter_cache", fake_get)

    response = await service.listar_rn623()

    assert response["dados"][0]["tipo_lista"] == "excelencia"
    assert response["meta"]["cache"] == "hit"
