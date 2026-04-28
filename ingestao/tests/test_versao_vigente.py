"""Sprint 37 — Testes do helper de versão vigente."""

from __future__ import annotations

import hashlib
import subprocess
from datetime import date
from pathlib import Path

import pytest
from sqlalchemy import text

from ingestao.app.carga_versao_vigente import carregar_arquivo_versao_vigente
from ingestao.app.carregar_postgres import SessionLocal
from ingestao.app.versao_vigente import (
    DatasetNaoVersionadoError,
    PoliticaVersaoDatasetNaoEncontradaError,
    VersaoDatasetInvalidaError,
    calcular_hash_arquivo,
    descartar_versoes_antigas_em_bruto,
    garantir_unica_versao_vigente,
    obter_versao_vigente,
    politica_exige_apenas_ultima_versao,
    registrar_nova_versao,
)

ROOT = Path(__file__).resolve().parents[2]
COMPOSE = ["docker", "compose", "-f", "infra/docker-compose.yml"]
PSQL = [
    *COMPOSE,
    "exec",
    "-T",
    "postgres",
    "psql",
    "-v",
    "ON_ERROR_STOP=1",
    "-U",
    "healthintel",
    "-d",
    "healthintel",
]


@pytest.fixture(scope="module", autouse=True)
def _aplicar_bootstrap_versao() -> None:
    subprocess.run(
        PSQL,
        input=(ROOT / "infra/postgres/init/032_fase7_versao_dataset.sql").read_text(),
        text=True,
        cwd=ROOT,
        check=True,
        capture_output=True,
    )


@pytest.fixture(autouse=True)
async def _descartar_pool_asyncpg() -> None:
    yield
    from ingestao.app.carregar_postgres import engine

    await engine.dispose()


@pytest.fixture(autouse=True)
async def _limpar_versao_vigente() -> None:
    async with SessionLocal() as session:
        async with session.begin():
            await session.execute(
                text(
                    """
                    delete from plataforma.versao_dataset_vigente
                    where dataset_codigo in (
                        'tuss_procedimento',
                        'tuss_material_opme',
                        'tuss_medicamento',
                        'depara_sip_tuss',
                        'rol_procedimento',
                        'prestador_cadastral',
                        'qualiss',
                        'cnes_estabelecimento'
                    )
                    """
                )
            )
    yield


async def _scalar(sql: str, params: dict | None = None):
    async with SessionLocal() as session:
        return await session.scalar(text(sql), params or {})


def test_calcular_hash_arquivo_sha256(tmp_path: Path) -> None:
    arquivo = tmp_path / "tuss_v1.csv"
    conteudo = b"codigo;descricao\n10101012;Consulta\n"
    arquivo.write_bytes(conteudo)

    esperado = hashlib.sha256(conteudo).hexdigest()
    assert calcular_hash_arquivo(arquivo) == esperado


def test_calcular_hash_arquivo_md5_proibido(tmp_path: Path) -> None:
    arquivo = tmp_path / "tuss_v1.csv"
    arquivo.write_bytes(b"x")

    with pytest.raises(VersaoDatasetInvalidaError):
        calcular_hash_arquivo(arquivo, algoritmo="md5")


@pytest.mark.asyncio
async def test_politica_exige_apenas_ultima_versao_tuss() -> None:
    assert await politica_exige_apenas_ultima_versao("tuss_procedimento") is True
    assert await politica_exige_apenas_ultima_versao("rol_procedimento") is True
    assert await politica_exige_apenas_ultima_versao("depara_sip_tuss") is True


@pytest.mark.asyncio
async def test_politica_exige_apenas_ultima_versao_cnes_false() -> None:
    # cnes_estabelecimento é snapshot_atual com carregar_apenas_ultima_versao=false.
    assert await politica_exige_apenas_ultima_versao("cnes_estabelecimento") is False


@pytest.mark.asyncio
async def test_politica_dataset_inexistente_falha() -> None:
    with pytest.raises(PoliticaVersaoDatasetNaoEncontradaError):
        await politica_exige_apenas_ultima_versao("dataset_fake_inexistente")


@pytest.mark.asyncio
async def test_registrar_primeira_versao() -> None:
    resultado = await registrar_nova_versao(
        dataset_codigo="tuss_procedimento",
        versao="2026.01",
        url_fonte="https://www.gov.br/ans/tuss/2026.01.zip",
        hash_arquivo="a" * 64,
        publicado_em=date(2026, 1, 15),
        arquivo_bytes=1024,
        metadados={"layout": "tuss_v3", "linhas": 5000},
    )
    assert resultado == "nova_versao"

    vigente = await obter_versao_vigente("tuss_procedimento")
    assert vigente is not None
    assert vigente.versao == "2026.01"
    assert vigente.hash_arquivo == "a" * 64
    assert vigente.url_fonte == "https://www.gov.br/ans/tuss/2026.01.zip"
    assert vigente.publicado_em == date(2026, 1, 15)
    assert vigente.arquivo_bytes == 1024
    assert vigente.metadados == {"layout": "tuss_v3", "linhas": 5000}
    assert vigente.vigente is True


@pytest.mark.asyncio
async def test_registrar_mesmo_hash_idempotente() -> None:
    await registrar_nova_versao(
        "tuss_procedimento",
        "2026.01",
        "https://example.com/v1.zip",
        "b" * 64,
    )
    resultado = await registrar_nova_versao(
        "tuss_procedimento",
        "2026.01-rerun",
        "https://example.com/v1-mirror.zip",
        "b" * 64,
    )
    assert resultado == "nada_a_fazer"

    total_vigentes = await _scalar(
        """
        select count(*) from plataforma.versao_dataset_vigente
        where dataset_codigo='tuss_procedimento' and vigente=true
        """
    )
    assert total_vigentes == 1


@pytest.mark.asyncio
async def test_registrar_hash_diferente_inativa_anterior() -> None:
    await registrar_nova_versao(
        "tuss_procedimento",
        "2026.01",
        "https://example.com/v1.zip",
        "c" * 64,
    )
    await registrar_nova_versao(
        "tuss_procedimento",
        "2026.02",
        "https://example.com/v2.zip",
        "d" * 64,
    )

    total_total = await _scalar(
        """
        select count(*) from plataforma.versao_dataset_vigente
        where dataset_codigo='tuss_procedimento'
        """
    )
    total_vigentes = await _scalar(
        """
        select count(*) from plataforma.versao_dataset_vigente
        where dataset_codigo='tuss_procedimento' and vigente=true
        """
    )
    assert total_total == 2
    assert total_vigentes == 1

    vigente = await obter_versao_vigente("tuss_procedimento")
    assert vigente is not None
    assert vigente.versao == "2026.02"
    assert vigente.hash_arquivo == "d" * 64


@pytest.mark.asyncio
async def test_unique_vigente_impede_duas_vigentes() -> None:
    from sqlalchemy.exc import IntegrityError

    await registrar_nova_versao(
        "tuss_procedimento",
        "2026.01",
        "https://example.com/v1.zip",
        "e" * 64,
    )

    async with SessionLocal() as session:
        async with session.begin():
            with pytest.raises(IntegrityError):
                await session.execute(
                    text(
                        """
                        insert into plataforma.versao_dataset_vigente (
                            dataset_codigo, versao, url_fonte, hash_arquivo, vigente
                        ) values (
                            'tuss_procedimento','forcar_segunda',
                            'https://example.com/x.zip','f' || repeat('0',63), true
                        )
                        """
                    )
                )


@pytest.mark.asyncio
async def test_dataset_nao_versionado_falha() -> None:
    # sib_operadora é grande_temporal, fora das classes do manifesto.
    with pytest.raises(DatasetNaoVersionadoError):
        await registrar_nova_versao(
            "sib_operadora",
            "2026.01",
            "https://example.com/v1.zip",
            "0" * 64,
        )


@pytest.mark.asyncio
async def test_garantir_unica_versao_vigente_ok() -> None:
    await registrar_nova_versao(
        "tuss_procedimento",
        "2026.01",
        "https://example.com/v1.zip",
        "9" * 64,
    )
    # Não levanta exceção.
    await garantir_unica_versao_vigente("tuss_procedimento")


@pytest.mark.asyncio
async def test_garantir_unica_versao_vigente_zero_ok() -> None:
    # Sem registros: deve passar (carga inicial pode ainda não ter ocorrido).
    await garantir_unica_versao_vigente("tuss_material_opme")


@pytest.mark.asyncio
async def test_garantir_unica_versao_vigente_duas_falha() -> None:
    # O índice parcial deve impedir a transição de duas linhas para vigente=true.
    from sqlalchemy.exc import IntegrityError

    async with SessionLocal() as session:
        async with session.begin():
            await session.execute(
                text(
                    """
                    insert into plataforma.versao_dataset_vigente (
                        dataset_codigo, versao, url_fonte, hash_arquivo, vigente
                    ) values
                        ('tuss_procedimento','va','https://x.com/a.zip','aa', false),
                        ('tuss_procedimento','vb','https://x.com/b.zip','bb', false)
                    """
                )
            )

    async with SessionLocal() as session:
        async with session.begin():
            with pytest.raises(IntegrityError):
                await session.execute(
                    text(
                        """
                        update plataforma.versao_dataset_vigente
                           set vigente = true
                         where dataset_codigo='tuss_procedimento'
                        """
                    )
                )


@pytest.mark.asyncio
async def test_descartar_versoes_antigas_em_bruto_noop_sem_tabela() -> None:
    await registrar_nova_versao(
        "tuss_procedimento",
        "2026.01",
        "https://example.com/v1.zip",
        "1" * 64,
    )

    removidas = await descartar_versoes_antigas_em_bruto(
        schema="bruto_ans",
        tabela="tabela_que_nao_existe_xyz",
        dataset_codigo="tuss_procedimento",
    )
    assert removidas == 0


@pytest.mark.asyncio
async def test_descartar_versoes_antigas_em_bruto_noop_sem_coluna() -> None:
    await registrar_nova_versao(
        "tuss_procedimento",
        "2026.01",
        "https://example.com/v1.zip",
        "2" * 64,
    )
    # `cnes_estabelecimento` existe em bruto_ans mas não tem coluna `versao_dataset`.
    removidas = await descartar_versoes_antigas_em_bruto(
        schema="bruto_ans",
        tabela="cnes_estabelecimento",
        dataset_codigo="tuss_procedimento",
        coluna_versao="coluna_que_nao_existe",
    )
    assert removidas == 0


@pytest.mark.asyncio
async def test_descartar_versoes_antigas_em_bruto_remove_antigas() -> None:
    await registrar_nova_versao(
        "tuss_procedimento",
        "2026.02",
        "https://example.com/v2.zip",
        "3" * 64,
    )

    async with SessionLocal() as session:
        async with session.begin():
            await session.execute(
                text(
                    """
                    create temporary table tmp_tuss_proc (
                        codigo text,
                        versao_dataset text
                    ) on commit drop
                    """
                )
            )
            await session.execute(
                text(
                    """
                    insert into tmp_tuss_proc values
                        ('A', '2025.12'),
                        ('B', '2026.01'),
                        ('C', '2026.02'),
                        ('D', '2026.02')
                    """
                )
            )
            # Note: descartar_versoes_antigas_em_bruto consulta information_schema,
            # mas tabelas temporárias ficam em pg_temp e não aparecem em
            # information_schema.tables com schema='public'. Para validar a
            # lógica de delete, criamos tabela real de teste em schema reservado.
            await session.execute(text("create schema if not exists tmp_test_versao"))
            await session.execute(text("drop table if exists tmp_test_versao.tuss_proc"))
            await session.execute(
                text(
                    """
                    create table tmp_test_versao.tuss_proc (
                        codigo text,
                        versao_dataset text
                    )
                    """
                )
            )
            await session.execute(
                text(
                    """
                    insert into tmp_test_versao.tuss_proc values
                        ('A', '2025.12'),
                        ('B', '2026.01'),
                        ('C', '2026.02'),
                        ('D', '2026.02')
                    """
                )
            )

    try:
        removidas = await descartar_versoes_antigas_em_bruto(
            schema="tmp_test_versao",
            tabela="tuss_proc",
            dataset_codigo="tuss_procedimento",
        )
        assert removidas == 2

        restantes = await _scalar("select count(*) from tmp_test_versao.tuss_proc")
        assert restantes == 2

        versoes = await _scalar(
            "select count(distinct versao_dataset) from tmp_test_versao.tuss_proc"
        )
        assert versoes == 1
    finally:
        async with SessionLocal() as session:
            async with session.begin():
                await session.execute(text("drop schema if exists tmp_test_versao cascade"))


@pytest.mark.asyncio
async def test_descartar_versoes_antigas_skip_quando_politica_false() -> None:
    # cnes_estabelecimento tem carregar_apenas_ultima_versao=false; não deve descartar.
    removidas = await descartar_versoes_antigas_em_bruto(
        schema="bruto_ans",
        tabela="cnes_estabelecimento",
        dataset_codigo="cnes_estabelecimento",
    )
    assert removidas == 0


@pytest.mark.asyncio
async def test_classificacao_prestador_rede_sem_ambiguidade() -> None:
    total = await _scalar(
        """
        select count(*) from plataforma.politica_dataset
        where dataset_codigo in (
            'prestador_cadastral','qualiss','cnes_estabelecimento',
            'rede_assistencial','rede_vigente'
        )
          and classe_dataset not in ('snapshot_atual','referencia_versionada','grande_temporal')
        """
    )
    assert total == 0

    historico = await _scalar(
        """
        select count(*) from plataforma.politica_dataset
        where dataset_codigo in (
            'prestador_cadastral','qualiss','cnes_estabelecimento',
            'rede_assistencial','rede_vigente'
        )
          and classe_dataset = 'historico_sob_demanda'
        """
    )
    assert historico == 0


@pytest.mark.asyncio
async def test_obter_versao_vigente_inexistente_retorna_none() -> None:
    vigente = await obter_versao_vigente("qualiss")
    assert vigente is None


@pytest.mark.asyncio
async def test_registrar_versao_falta_argumento_falha() -> None:
    with pytest.raises(VersaoDatasetInvalidaError):
        await registrar_nova_versao("tuss_procedimento", "", "url", "hash")
    with pytest.raises(VersaoDatasetInvalidaError):
        await registrar_nova_versao("tuss_procedimento", "v1", "", "hash")


@pytest.mark.asyncio
async def test_carregar_arquivo_versao_vigente_tuss_remove_antiga(tmp_path: Path) -> None:
    arquivo_v1 = tmp_path / "tuss_v1.csv"
    arquivo_v2 = tmp_path / "tuss_v2.csv"
    arquivo_v1.write_text(
        "codigo_tuss;descricao;grupo;subgrupo;capitulo\n"
        "101010;Consulta;CONSULTAS;ATENDIMENTO;AMBULATORIAL\n"
        "202020;Exame;EXAMES;DIAGNOSTICO;DIAGNOSTICO\n",
        encoding="utf-8",
    )
    arquivo_v2.write_text(
        "codigo_tuss;descricao;grupo;subgrupo;capitulo\n"
        "303030;Terapia;TERAPIAS;REABILITACAO;TERAPEUTICO\n"
        "404040;Cirurgia;CIRURGIAS;PROCEDIMENTO;HOSPITALAR\n",
        encoding="utf-8",
    )

    async with SessionLocal() as session:
        transacao = await session.begin()
        try:
            resultado_v1 = await carregar_arquivo_versao_vigente(
                "tuss_procedimento",
                arquivo_v1,
                versao="teste_2026_01",
                url_fonte="https://www.gov.br/ans/teste/tuss_v1.csv",
                conn=session,
            )
            resultado_v2 = await carregar_arquivo_versao_vigente(
                "tuss_procedimento",
                arquivo_v2,
                versao="teste_2026_02",
                url_fonte="https://www.gov.br/ans/teste/tuss_v2.csv",
                conn=session,
            )

            total_versoes_raw = await session.scalar(
                text("select count(distinct versao_dataset) from bruto_ans.tuss_procedimento")
            )
            total_linhas_raw = await session.scalar(
                text("select count(*) from bruto_ans.tuss_procedimento")
            )
            vigente = await obter_versao_vigente("tuss_procedimento", session)

            assert resultado_v1.status_manifesto == "nova_versao"
            assert resultado_v1.linhas_carregadas == 2
            assert resultado_v2.status_manifesto == "nova_versao"
            assert resultado_v2.linhas_carregadas == 2
            assert resultado_v2.linhas_removidas == 2
            assert total_versoes_raw == 1
            assert total_linhas_raw == 2
            assert vigente is not None
            assert vigente.versao == "teste_2026_02"
        finally:
            await transacao.rollback()


@pytest.mark.asyncio
async def test_carregar_snapshot_prestador_preserva_snapshot_anterior(tmp_path: Path) -> None:
    arquivo_v1 = tmp_path / "prestador_v1.csv"
    arquivo_v2 = tmp_path / "prestador_v2.csv"
    arquivo_v1.write_text(
        "codigo_prestador;cnpj;razao_social;sg_uf;cd_municipio\n"
        "P001;11111111000191;Prestador Antigo;SP;3550308\n",
        encoding="utf-8",
    )
    arquivo_v2.write_text(
        "codigo_prestador;cnpj;razao_social;sg_uf;cd_municipio\n"
        "P002;22222222000191;Prestador Novo;RJ;3304557\n",
        encoding="utf-8",
    )

    async with SessionLocal() as session:
        transacao = await session.begin()
        try:
            await carregar_arquivo_versao_vigente(
                "prestador_cadastral",
                arquivo_v1,
                versao="prestador_2026_01",
                url_fonte="https://www.gov.br/ans/teste/prestador_v1.csv",
                conn=session,
            )
            resultado_v2 = await carregar_arquivo_versao_vigente(
                "prestador_cadastral",
                arquivo_v2,
                versao="prestador_2026_02",
                url_fonte="https://www.gov.br/ans/teste/prestador_v2.csv",
                conn=session,
            )

            atual = await session.scalar(text("select count(*) from bruto_ans.prestador_cadastral"))
            anterior = await session.scalar(
                text("select count(*) from bruto_ans.prestador_cadastral_snapshot_anterior")
            )
            versoes_atual = await session.scalar(
                text(
                    """
                    select count(distinct versao_dataset)
                    from bruto_ans.prestador_cadastral
                    """
                )
            )

            assert resultado_v2.linhas_carregadas == 1
            assert atual == 1
            assert anterior == 1
            assert versoes_atual == 1
        finally:
            await transacao.rollback()
