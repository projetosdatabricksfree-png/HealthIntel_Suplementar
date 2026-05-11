"""Testes unitários para os parsers do módulo ingestao_delta_ans (Sprint 41).

Cada teste verifica que a função de ingestão:
1. Chama baixar_arquivo com o dataset_codigo correto.
2. Passa os registros para processar_arquivo_bruto.
3. Retorna o resultado do pipeline.
"""

from __future__ import annotations

import io
import zipfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

pytestmark = pytest.mark.asyncio

_PIPELINE_RESULT = {
    "status": "carregado",
    "lote_id": "lote-delta-test",
    "tabela_destino": "bruto_ans.test",
    "total_registros": 1,
}

_ARQUIVO_MOCK = {
    "path": "/tmp/fake.csv",
    "arquivo_origem": "fake.csv",
    "hash_arquivo": "sha256:fake",
}


def _mock_csv_path(tmp_path: Path, conteudo: str = "col_a;col_b\nval1;val2\n") -> Path:
    p = tmp_path / "fake.csv"
    p.write_text(conteudo, encoding="utf-8")
    return p


def _make_mocks(path: str):
    arquivo_mock = {**_ARQUIVO_MOCK, "path": path}
    baixar = AsyncMock(return_value=arquivo_mock)
    pipeline = AsyncMock(return_value=_PIPELINE_RESULT)
    return baixar, pipeline


@patch("ingestao.app.ingestao_delta_ans.processar_arquivo_bruto", new_callable=AsyncMock)
@patch("ingestao.app.ingestao_delta_ans.baixar_arquivo", new_callable=AsyncMock)
async def test_ingestao_produto_caracteristica_chama_pipeline(
    mock_baixar: AsyncMock, mock_pipeline: AsyncMock, tmp_path: Path
) -> None:
    p = _mock_csv_path(tmp_path)
    mock_baixar.return_value = {**_ARQUIVO_MOCK, "path": str(p)}
    mock_pipeline.return_value = _PIPELINE_RESULT

    from ingestao.app.ingestao_delta_ans import executar_ingestao_produto_caracteristica

    resultado = await executar_ingestao_produto_caracteristica("202501")

    mock_baixar.assert_called_once()
    assert mock_baixar.call_args[0][0] == "produto_caracteristica"
    mock_pipeline.assert_called_once()
    assert resultado["status"] == "carregado"


@patch("ingestao.app.ingestao_delta_ans.processar_arquivo_bruto", new_callable=AsyncMock)
@patch("ingestao.app.ingestao_delta_ans.baixar_arquivo", new_callable=AsyncMock)
async def test_ingestao_historico_plano_chama_pipeline(
    mock_baixar: AsyncMock, mock_pipeline: AsyncMock, tmp_path: Path
) -> None:
    p = _mock_csv_path(tmp_path)
    mock_baixar.return_value = {**_ARQUIVO_MOCK, "path": str(p)}
    mock_pipeline.return_value = _PIPELINE_RESULT

    from ingestao.app.ingestao_delta_ans import executar_ingestao_historico_plano

    resultado = await executar_ingestao_historico_plano("202501")

    assert mock_baixar.call_args[0][0] == "historico_plano"
    assert resultado["status"] == "carregado"


@patch("ingestao.app.ingestao_delta_ans.processar_arquivo_bruto", new_callable=AsyncMock)
@patch("ingestao.app.ingestao_delta_ans.baixar_arquivo", new_callable=AsyncMock)
async def test_ingestao_plano_servico_opcional_chama_pipeline(
    mock_baixar: AsyncMock, mock_pipeline: AsyncMock, tmp_path: Path
) -> None:
    p = _mock_csv_path(tmp_path)
    mock_baixar.return_value = {**_ARQUIVO_MOCK, "path": str(p)}
    mock_pipeline.return_value = _PIPELINE_RESULT

    from ingestao.app.ingestao_delta_ans import executar_ingestao_plano_servico_opcional

    resultado = await executar_ingestao_plano_servico_opcional("202501")

    assert mock_baixar.call_args[0][0] == "plano_servico_opcional"
    assert resultado["status"] == "carregado"


@patch("ingestao.app.ingestao_delta_ans.processar_arquivo_bruto", new_callable=AsyncMock)
@patch("ingestao.app.ingestao_delta_ans.baixar_arquivo", new_callable=AsyncMock)
async def test_ingestao_quadro_auxiliar_corresponsabilidade_chama_pipeline(
    mock_baixar: AsyncMock, mock_pipeline: AsyncMock, tmp_path: Path
) -> None:
    p = _mock_csv_path(tmp_path)
    mock_baixar.return_value = {**_ARQUIVO_MOCK, "path": str(p)}
    mock_pipeline.return_value = _PIPELINE_RESULT

    from ingestao.app.ingestao_delta_ans import (
        executar_ingestao_quadro_auxiliar_corresponsabilidade,
    )

    resultado = await executar_ingestao_quadro_auxiliar_corresponsabilidade("202501")

    assert mock_baixar.call_args[0][0] == "quadro_auxiliar_corresponsabilidade"
    assert resultado["status"] == "carregado"


@patch("ingestao.app.ingestao_delta_ans.processar_arquivo_bruto", new_callable=AsyncMock)
@patch("ingestao.app.ingestao_delta_ans.baixar_arquivo", new_callable=AsyncMock)
async def test_ingestao_tuss_oficial_chama_pipeline(
    mock_baixar: AsyncMock, mock_pipeline: AsyncMock, tmp_path: Path
) -> None:
    # TUSS usa ZIP — criar arquivo zip falso com CSV interno
    csv_bytes = b"codigo_tuss;descricao\n123456;CONSULTA MEDICA\n"
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("TUSS.csv", csv_bytes)
    zip_path = tmp_path / "TUSS.zip"
    zip_path.write_bytes(buf.getvalue())

    mock_baixar.return_value = {**_ARQUIVO_MOCK, "path": str(zip_path)}
    mock_pipeline.return_value = _PIPELINE_RESULT

    from ingestao.app.ingestao_delta_ans import executar_ingestao_tuss_oficial

    resultado = await executar_ingestao_tuss_oficial("202501")

    assert mock_baixar.call_args[0][0] == "tuss_oficial"
    assert resultado["status"] == "carregado"


@patch("ingestao.app.ingestao_delta_ans.processar_arquivo_bruto", new_callable=AsyncMock)
@patch("ingestao.app.ingestao_delta_ans.baixar_arquivo", new_callable=AsyncMock)
async def test_ingestao_tiss_ambulatorial_chama_pipeline(
    mock_baixar: AsyncMock, mock_pipeline: AsyncMock, tmp_path: Path
) -> None:
    p = _mock_csv_path(tmp_path)
    mock_baixar.return_value = {**_ARQUIVO_MOCK, "path": str(p)}
    mock_pipeline.return_value = _PIPELINE_RESULT

    from ingestao.app.ingestao_delta_ans import executar_ingestao_tiss_ambulatorial

    resultado = await executar_ingestao_tiss_ambulatorial("202501")

    assert mock_baixar.call_args[0][0] == "tiss_ambulatorial"
    assert resultado["status"] == "carregado"


@patch("ingestao.app.ingestao_delta_ans.processar_arquivo_bruto", new_callable=AsyncMock)
@patch("ingestao.app.ingestao_delta_ans.baixar_arquivo", new_callable=AsyncMock)
async def test_ingestao_sip_mapa_assistencial_chama_pipeline(
    mock_baixar: AsyncMock, mock_pipeline: AsyncMock, tmp_path: Path
) -> None:
    p = _mock_csv_path(tmp_path)
    mock_baixar.return_value = {**_ARQUIVO_MOCK, "path": str(p)}
    mock_pipeline.return_value = _PIPELINE_RESULT

    from ingestao.app.ingestao_delta_ans import executar_ingestao_sip_mapa_assistencial

    resultado = await executar_ingestao_sip_mapa_assistencial("202501")

    assert mock_baixar.call_args[0][0] == "sip_mapa_assistencial"
    assert resultado["status"] == "carregado"


@patch("ingestao.app.ingestao_delta_ans.processar_arquivo_bruto", new_callable=AsyncMock)
@patch("ingestao.app.ingestao_delta_ans.baixar_arquivo", new_callable=AsyncMock)
async def test_ingestao_ressarcimento_sus_operadora_plano_chama_pipeline(
    mock_baixar: AsyncMock, mock_pipeline: AsyncMock, tmp_path: Path
) -> None:
    p = _mock_csv_path(tmp_path)
    mock_baixar.return_value = {**_ARQUIVO_MOCK, "path": str(p)}
    mock_pipeline.return_value = _PIPELINE_RESULT

    from ingestao.app.ingestao_delta_ans import (
        executar_ingestao_ressarcimento_sus_operadora_plano,
    )

    resultado = await executar_ingestao_ressarcimento_sus_operadora_plano("202501")

    assert mock_baixar.call_args[0][0] == "ressarcimento_sus_operadora_plano"
    assert resultado["status"] == "carregado"


@patch("ingestao.app.ingestao_delta_ans.processar_arquivo_bruto", new_callable=AsyncMock)
@patch("ingestao.app.ingestao_delta_ans.baixar_arquivo", new_callable=AsyncMock)
async def test_ingestao_painel_precificacao_chama_pipeline(
    mock_baixar: AsyncMock, mock_pipeline: AsyncMock, tmp_path: Path
) -> None:
    p = _mock_csv_path(tmp_path)
    mock_baixar.return_value = {**_ARQUIVO_MOCK, "path": str(p)}
    mock_pipeline.return_value = _PIPELINE_RESULT

    from ingestao.app.ingestao_delta_ans import executar_ingestao_painel_precificacao

    resultado = await executar_ingestao_painel_precificacao("202501")

    assert mock_baixar.call_args[0][0] == "painel_precificacao"
    assert resultado["status"] == "carregado"


@patch("ingestao.app.ingestao_delta_ans.processar_arquivo_bruto", new_callable=AsyncMock)
@patch("ingestao.app.ingestao_delta_ans.baixar_arquivo", new_callable=AsyncMock)
async def test_ingestao_operadora_cancelada_chama_pipeline(
    mock_baixar: AsyncMock, mock_pipeline: AsyncMock, tmp_path: Path
) -> None:
    p = _mock_csv_path(tmp_path)
    mock_baixar.return_value = {**_ARQUIVO_MOCK, "path": str(p)}
    mock_pipeline.return_value = _PIPELINE_RESULT

    from ingestao.app.ingestao_delta_ans import executar_ingestao_operadora_cancelada

    resultado = await executar_ingestao_operadora_cancelada("202501")

    assert mock_baixar.call_args[0][0] == "operadora_cancelada"
    assert resultado["status"] == "carregado"


@patch("ingestao.app.ingestao_delta_ans.processar_arquivo_bruto", new_callable=AsyncMock)
@patch("ingestao.app.ingestao_delta_ans.baixar_arquivo", new_callable=AsyncMock)
async def test_ingestao_penalidade_operadora_chama_pipeline(
    mock_baixar: AsyncMock, mock_pipeline: AsyncMock, tmp_path: Path
) -> None:
    p = _mock_csv_path(tmp_path)
    mock_baixar.return_value = {**_ARQUIVO_MOCK, "path": str(p)}
    mock_pipeline.return_value = _PIPELINE_RESULT

    from ingestao.app.ingestao_delta_ans import executar_ingestao_penalidade_operadora

    resultado = await executar_ingestao_penalidade_operadora("202501")

    assert mock_baixar.call_args[0][0] == "penalidade_operadora"
    assert resultado["status"] == "carregado"


@patch("ingestao.app.ingestao_delta_ans.processar_arquivo_bruto", new_callable=AsyncMock)
@patch("ingestao.app.ingestao_delta_ans.baixar_arquivo", new_callable=AsyncMock)
async def test_ingestao_beneficiario_regiao_geografica_chama_pipeline(
    mock_baixar: AsyncMock, mock_pipeline: AsyncMock, tmp_path: Path
) -> None:
    p = _mock_csv_path(tmp_path)
    mock_baixar.return_value = {**_ARQUIVO_MOCK, "path": str(p)}
    mock_pipeline.return_value = _PIPELINE_RESULT

    from ingestao.app.ingestao_delta_ans import (
        executar_ingestao_beneficiario_regiao_geografica,
    )

    resultado = await executar_ingestao_beneficiario_regiao_geografica("202501")

    assert mock_baixar.call_args[0][0] == "beneficiario_regiao_geografica"
    assert resultado["status"] == "carregado"


@patch("ingestao.app.ingestao_delta_ans.processar_arquivo_bruto", new_callable=AsyncMock)
@patch("ingestao.app.ingestao_delta_ans.baixar_arquivo", new_callable=AsyncMock)
async def test_ingestao_csv_zip_extrai_e_processa(
    mock_baixar: AsyncMock, mock_pipeline: AsyncMock, tmp_path: Path
) -> None:
    """Garante que arquivos ZIP com CSV interno são extraídos antes do processamento."""
    csv_bytes = b"col_a;col_b\nval1;val2\n"
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("dados.csv", csv_bytes)
    zip_path = tmp_path / "dados.zip"
    zip_path.write_bytes(buf.getvalue())

    mock_baixar.return_value = {**_ARQUIVO_MOCK, "path": str(zip_path)}
    mock_pipeline.return_value = _PIPELINE_RESULT

    from ingestao.app.ingestao_delta_ans import executar_ingestao_produto_caracteristica

    await executar_ingestao_produto_caracteristica("202501")

    # pipeline deve ter sido chamado com registros extraídos do CSV interno
    call_kwargs = mock_pipeline.call_args[1]
    assert len(call_kwargs.get("registros", [])) > 0


@patch("ingestao.app.ingestao_delta_ans.processar_arquivo_bruto", new_callable=AsyncMock)
@patch("ingestao.app.ingestao_delta_ans.baixar_arquivo", new_callable=AsyncMock)
async def test_ingestao_propagates_competencia_quando_ausente(
    mock_baixar: AsyncMock, mock_pipeline: AsyncMock, tmp_path: Path
) -> None:
    """Garante que competencia é injetada via setdefault quando não vem no CSV."""
    csv_bytes = b"registro_ans;nome\n123456;OPERADORA X\n"
    p = tmp_path / "sem_competencia.csv"
    p.write_bytes(csv_bytes)

    mock_baixar.return_value = {**_ARQUIVO_MOCK, "path": str(p)}
    mock_pipeline.return_value = _PIPELINE_RESULT

    from ingestao.app.ingestao_delta_ans import executar_ingestao_produto_caracteristica

    await executar_ingestao_produto_caracteristica("202506")

    registros = mock_pipeline.call_args[1].get("registros", [])
    assert all(r.get("competencia") == "202506" for r in registros)
