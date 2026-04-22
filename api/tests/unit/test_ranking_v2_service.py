import pytest

from api.app.services import ranking as service


@pytest.mark.asyncio
async def test_ranking_oportunidade_v2_usa_cache(monkeypatch) -> None:
    payload = {
        "dados": [{"cd_municipio": "3550308", "oportunidade_v2_score": 91.2}],
        "meta": {"cache": "miss"},
    }

    async def fake_get(_chave: str) -> dict:
        return payload

    monkeypatch.setattr(service, "_obter_cache", fake_get)

    response = await service.listar_ranking_oportunidade_v2()

    assert response["dados"][0]["cd_municipio"] == "3550308"
    assert response["meta"]["cache"] == "hit"
