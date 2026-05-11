from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _bloquear_log_uso_real(monkeypatch: pytest.MonkeyPatch) -> None:
    """Evita persistir `plataforma.log_uso` em testes que usam TestClient.

    Mesmo motivo do conftest em `api/tests/`: o middleware
    `registrar_tempo_requisicao` tentaria inserir UUIDs reais com FK,
    e os testes usam IDs sinteticos no `request.state`.
    """

    async def _noop(*args, **kwargs):
        return None

    try:
        monkeypatch.setattr(
            "api.app.middleware.log_requisicao.registrar_log_uso",
            _noop,
        )
    except (ImportError, AttributeError):
        return
