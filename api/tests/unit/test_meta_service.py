from contextlib import asynccontextmanager
from datetime import datetime

import pytest

from api.app.services import meta as service


class FakeResult:
    def __init__(self, rows: list[dict]) -> None:
        self.rows = rows

    def mappings(self) -> list[dict]:
        return self.rows


class FakeSession:
    def __init__(self, rows: list[dict]) -> None:
        self.rows = rows

    async def execute(self, *_args, **_kwargs):
        return FakeResult(self.rows)


@pytest.mark.asyncio
async def test_listar_pipeline_deve_expor_dataset(monkeypatch) -> None:
    @asynccontextmanager
    async def fake_session_local():
        yield FakeSession(
            [
                {
                    "dag_id": "dag_mestre_mensal",
                    "dataset": "cadop",
                    "status": "sucesso",
                    "iniciado_em": datetime(2026, 4, 22),
                    "finalizado_em": None,
                }
            ]
        )

    monkeypatch.setattr(service, "SessionLocal", fake_session_local)

    payload = await service.listar_pipeline()

    assert payload["dados"][0]["dataset"] == "cadop"


@pytest.mark.asyncio
async def test_listar_endpoints_deve_expor_novo_endpoint(monkeypatch) -> None:
    payload = await service.listar_endpoints()

    assert any(
        endpoint["rota"] == "/v1/rankings/municipio/oportunidade-v2"
        for endpoint in payload["dados"]
    )
