from unittest.mock import AsyncMock, patch

import pytest

from mongo_layout_service.app.services.health import obter_prontidao

pytestmark = pytest.mark.asyncio


@patch("mongo_layout_service.app.services.health.get_database")
async def test_obter_prontidao_retorna_status_ok(mock_get_database) -> None:
    mock_get_database.return_value = type(
        "MongoMock",
        (),
        {"command": AsyncMock(return_value={"ok": 1})},
    )()

    payload = await obter_prontidao()

    assert payload["status"] == "ok"
    assert payload["dependencias"]["mongo"]["status"] == "ok"
