from unittest.mock import AsyncMock, patch

import pytest

from ingestao.app.identificar_layout import identificar_layout

pytestmark = pytest.mark.asyncio


@patch("ingestao.app.identificar_layout.validar_arquivo_layout", new_callable=AsyncMock)
async def test_identificar_layout_via_servico_real(mock_validar_arquivo_layout: AsyncMock) -> None:
    mock_validar_arquivo_layout.return_value = {
        "dataset_codigo": "cadop",
        "nome_arquivo": "cadop.csv",
        "assinatura_detectada": "sha256:abc",
        "compativel": True,
        "layout_id": "layout_cadop_csv",
        "layout_versao_id": "layout_cadop_csv:v1",
        "motivos": [],
        "colunas_mapeadas": [{"origem": "Registro ANS", "destino_raw": "registro_ans"}],
    }

    resultado = await identificar_layout(
        dataset_codigo="cadop",
        colunas_detectadas=["Registro ANS"],
        nome_arquivo="cadop.csv",
    )

    assert resultado.compativel is True
    assert resultado.layout_id == "layout_cadop_csv"
    assert resultado.colunas_mapeadas[0]["destino_raw"] == "registro_ans"
