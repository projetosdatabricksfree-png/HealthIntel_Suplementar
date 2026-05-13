"""Testes da ingestao delta ANS real (Sprint 41/42)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from ingestao.app import ingestao_delta_ans as delta


def test_ler_csv_bytes_rejeita_html() -> None:
    with pytest.raises(ValueError, match="HTML"):
        delta._ler_csv_bytes(b"<!doctype html><html><body>index</body></html>")


def test_ler_csv_bytes_detecta_delimitador_ponto_virgula() -> None:
    registros = delta._ler_csv_bytes(b"col_a;col_b\nvalor_a;valor_b\n")

    assert registros == [{"col_a": "valor_a", "col_b": "valor_b"}]


def test_normalizar_produto_caracteristica_para_raw_delta() -> None:
    registros = delta._normalizar_registros(
        "produto_caracteristica",
        [
            {
                "CD_PLANO": "123",
                "NM_PLANO": "Plano X",
                "REGISTRO_OPERADORA": "582",
                "DT_ATUALIZACAO": "2025-03-31",
            }
        ],
        "202503",
        "produtos.csv",
    )

    assert registros[0]["registro_ans"] == "582"
    assert registros[0]["codigo_produto"] == "123"
    assert registros[0]["nome_produto"] == "Plano X"
    assert registros[0]["competencia"] == 202503


def test_normalizar_quadro_auxiliar_com_valor_decimal() -> None:
    registros = delta._normalizar_registros(
        "quadro_auxiliar_corresponsabilidade",
        [
            {
                "CD_OPERADORA": "000701",
                "DE_CORRESPONSABILIDADE": "Corresponsabilidade cedida",
                "VL_SALDO_FINAL": "1.234,56",
            }
        ],
        "202501",
        "QUADRO AUXILIAR 1.csv",
    )

    assert registros[0]["registro_ans"] == "000701"
    assert str(registros[0]["valor_corresponsabilidade"]) == "1234.56"


@pytest.mark.asyncio
async def test_resolver_fontes_diretorio_filtra_arquivos_tabulares() -> None:
    with patch(
        "ingestao.app.ingestao_delta_ans._listar_links",
        new=AsyncMock(
            return_value=[
                "https://dadosabertos.ans.gov.br/FTP/PDA/base/dicionario.ods",
                "https://dadosabertos.ans.gov.br/FTP/PDA/base/dados_202401.csv",
                "https://dadosabertos.ans.gov.br/FTP/PDA/base/readme.html",
            ]
        ),
    ):
        fontes = await delta._resolver_fontes(
            dataset_codigo="teste",
            familia="familia",
            competencia="202501",
            base_url="https://dadosabertos.ans.gov.br/FTP/PDA/base/",
            padrao=r"dados_20\d{4}\.csv$",
        )

    assert [fonte.nome_arquivo for fonte in fontes] == ["dados_202401.csv"]


@pytest.mark.asyncio
async def test_resolver_fontes_diretorio_sem_csv_falha_explicita() -> None:
    with patch(
        "ingestao.app.ingestao_delta_ans._listar_links",
        new=AsyncMock(return_value=["https://dadosabertos.ans.gov.br/FTP/PDA/base/index.html"]),
    ):
        with pytest.raises(RuntimeError, match="Nenhum arquivo tabular"):
            await delta._resolver_fontes(
                dataset_codigo="teste",
                familia="familia",
                competencia="202501",
                base_url="https://dadosabertos.ans.gov.br/FTP/PDA/base/",
            )


@pytest.mark.asyncio
async def test_processar_fonte_registra_baixado_e_carregado(tmp_path: Path) -> None:
    arquivo = tmp_path / "dados.csv"
    arquivo.write_text("col_a;col_b\n1;2\n", encoding="utf-8")
    fonte = delta.FonteDelta(
        dataset_codigo="dataset",
        familia="familia",
        url="https://dadosabertos.ans.gov.br/FTP/PDA/base/dados.csv",
        nome_arquivo="dados.csv",
        competencia="202501",
    )

    with (
        patch(
            "ingestao.app.ingestao_delta_ans._baixar_fonte",
            new=AsyncMock(
                return_value={
                    "path": str(arquivo),
                    "arquivo_origem": "dados.csv",
                    "hash_arquivo": "sha256:test",
                    "tamanho_bytes": "14",
                }
            ),
        ),
        patch(
            "ingestao.app.ingestao_delta_ans._registrar_arquivo_fonte",
            new=AsyncMock(),
        ) as registrar,
        patch(
            "ingestao.app.ingestao_delta_ans.processar_arquivo_bruto",
            new=AsyncMock(
                return_value={
                    "status": "carregado",
                    "lote_id": "lote",
                    "tabela_destino": "bruto_ans.dataset",
                    "total_registros": 1,
                }
            ),
        ),
    ):
        resultado = await delta._processar_fonte(fonte, normalizar=False)

    assert resultado["status"] == "carregado"
    assert [call.args[2] for call in registrar.call_args_list] == ["baixado", "carregado"]


@pytest.mark.asyncio
async def test_ingestao_produto_usa_discovery_e_carga_direta() -> None:
    fonte = delta.FonteDelta(
        dataset_codigo="produto_caracteristica",
        familia="produtos_planos",
        url="https://dadosabertos.ans.gov.br/FTP/PDA/produtos.csv",
        nome_arquivo="produtos.csv",
        competencia="202501",
    )
    with (
        patch(
            "ingestao.app.ingestao_delta_ans._resolver_fontes",
            new=AsyncMock(return_value=[fonte]),
        ) as resolver,
        patch(
            "ingestao.app.ingestao_delta_ans._processar_fonte",
            new=AsyncMock(return_value={"status": "carregado", "total_registros": 1}),
        ) as processar,
    ):
        resultado = await delta.executar_ingestao_produto_caracteristica("202501")

    assert resultado["status"] == "carregado"
    assert resolver.call_args.kwargs["padrao"].endswith(r"\.csv$")
    assert processar.call_args.kwargs["direto"] is True


@pytest.mark.asyncio
async def test_ingestao_tiss_usa_resolucao_hierarquica_e_carga_direta() -> None:
    fonte = delta.FonteDelta(
        dataset_codigo="tiss_ambulatorial",
        familia="tiss",
        url="https://dadosabertos.ans.gov.br/FTP/PDA/TISS/AMBULATORIAL/2024/SP/a.zip",
        nome_arquivo="SP_202412_AMB_REM.zip",
        competencia="202412",
    )
    with (
        patch(
            "ingestao.app.ingestao_delta_ans._resolver_fontes_tiss",
            new=AsyncMock(return_value=[fonte]),
        ) as resolver,
        patch(
            "ingestao.app.ingestao_delta_ans._processar_fonte",
            new=AsyncMock(return_value={"status": "carregado", "total_registros": 1}),
        ) as processar,
    ):
        resultado = await delta.executar_ingestao_tiss_ambulatorial("202604")

    assert resultado["status"] == "carregado"
    assert resolver.call_args.kwargs["subfamilia"] == "AMBULATORIAL"
    assert processar.call_args.kwargs["direto"] is True
