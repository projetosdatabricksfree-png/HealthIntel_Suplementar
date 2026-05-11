from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi import Request

from api.app.main import app
from api.app.middleware.autenticacao import validar_api_key


def aplicar_fake_auth(
    *,
    endpoints: list[str] | None = None,
    camadas: list[str] | None = None,
    plano_nome: str = "premium",
    is_admin: bool = False,
):
    async def fake_auth(request: Request, x_api_key: str | None = None) -> str:
        request.state.chave_api = "teste"
        request.state.chave_api_id = "chave-teste"
        request.state.cliente_id = "cliente-teste"
        request.state.plano_id = "plano-teste"
        request.state.plano_nome = plano_nome
        request.state.limite_rpm = 1000
        request.state.endpoint_permitido = endpoints or ["/v1"]
        request.state.camadas_permitidas = camadas or ["bronze", "prata", "ouro"]
        request.state.is_admin = is_admin
        request.state.auth_cache = "miss"
        return "ok"

    return fake_auth


@pytest.fixture
def cliente_autenticado() -> Iterator[None]:
    app.dependency_overrides[validar_api_key] = aplicar_fake_auth()
    try:
        yield
    finally:
        app.dependency_overrides.pop(validar_api_key, None)


@pytest.fixture(autouse=True)
def _bloquear_log_uso_real(monkeypatch: pytest.MonkeyPatch) -> None:
    """Evita persistir `plataforma.log_uso` em testes que usam TestClient.

    O middleware `registrar_tempo_requisicao` chama `registrar_log_uso` apos
    cada response e tenta inserir UUIDs reais com FK em chave_api/cliente/plano.
    Como os testes usam IDs sinteticos no `request.state`, o insert falharia.
    O patch ocorre no ponto de import do middleware; testes que importam
    `registrar_log_uso` direto de `api.app.services.uso` nao sao afetados.
    """

    async def _noop(*args, **kwargs):
        return None

    monkeypatch.setattr(
        "api.app.middleware.log_requisicao.registrar_log_uso",
        _noop,
    )


__all__ = ["aplicar_fake_auth", "cliente_autenticado"]
