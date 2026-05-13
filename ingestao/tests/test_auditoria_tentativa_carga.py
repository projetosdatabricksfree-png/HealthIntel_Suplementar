"""Sprint 43 — testes do helper auditoria_tentativa_carga.

Integração: requer Postgres ativo (via docker compose ou CI) e migration 051
aplicada. Os testes inserem registros em plataforma.tentativa_carga_ans com
domínio dedicado `_test_sprint43_audit` para facilitar limpeza.
"""

from __future__ import annotations

import os
import subprocess
from uuid import UUID

import pytest
from sqlalchemy import text

from ingestao.app.auditoria_tentativa_carga import (
    STATUS_VALIDOS,
    registrar_arquivo_ja_carregado,
    registrar_erro_carga,
    registrar_erro_parse,
    registrar_evento_tentativa,
    registrar_final_tentativa,
    registrar_fonte_indisponivel,
    registrar_inicio_tentativa,
    registrar_layout_nao_mapeado,
    registrar_sem_novos_arquivos,
    registrar_sucesso_carga,
)
from ingestao.app.carregar_postgres import SessionLocal

DOMINIO_TESTE = "_test_sprint43_audit"

# Compartilha event loop e connection pool por módulo — evita conflito asyncpg
# "Task ... got Future ... attached to a different loop" entre tests assíncronos.
pytestmark = pytest.mark.asyncio(loop_scope="module")


def _psql_sync(sql: str) -> None:
    """Executa SQL via subprocess (psql direto ou docker compose). Sync — não toca
    o event loop do asyncpg, evitando ruído de teardown."""
    if os.getenv("POSTGRES_HOST"):
        cmd = [
            "psql",
            "-h", os.getenv("POSTGRES_HOST", "localhost"),
            "-p", os.getenv("POSTGRES_PORT", "5432"),
            "-U", os.getenv("POSTGRES_USER", "healthintel"),
            "-d", os.getenv("POSTGRES_DB", "healthintel"),
            "-v", "ON_ERROR_STOP=1", "-c", sql,
        ]
        env = {**os.environ, "PGPASSWORD": os.getenv("POSTGRES_PASSWORD", "healthintel")}
        subprocess.run(cmd, env=env, check=True, capture_output=True)
    else:
        subprocess.run([
            "docker", "compose", "-f", "infra/docker-compose.yml",
            "exec", "-T", "postgres",
            "psql", "-U", "healthintel", "-d", "healthintel",
            "-v", "ON_ERROR_STOP=1", "-c", sql,
        ], check=True, capture_output=True)


async def _eventos_da_tentativa(tentativa_id: UUID | str) -> list[dict]:
    async with SessionLocal() as s:
        res = await s.execute(
            text(
                "select status, motivo, linhas_inseridas, linhas_lidas, finalizado_em, duracao_ms "
                "from plataforma.tentativa_carga_ans "
                "where tentativa_id = cast(:t as uuid) order by id asc"
            ),
            {"t": str(tentativa_id)},
        )
        return [dict(row._mapping) for row in res.all()]


@pytest.fixture(autouse=True)
def _limpar_antes_e_depois():
    """Sync fixture: limpa o domínio de teste antes e depois, via subprocess psql.
    Evita conflito de event loops do asyncpg em pytest-asyncio recente."""
    _psql_sync(
        f"delete from plataforma.tentativa_carga_ans where dominio = '{DOMINIO_TESTE}'"
    )
    yield
    _psql_sync(
        f"delete from plataforma.tentativa_carga_ans where dominio = '{DOMINIO_TESTE}'"
    )


async def test_inicio_gera_uuid_e_status_iniciado():
    tid = await registrar_inicio_tentativa(
        dominio=DOMINIO_TESTE, dataset_codigo="ds_inicio",
        dag_id="d", task_id="t", run_id="r",
    )
    assert isinstance(tid, UUID)
    eventos = await _eventos_da_tentativa(tid)
    assert len(eventos) == 1
    assert eventos[0]["status"] == "INICIADO"


async def test_evento_adiciona_segunda_linha_e_status_intermediario():
    tid = await registrar_inicio_tentativa(
        dominio=DOMINIO_TESTE, dataset_codigo="ds_evento",
    )
    await registrar_evento_tentativa(tid, status="BAIXADO", motivo="ok", linhas_lidas=10)
    eventos = await _eventos_da_tentativa(tid)
    assert [e["status"] for e in eventos] == ["INICIADO", "BAIXADO"]
    assert eventos[1]["linhas_lidas"] == 10


async def test_final_preenche_finalizado_em_e_duracao():
    tid = await registrar_inicio_tentativa(
        dominio=DOMINIO_TESTE, dataset_codigo="ds_final",
    )
    await registrar_final_tentativa(tid, status_final="CARREGADO", linhas_inseridas=42)
    eventos = await _eventos_da_tentativa(tid)
    # 2 linhas: INICIADO + CARREGADO; a INICIADO ganha finalizado_em via UPDATE
    assert len(eventos) == 2
    inicio = eventos[0]
    final = eventos[1]
    assert final["status"] == "CARREGADO"
    assert final["linhas_inseridas"] == 42
    assert inicio["finalizado_em"] is not None
    assert inicio["duracao_ms"] is not None and inicio["duracao_ms"] >= 0


async def test_status_invalido_levanta():
    tid = await registrar_inicio_tentativa(
        dominio=DOMINIO_TESTE, dataset_codigo="ds_invalido",
    )
    with pytest.raises(ValueError):
        await registrar_evento_tentativa(tid, status="STATUS_INVENTADO")


async def test_shortcut_sem_novos_arquivos():
    tid = await registrar_sem_novos_arquivos(
        dominio=DOMINIO_TESTE, dataset_codigo="ds_sem_novos",
        dag_id="dag_x", task_id="discovery", run_id="run_1",
    )
    eventos = await _eventos_da_tentativa(tid)
    statuses = [e["status"] for e in eventos]
    assert "INICIADO" in statuses
    assert "SEM_NOVOS_ARQUIVOS" in statuses


async def test_shortcut_arquivo_ja_carregado():
    tid = await registrar_arquivo_ja_carregado(
        dominio=DOMINIO_TESTE, dataset_codigo="ds_dup",
        arquivo_hash="deadbeef" * 8, arquivo_nome="x.csv",
    )
    eventos = await _eventos_da_tentativa(tid)
    assert "ARQUIVO_JA_CARREGADO" in [e["status"] for e in eventos]


async def test_shortcut_fonte_indisponivel():
    tid = await registrar_fonte_indisponivel(
        dominio=DOMINIO_TESTE, dataset_codigo="ds_fonte",
        fonte_url="https://ans.example/x.csv",
        erro_mensagem="HTTP 503",
    )
    eventos = await _eventos_da_tentativa(tid)
    assert "FONTE_INDISPONIVEL" in [e["status"] for e in eventos]


async def test_shortcut_layout_nao_mapeado():
    tid = await registrar_layout_nao_mapeado(
        dominio=DOMINIO_TESTE, dataset_codigo="ds_layout",
        arquivo_nome="novo.csv", assinatura="sha256:abc",
        rascunho_id="rasc_001",
    )
    eventos = await _eventos_da_tentativa(tid)
    assert "LAYOUT_NAO_MAPEADO" in [e["status"] for e in eventos]


async def test_shortcut_erro_parse_e_erro_carga():
    t1 = await registrar_erro_parse(
        dominio=DOMINIO_TESTE, dataset_codigo="ds_parse",
        arquivo_nome="x.csv", erro_mensagem="UnicodeDecodeError",
    )
    t2 = await registrar_erro_carga(
        dominio=DOMINIO_TESTE, dataset_codigo="ds_carga",
        tabela_destino="bruto_ans.x", erro_mensagem="not null violation",
    )
    e1 = await _eventos_da_tentativa(t1)
    e2 = await _eventos_da_tentativa(t2)
    assert "ERRO_PARSE" in [e["status"] for e in e1]
    assert "ERRO_CARGA" in [e["status"] for e in e2]


async def test_shortcut_sucesso_carga_com_linhas_e_sem_linhas():
    t_ok = await registrar_sucesso_carga(
        dominio=DOMINIO_TESTE, dataset_codigo="ds_ok",
        tabela_destino="bruto_ans.x", linhas_inseridas=100,
    )
    t_zero = await registrar_sucesso_carga(
        dominio=DOMINIO_TESTE, dataset_codigo="ds_zero",
        tabela_destino="bruto_ans.x", linhas_inseridas=0,
    )
    e_ok = await _eventos_da_tentativa(t_ok)
    e_zero = await _eventos_da_tentativa(t_zero)
    assert "CARREGADO" in [e["status"] for e in e_ok]
    assert "CARREGADO_SEM_LINHAS" in [e["status"] for e in e_zero]


def test_status_validos_cobre_constraint_db():
    # Garante que a lista local bate com a CHECK constraint do migration 051
    esperados = {
        "INICIADO", "SEM_NOVOS_ARQUIVOS", "ARQUIVO_JA_CARREGADO", "BAIXADO",
        "VALIDADO", "CARREGADO", "CARREGADO_SEM_LINHAS", "CARREGADO_SEM_CHAVE",
        "IGNORADO_DUPLICATA", "FONTE_INDISPONIVEL", "LAYOUT_NAO_MAPEADO",
        "ERRO_DOWNLOAD", "ERRO_PARSE", "ERRO_VALIDACAO", "ERRO_CARGA",
        "ERRO_DBT", "FINALIZADO",
    }
    assert STATUS_VALIDOS == frozenset(esperados)
