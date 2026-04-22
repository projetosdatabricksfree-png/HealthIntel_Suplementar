import pytest

from api.app.services import operadora as service


@pytest.mark.asyncio
async def test_detalhar_operadora_usa_cache(monkeypatch) -> None:
    payload = {"dados": [{"registro_ans": "123456"}], "meta": {"cache": "miss"}}

    async def fake_get(_chave: str) -> dict:
        return payload

    monkeypatch.setattr(service, "_obter_cache", fake_get)

    response = await service.detalhar_operadora("123456")

    assert response["dados"][0]["registro_ans"] == "123456"
    assert response["meta"]["cache"] == "hit"
