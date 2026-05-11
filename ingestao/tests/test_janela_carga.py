from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy import text

from ingestao.app.carregar_postgres import SessionLocal, _validar_janela_temporal
from ingestao.app.janela_carga import (
    ConfiguracaoJanelaInvalidaError,
    DatasetNaoTemporalError,
    HistoricoForaDaJanelaError,
    JanelaCarga,
    PoliticaDatasetNaoEncontradaError,
    assegurar_dentro_da_janela_ou_falhar,
    competencia_dentro_janela,
    filtrar_competencias_janela,
    garantir_particoes_dataset,
    normalizar_competencia,
    obter_anos_carga_default,
    obter_janela,
    registrar_decisao,
)
from ingestao.tests._psql import aplicar_arquivo

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module", autouse=True)
def _aplicar_bootstrap_janela() -> None:
    aplicar_arquivo(ROOT / "infra/postgres/init/031_fase7_janela_carga.sql")


@pytest.fixture(autouse=True)
async def _descartar_pool_asyncpg() -> None:
    yield
    from ingestao.app.carregar_postgres import engine

    await engine.dispose()


@pytest.fixture
def janela_sib() -> JanelaCarga:
    return JanelaCarga(
        dataset_codigo="sib_operadora",
        classe_dataset="grande_temporal",
        estrategia_carga="ano_vigente_mais_ano_anterior",
        anos_carga_hot=2,
        competencia_minima=202501,
        competencia_maxima_exclusiva=202701,
        ano_inicial=2025,
        ano_final=2026,
        ano_preparado=2027,
        schema_destino="bruto_ans",
        tabela_destino="sib_beneficiario_operadora",
        coluna_competencia="competencia",
        particionar_por_ano=True,
    )


async def _scalar(sql: str, params: dict | None = None):
    async with SessionLocal() as session:
        return await session.scalar(text(sql), params or {})


def test_obter_anos_carga_default_sem_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ANS_ANOS_CARGA_HOT", raising=False)
    assert obter_anos_carga_default() == 2


def test_obter_anos_carga_env_invalido(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANS_ANOS_CARGA_HOT", "abc")
    with pytest.raises(ConfiguracaoJanelaInvalidaError):
        obter_anos_carga_default()


def test_obter_anos_carga_env_menor_que_1(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANS_ANOS_CARGA_HOT", "0")
    with pytest.raises(ConfiguracaoJanelaInvalidaError):
        obter_anos_carga_default()


def test_obter_anos_carga_env_valido(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANS_ANOS_CARGA_HOT", "3")
    assert obter_anos_carga_default() == 3


def test_competencia_dentro_janela(janela_sib: JanelaCarga) -> None:
    assert competencia_dentro_janela(202501, janela_sib) is True
    assert competencia_dentro_janela(202612, janela_sib) is True
    assert competencia_dentro_janela(202412, janela_sib) is False
    assert competencia_dentro_janela(202701, janela_sib) is False


@pytest.mark.parametrize("valor", ["", "abc", "202613"])
def test_normalizar_competencia_invalida(valor: str) -> None:
    with pytest.raises(ValueError):
        normalizar_competencia(valor)


@pytest.mark.asyncio
async def test_obter_janela_sib_operadora() -> None:
    janela = await obter_janela("sib_operadora")

    assert janela.dataset_codigo == "sib_operadora"
    assert janela.competencia_minima == 202501
    assert janela.competencia_maxima_exclusiva == 202701
    assert janela.ano_preparado == 2027


@pytest.mark.asyncio
async def test_obter_janela_com_conexao_existente() -> None:
    async with SessionLocal() as session:
        janela = await obter_janela("sib_operadora", conn=session)

    assert janela.dataset_codigo == "sib_operadora"


@pytest.mark.asyncio
async def test_dataset_inexistente_falha() -> None:
    with pytest.raises(PoliticaDatasetNaoEncontradaError):
        await obter_janela("dataset_fake")


@pytest.mark.asyncio
@pytest.mark.parametrize("dataset_codigo", ["cadop", "idss", "rol_procedimento"])
async def test_dataset_nao_temporal_falha(dataset_codigo: str) -> None:
    with pytest.raises(DatasetNaoTemporalError):
        await obter_janela(dataset_codigo)


@pytest.mark.asyncio
@pytest.mark.parametrize("dataset_codigo", ["cadop", "idss"])
async def test_loader_generico_dataset_nao_temporal_nao_bloqueia_janela(
    dataset_codigo: str,
) -> None:
    janela, competencia = await _validar_janela_temporal(dataset_codigo, "202001")

    assert janela is None
    assert competencia is None


@pytest.mark.asyncio
async def test_loader_generico_dataset_sem_politica_nao_bloqueia_janela() -> None:
    janela, competencia = await _validar_janela_temporal("dataset_legado", "202001")

    assert janela is None
    assert competencia is None


@pytest.mark.asyncio
async def test_registrar_decisao_ignorado_fora_janela(janela_sib: JanelaCarga) -> None:
    await registrar_decisao(
        "sib_operadora",
        202412,
        "ignorado_fora_janela",
        janela_sib,
        "Teste de auditoria fora da janela.",
    )

    total = await _scalar(
        """
        select count(*)
        from plataforma.ingestao_janela_decisao
        where dataset_codigo = 'sib_operadora'
          and competencia = 202412
          and acao = 'ignorado_fora_janela'
        """
    )
    assert total >= 1


@pytest.mark.asyncio
async def test_registrar_decisao_acao_invalida(janela_sib: JanelaCarga) -> None:
    with pytest.raises(ValueError):
        await registrar_decisao("sib_operadora", 202412, "acao_invalida", janela_sib)


@pytest.mark.asyncio
async def test_registrar_decisao_com_conexao_existente(janela_sib: JanelaCarga) -> None:
    async with SessionLocal() as session:
        async with session.begin():
            await registrar_decisao(
                "sib_operadora",
                202412,
                "ignorado_fora_janela",
                janela_sib,
                "Teste em transacao controlada.",
                session,
            )
            total = await session.scalar(
                text(
                    """
                    select count(*)
                    from plataforma.ingestao_janela_decisao
                    where dataset_codigo = 'sib_operadora'
                      and competencia = 202412
                      and acao = 'ignorado_fora_janela'
                    """
                )
            )

    assert total >= 1


@pytest.mark.asyncio
async def test_assegurar_fora_janela_sem_flag_falha(janela_sib: JanelaCarga) -> None:
    with pytest.raises(HistoricoForaDaJanelaError):
        await assegurar_dentro_da_janela_ou_falhar(202412, janela_sib)

    total = await _scalar(
        """
        select count(*)
        from plataforma.ingestao_janela_decisao
        where dataset_codigo = 'sib_operadora'
          and competencia = 202412
          and acao = 'rejeitado_historico_sem_flag'
        """
    )
    assert total >= 1


@pytest.mark.asyncio
async def test_assegurar_dentro_janela_retorna_sem_registro(janela_sib: JanelaCarga) -> None:
    await assegurar_dentro_da_janela_ou_falhar(202602, janela_sib)


@pytest.mark.asyncio
async def test_assegurar_fora_janela_com_flag_historico_permite(
    janela_sib: JanelaCarga,
) -> None:
    await assegurar_dentro_da_janela_ou_falhar(
        202412,
        janela_sib,
        permitir_historico=True,
    )


@pytest.mark.asyncio
async def test_limite_superior_exclusivo(janela_sib: JanelaCarga) -> None:
    with pytest.raises(HistoricoForaDaJanelaError):
        await assegurar_dentro_da_janela_ou_falhar(202701, janela_sib, registrar=False)


@pytest.mark.asyncio
async def test_filtrar_competencias_janela() -> None:
    dentro, fora = await filtrar_competencias_janela(
        "sib_operadora",
        [202412, 202501, 202602, 202701],
    )

    assert dentro == [202501, 202602]
    assert fora == [202412, 202701]


@pytest.mark.asyncio
async def test_garantir_particoes_dataset() -> None:
    janela = await obter_janela("sib_operadora")
    await garantir_particoes_dataset(janela)

    total = await _scalar(
        """
        select count(*)
        from pg_inherits
        where inhparent = 'bruto_ans.sib_beneficiario_operadora'::regclass
          and inhrelid::regclass::text in (
              'bruto_ans.sib_beneficiario_operadora_2025',
              'bruto_ans.sib_beneficiario_operadora_2026',
              'bruto_ans.sib_beneficiario_operadora_2027',
              'bruto_ans.sib_beneficiario_operadora_default'
          )
        """
    )
    assert total == 4


@pytest.mark.asyncio
async def test_garantir_particoes_dataset_ignora_sem_particionamento(
    janela_sib: JanelaCarga,
) -> None:
    janela = JanelaCarga(
        dataset_codigo=janela_sib.dataset_codigo,
        classe_dataset=janela_sib.classe_dataset,
        estrategia_carga=janela_sib.estrategia_carga,
        anos_carga_hot=janela_sib.anos_carga_hot,
        competencia_minima=janela_sib.competencia_minima,
        competencia_maxima_exclusiva=janela_sib.competencia_maxima_exclusiva,
        ano_inicial=janela_sib.ano_inicial,
        ano_final=janela_sib.ano_final,
        ano_preparado=janela_sib.ano_preparado,
        schema_destino=None,
        tabela_destino=None,
        coluna_competencia=janela_sib.coluna_competencia,
        particionar_por_ano=False,
    )

    await garantir_particoes_dataset(janela)


@pytest.mark.asyncio
async def test_garantir_particoes_dataset_com_conexao_existente() -> None:
    janela = await obter_janela("sib_operadora")
    async with SessionLocal() as session:
        await garantir_particoes_dataset(janela, conn=session)


def test_dag_mensal_nao_usa_permitir_historico_true() -> None:
    arquivos = [
        *ROOT.joinpath("ingestao/dags").glob("*.py"),
        *ROOT.joinpath("ingestao/app").glob("*.py"),
        *ROOT.joinpath("scripts").glob("*.py"),
    ]
    ocorrencias = [
        str(path.relative_to(ROOT))
        for path in arquivos
        if "permitir_historico=True" in path.read_text()
    ]
    assert ocorrencias == []


def test_sem_hardcode_ano_produtivo() -> None:
    arquivos = [
        ROOT / "ingestao/app/janela_carga.py",
        ROOT / "ingestao/app/ingestao_real.py",
        ROOT / "ingestao/app/carregar_postgres.py",
        ROOT / "ingestao/app/pipeline_bronze.py",
    ]
    ocorrencias = []
    for path in arquivos:
        for numero_linha, linha in enumerate(path.read_text().splitlines(), start=1):
            if any(ano in linha for ano in ("2025", "2026", "2027")):
                ocorrencias.append(f"{path.relative_to(ROOT)}:{numero_linha}")
    assert ocorrencias == []
