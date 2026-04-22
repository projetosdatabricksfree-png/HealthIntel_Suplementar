from unittest.mock import AsyncMock, patch

import pytest

from ingestao.app.pipeline_bronze import processar_arquivo_bruto

pytestmark = pytest.mark.asyncio


@patch("ingestao.app.pipeline_bronze.carregar_dataset_bruto", new_callable=AsyncMock)
@patch("ingestao.app.pipeline_bronze.identificar_layout", new_callable=AsyncMock)
async def test_processa_arquivo_e_carrega_bruto(
    mock_identificar_layout: AsyncMock,
    mock_carregar_dataset_bruto: AsyncMock,
) -> None:
    mock_identificar_layout.return_value = type(
        "IdentificacaoMock",
        (),
        {
            "compativel": True,
            "layout_id": "layout_cadop_csv",
            "layout_versao_id": "layout_cadop_csv:v1",
            "assinatura_colunas": "sha256:estrutura",
            "motivos": [],
            "colunas_mapeadas": [
                {"origem": "Registro ANS", "destino_raw": "registro_ans"},
                {"origem": "competência", "destino_raw": "competencia"},
            ],
        },
    )()
    mock_carregar_dataset_bruto.return_value = type(
        "LoteMock",
        (),
        {
            "lote_id": "lote-1",
            "tabela_destino": "bruto_ans.cadop",
            "total_registros": 1,
        },
    )()

    resultado = await processar_arquivo_bruto(
        dataset_codigo="cadop",
        nome_arquivo="cadop_202603.csv",
        hash_arquivo="sha256:arquivo",
        registros=[{"Registro ANS": "123", "competência": "202603"}],
    )

    assert resultado["status"] == "carregado"
    assert resultado["tabela_destino"] == "bruto_ans.cadop"


@patch("ingestao.app.pipeline_bronze.registrar_quarentena", new_callable=AsyncMock)
@patch("ingestao.app.pipeline_bronze.identificar_layout", new_callable=AsyncMock)
async def test_processa_arquivo_e_envia_para_quarentena(
    mock_identificar_layout: AsyncMock,
    mock_registrar_quarentena: AsyncMock,
) -> None:
    mock_identificar_layout.return_value = type(
        "IdentificacaoMock",
        (),
        {
            "compativel": False,
            "layout_id": None,
            "layout_versao_id": None,
            "assinatura_colunas": "sha256:estrutura",
            "motivos": ["Nenhum layout cadastrado para o dataset."],
            "colunas_mapeadas": [],
        },
    )()
    mock_registrar_quarentena.return_value = "quarentena-1"

    resultado = await processar_arquivo_bruto(
        dataset_codigo="cadop",
        nome_arquivo="cadop_202603.csv",
        hash_arquivo="sha256:arquivo",
        registros=[{"Registro ANS": "123"}],
    )

    assert resultado["status"] == "quarentena"
    assert resultado["quarentena_id"] == "quarentena-1"
