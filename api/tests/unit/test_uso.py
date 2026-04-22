from contextlib import asynccontextmanager
from datetime import UTC, datetime

import pytest

from api.app.services import uso
from api.app.services.uso import registrar_log_uso


class FakeSession:
    def __init__(self) -> None:
        self.executed: list[tuple[str, dict]] = []
        self.committed = False

    async def execute(self, statement, params):
        self.executed.append((str(statement), params))

    async def commit(self) -> None:
        self.committed = True


@pytest.mark.asyncio
async def test_registrar_log_uso_persiste_hash_ip(monkeypatch) -> None:
    fake_session = FakeSession()

    @asynccontextmanager
    async def fake_session_local():
        yield fake_session

    monkeypatch.setattr(uso, "SessionLocal", fake_session_local)
    monkeypatch.setattr(
        uso,
        "datetime",
        type(
            "FakeDateTime",
            (),
            {"now": staticmethod(lambda tz=None: datetime(2026, 4, 22, tzinfo=UTC))},
        ),
    )

    await registrar_log_uso(
        chave_id="33333333-3333-3333-3333-333333333333",
        cliente_id="22222222-2222-2222-2222-222222222222",
        plano_id="11111111-1111-1111-1111-111111111111",
        endpoint="/v1/operadoras",
        rota="/v1/operadoras",
        metodo="GET",
        codigo_status=200,
        latencia_ms=42,
        cache_hit=True,
        ip_cliente="127.0.0.1",
    )

    assert fake_session.committed is True
    assert len(fake_session.executed) == 1
    _, params = fake_session.executed[0]
    assert params["endpoint"] == "/v1/operadoras"
    assert params["hash_ip"] is not None
