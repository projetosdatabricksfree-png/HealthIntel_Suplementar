from __future__ import annotations

import importlib
import importlib.util
import subprocess
from pathlib import Path

import pytest
from sqlalchemy import text

from ingestao.app.carregar_postgres import SessionLocal
from ingestao.app.historico_sob_demanda import processar_proxima_solicitacao_historico

ROOT = Path(__file__).resolve().parents[2]
PSQL = (
    "docker",
    "compose",
    "-f",
    "infra/docker-compose.yml",
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
)

CLIENTE_HISTORICO = "90000000-0000-0000-0000-000000000038"


@pytest.fixture(scope="module", autouse=True)
def _aplicar_bootstraps_historico() -> None:
    for arquivo in (
        "030_fase7_particionamento_anual.sql",
        "031_fase7_janela_carga.sql",
        "033_fase7_historico_sob_demanda.sql",
    ):
        subprocess.run(
            PSQL,
            input=(ROOT / f"infra/postgres/init/{arquivo}").read_text(),
            text=True,
            cwd=ROOT,
            check=True,
            capture_output=True,
        )


@pytest.fixture(autouse=True)
async def _descartar_engine() -> None:
    yield
    from ingestao.app.carregar_postgres import engine

    await engine.dispose()


async def _preparar_cliente(session) -> None:
    await session.execute(
        text(
            """
            insert into plataforma.cliente (
                id,
                nome,
                email,
                status,
                plano_id,
                status_cobranca,
                dia_fechamento
            ) values (
                cast(:cliente_id as uuid),
                'Cliente Historico Teste',
                'cliente-historico-dag@teste.local',
                'ativo',
                '11111111-1111-1111-1111-111111111114',
                'em_dia',
                1
            )
            on conflict (email) do update set status = 'ativo'
            """
        ),
        {"cliente_id": CLIENTE_HISTORICO},
    )


async def _criar_solicitacao(
    session,
    dataset_codigo: str,
    status: str = "aprovada",
    competencia_inicio: int = 202401,
    competencia_fim: int = 202401,
) -> int:
    result = await session.execute(
        text(
            """
            insert into plataforma.solicitacao_historico (
                cliente_id,
                dataset_codigo,
                competencia_inicio,
                competencia_fim,
                status,
                aprovado_em,
                motivo
            ) values (
                cast(:cliente_id as uuid),
                :dataset_codigo,
                :competencia_inicio,
                :competencia_fim,
                :status,
                case when :status = 'aprovada' then now() else null end,
                'teste automatizado'
            )
            returning id
            """
        ),
        {
            "cliente_id": CLIENTE_HISTORICO,
            "dataset_codigo": dataset_codigo,
            "competencia_inicio": competencia_inicio,
            "competencia_fim": competencia_fim,
            "status": status,
        },
    )
    return int(result.scalar_one())


@pytest.mark.asyncio
async def test_parser_import_dag_historico_nao_falha() -> None:
    if importlib.util.find_spec("airflow") is None:
        texto = (ROOT / "ingestao/dags/dag_historico_sob_demanda.py").read_text()
        assert "dag_historico_sob_demanda" in texto
        return

    modulo = importlib.import_module("ingestao.dags.dag_historico_sob_demanda")

    assert modulo.dag.dag_id == "dag_historico_sob_demanda"


@pytest.mark.asyncio
async def test_solicitacao_aprovada_conclui_em_dry_run() -> None:
    async with SessionLocal() as session:
        transacao = await session.begin()
        try:
            await _preparar_cliente(session)
            solicitacao_id = await _criar_solicitacao(session, "sib_operadora")
            resultado = await processar_proxima_solicitacao_historico(
                dry_run=True,
                conn=session,
            )
            status = await session.scalar(
                text("select status from plataforma.solicitacao_historico where id = :id"),
                {"id": solicitacao_id},
            )
            particao = await session.scalar(
                text("select to_regclass('bruto_ans.sib_beneficiario_operadora_2024')::text")
            )
        finally:
            await transacao.rollback()

    assert resultado.status == "concluida"
    assert status == "concluida"
    assert particao == "bruto_ans.sib_beneficiario_operadora_2024"


@pytest.mark.asyncio
async def test_dataset_sem_historico_permitido_vira_erro_controlado() -> None:
    async with SessionLocal() as session:
        transacao = await session.begin()
        try:
            await _preparar_cliente(session)
            await _criar_solicitacao(session, "cadop")
            resultado = await processar_proxima_solicitacao_historico(
                dry_run=True,
                conn=session,
            )
        finally:
            await transacao.rollback()

    assert resultado.status == "erro"
    assert "nao permite historico" in str(resultado.mensagem)


@pytest.mark.asyncio
async def test_solicitacao_concluida_nao_reprocessa() -> None:
    async with SessionLocal() as session:
        transacao = await session.begin()
        try:
            await _preparar_cliente(session)
            await _criar_solicitacao(session, "sib_operadora", status="concluida")
            resultado = await processar_proxima_solicitacao_historico(
                dry_run=True,
                conn=session,
            )
        finally:
            await transacao.rollback()

    assert resultado.status == "sem_solicitacao"


def test_permitir_historico_true_apenas_dag_historico() -> None:
    resultado = subprocess.run(
        (
            "bash",
            "-lc",
            "grep -R \"permitir_historico=True\" -n ingestao/dags ingestao/app scripts || true",
        ),
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    linhas = [linha for linha in resultado.stdout.splitlines() if linha.strip()]

    assert all(
        "dag_historico_sob_demanda.py" in linha
        or "test_dag_historico_sob_demanda.py" in linha
        for linha in linhas
    )
