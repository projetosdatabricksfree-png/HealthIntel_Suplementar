from unittest.mock import patch

import pytest

from api.app.services.layout_admin import listar_layouts

pytestmark = pytest.mark.asyncio


class FakeAsyncClient:
    captured_headers: dict[str, str] = {}

    def __init__(self, *args, **kwargs) -> None:
        self.headers = kwargs["headers"]
        FakeAsyncClient.captured_headers = dict(self.headers)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None

    async def request(self, method: str, path: str, json=None, params=None):
        return type(
            "ResponseMock",
            (),
            {
                "raise_for_status": lambda self: None,
                "json": lambda self: {"dados": [], "metodo": method, "path": path},
            },
        )()


@patch("api.app.services.layout_admin.httpx.AsyncClient", FakeAsyncClient)
async def test_layout_admin_envia_service_token() -> None:
    resultado = await listar_layouts()

    assert resultado["dados"] == []
    assert FakeAsyncClient.captured_headers["X-Service-Token"]
