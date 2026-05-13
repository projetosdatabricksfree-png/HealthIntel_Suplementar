"""Sprint 43 — auditoria granular de tentativa de carga ANS.

Cada execução de task Airflow (discovery, download, parse, carga, dbt) registra
uma tentativa em `plataforma.tentativa_carga_ans`. Inclui também os casos
sem novos arquivos, com fonte indisponível, com layout desconhecido, etc.

A camada complementa (não substitui):
- `plataforma.lote_ingestao` (granularidade de lote / hash de arquivo)
- `plataforma.arquivo_fonte_ans` (granularidade de arquivo)

API pública (async é primária; wrappers sync existem para uso em PythonOperator
síncrono dentro de DAGs):

    tentativa_id = await registrar_inicio_tentativa(
        dominio="tiss",
        dataset_codigo="tiss_ambulatorial",
        dag_id="dag_ingest_tiss",
        task_id="descobrir_fontes",
        run_id="manual__2026-05-13T14:00:00",
    )
    await registrar_evento_tentativa(tentativa_id, status="BAIXADO", motivo="...", linhas_lidas=1000)
    await registrar_final_tentativa(tentativa_id, status_final="CARREGADO", linhas_inseridas=1000)

Shortcuts assíncronos (e síncronos via *_sync):
    registrar_sem_novos_arquivos, registrar_arquivo_ja_carregado,
    registrar_fonte_indisponivel, registrar_layout_nao_mapeado,
    registrar_erro_parse, registrar_erro_carga, registrar_sucesso_carga

Princípios:
- Idempotente em nível de evento; o `tentativa_id` UUID é o que costura.
- Falhas internas de auditoria nunca propagam para a DAG (log no Airflow).
- Os 16 status válidos estão na CHECK constraint
  `tentativa_carga_ans_status_ck` em
  `infra/postgres/init/051_sprint43_tentativa_carga_ans.sql`.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime
from typing import Any, Final
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ingestao.app.carregar_postgres import SessionLocal

logger = logging.getLogger(__name__)

STATUS_VALIDOS: Final[frozenset[str]] = frozenset({
    "INICIADO",
    "SEM_NOVOS_ARQUIVOS",
    "ARQUIVO_JA_CARREGADO",
    "BAIXADO",
    "VALIDADO",
    "CARREGADO",
    "CARREGADO_SEM_LINHAS",
    "CARREGADO_SEM_CHAVE",
    "IGNORADO_DUPLICATA",
    "FONTE_INDISPONIVEL",
    "LAYOUT_NAO_MAPEADO",
    "ERRO_DOWNLOAD",
    "ERRO_PARSE",
    "ERRO_VALIDACAO",
    "ERRO_CARGA",
    "ERRO_DBT",
    "FINALIZADO",
})

STATUS_TERMINAIS_SUCESSO: Final[frozenset[str]] = frozenset({
    "CARREGADO",
    "SEM_NOVOS_ARQUIVOS",
    "ARQUIVO_JA_CARREGADO",
    "IGNORADO_DUPLICATA",
    "FINALIZADO",
})

STATUS_TERMINAIS_NAO_SUCESSO: Final[frozenset[str]] = frozenset({
    "FONTE_INDISPONIVEL",
    "LAYOUT_NAO_MAPEADO",
    "CARREGADO_SEM_LINHAS",
    "CARREGADO_SEM_CHAVE",
    "ERRO_DOWNLOAD",
    "ERRO_PARSE",
    "ERRO_VALIDACAO",
    "ERRO_CARGA",
    "ERRO_DBT",
})


def _validar_status(status: str) -> None:
    if status not in STATUS_VALIDOS:
        raise ValueError(
            f"status inválido para tentativa_carga_ans: {status!r}. "
            f"Válidos: {sorted(STATUS_VALIDOS)}"
        )


async def _executar_sql(
    sql: str,
    params: dict[str, Any],
    *,
    session: AsyncSession | None = None,
) -> Any:
    """Executa SQL de forma idempotente. Falhas viram WARN no log, não Exception."""
    try:
        if session is not None:
            return await session.execute(text(sql), params)
        async with SessionLocal() as s:
            try:
                result = await s.execute(text(sql), params)
                await s.commit()
                return result
            except Exception:
                await s.rollback()
                raise
    except Exception as exc:
        logger.warning(
            "[auditoria_tentativa_carga] falha ao executar SQL: %s — payload=%s",
            exc, params, exc_info=True,
        )
        return None


async def registrar_inicio_tentativa(
    *,
    dominio: str,
    dataset_codigo: str,
    dag_id: str | None = None,
    task_id: str | None = None,
    run_id: str | None = None,
    fonte_url: str | None = None,
    arquivo_nome: str | None = None,
    arquivo_hash: str | None = None,
    competencia: int | None = None,
    tabela_destino: str | None = None,
    motivo: str | None = None,
    session: AsyncSession | None = None,
) -> UUID:
    """Inicia uma tentativa (status='INICIADO') e retorna o tentativa_id."""
    tentativa_id = uuid4()
    sql = """
        insert into plataforma.tentativa_carga_ans (
            tentativa_id, dag_id, task_id, run_id, dominio, dataset_codigo,
            fonte_url, arquivo_nome, arquivo_hash, competencia,
            tabela_destino, status, motivo, iniciado_em
        )
        values (
            :tentativa_id, :dag_id, :task_id, :run_id, :dominio, :dataset_codigo,
            :fonte_url, :arquivo_nome, :arquivo_hash, :competencia,
            :tabela_destino, 'INICIADO', :motivo, now()
        )
    """
    await _executar_sql(sql, {
        "tentativa_id": str(tentativa_id),
        "dag_id": dag_id,
        "task_id": task_id,
        "run_id": run_id,
        "dominio": dominio,
        "dataset_codigo": dataset_codigo,
        "fonte_url": fonte_url,
        "arquivo_nome": arquivo_nome,
        "arquivo_hash": arquivo_hash,
        "competencia": competencia,
        "tabela_destino": tabela_destino,
        "motivo": motivo,
    }, session=session)
    return tentativa_id


async def registrar_evento_tentativa(
    tentativa_id: UUID | str,
    *,
    status: str,
    motivo: str | None = None,
    linhas_lidas: int | None = None,
    linhas_validas: int | None = None,
    linhas_invalidas: int | None = None,
    linhas_inseridas: int | None = None,
    linhas_atualizadas: int | None = None,
    linhas_ignoradas: int | None = None,
    arquivo_hash: str | None = None,
    tabela_destino: str | None = None,
    erro_tipo: str | None = None,
    erro_mensagem: str | None = None,
    lote_ingestao_id: UUID | str | None = None,
    arquivo_fonte_ans_id: UUID | str | None = None,
    session: AsyncSession | None = None,
) -> None:
    """Insere uma nova linha (evento) na tentativa. Múltiplas linhas com mesmo tentativa_id."""
    _validar_status(status)
    sql = """
        insert into plataforma.tentativa_carga_ans (
            tentativa_id, dominio, dataset_codigo, status, motivo,
            linhas_lidas, linhas_validas, linhas_invalidas,
            linhas_inseridas, linhas_atualizadas, linhas_ignoradas,
            arquivo_hash, tabela_destino,
            erro_tipo, erro_mensagem,
            lote_ingestao_id, arquivo_fonte_ans_id,
            dag_id, task_id, run_id,
            iniciado_em
        )
        select
            cast(:tentativa_id as uuid), t.dominio, t.dataset_codigo, :status, :motivo,
            :linhas_lidas, :linhas_validas, :linhas_invalidas,
            :linhas_inseridas, :linhas_atualizadas, :linhas_ignoradas,
            coalesce(:arquivo_hash, t.arquivo_hash),
            coalesce(:tabela_destino, t.tabela_destino),
            :erro_tipo, :erro_mensagem,
            cast(:lote_ingestao_id as uuid), cast(:arquivo_fonte_ans_id as uuid),
            t.dag_id, t.task_id, t.run_id,
            now()
        from plataforma.tentativa_carga_ans t
        where t.tentativa_id = cast(:tentativa_id as uuid)
        order by t.id asc
        limit 1
    """
    await _executar_sql(sql, {
        "tentativa_id": str(tentativa_id),
        "status": status,
        "motivo": motivo,
        "linhas_lidas": linhas_lidas,
        "linhas_validas": linhas_validas,
        "linhas_invalidas": linhas_invalidas,
        "linhas_inseridas": linhas_inseridas,
        "linhas_atualizadas": linhas_atualizadas,
        "linhas_ignoradas": linhas_ignoradas,
        "arquivo_hash": arquivo_hash,
        "tabela_destino": tabela_destino,
        "erro_tipo": erro_tipo,
        "erro_mensagem": erro_mensagem,
        "lote_ingestao_id": str(lote_ingestao_id) if lote_ingestao_id else None,
        "arquivo_fonte_ans_id": str(arquivo_fonte_ans_id) if arquivo_fonte_ans_id else None,
    }, session=session)


async def registrar_final_tentativa(
    tentativa_id: UUID | str,
    *,
    status_final: str,
    duracao_ms: int | None = None,
    session: AsyncSession | None = None,
    **kwargs: Any,
) -> None:
    """Atualiza finalizado_em + duracao_ms na linha mais recente da tentativa
    e adiciona evento final."""
    _validar_status(status_final)
    sql_evento = """
        update plataforma.tentativa_carga_ans
        set finalizado_em = now(),
            duracao_ms = cast(coalesce(:duracao_ms, extract(epoch from (now() - iniciado_em)) * 1000) as bigint)
        where tentativa_id = cast(:tentativa_id as uuid)
          and finalizado_em is null
    """
    await _executar_sql(sql_evento, {
        "tentativa_id": str(tentativa_id),
        "duracao_ms": duracao_ms,
    }, session=session)
    await registrar_evento_tentativa(
        tentativa_id, status=status_final, session=session, **kwargs
    )


# ============================================================================
# Shortcuts (async) — registram em 1 chamada (inicio + final)
# ============================================================================

async def registrar_sem_novos_arquivos(
    *, dominio: str, dataset_codigo: str, dag_id: str | None = None,
    task_id: str | None = None, run_id: str | None = None,
    motivo: str = "discovery não encontrou arquivos novos",
) -> UUID:
    tentativa_id = await registrar_inicio_tentativa(
        dominio=dominio, dataset_codigo=dataset_codigo,
        dag_id=dag_id, task_id=task_id, run_id=run_id, motivo=motivo,
    )
    await registrar_final_tentativa(tentativa_id, status_final="SEM_NOVOS_ARQUIVOS", motivo=motivo)
    return tentativa_id


async def registrar_arquivo_ja_carregado(
    *, dominio: str, dataset_codigo: str, arquivo_hash: str,
    dag_id: str | None = None, task_id: str | None = None, run_id: str | None = None,
    arquivo_nome: str | None = None,
) -> UUID:
    tentativa_id = await registrar_inicio_tentativa(
        dominio=dominio, dataset_codigo=dataset_codigo,
        dag_id=dag_id, task_id=task_id, run_id=run_id,
        arquivo_hash=arquivo_hash, arquivo_nome=arquivo_nome,
        motivo="hash já presente em lote_ingestao com sucesso",
    )
    await registrar_final_tentativa(
        tentativa_id,
        status_final="ARQUIVO_JA_CARREGADO",
        arquivo_hash=arquivo_hash,
    )
    return tentativa_id


async def registrar_fonte_indisponivel(
    *, dominio: str, dataset_codigo: str, fonte_url: str,
    dag_id: str | None = None, task_id: str | None = None, run_id: str | None = None,
    erro_mensagem: str | None = None,
) -> UUID:
    tentativa_id = await registrar_inicio_tentativa(
        dominio=dominio, dataset_codigo=dataset_codigo,
        dag_id=dag_id, task_id=task_id, run_id=run_id, fonte_url=fonte_url,
        motivo="fonte ANS inacessível",
    )
    await registrar_final_tentativa(
        tentativa_id,
        status_final="FONTE_INDISPONIVEL",
        erro_tipo="HTTP",
        erro_mensagem=erro_mensagem,
    )
    return tentativa_id


async def registrar_layout_nao_mapeado(
    *, dominio: str, dataset_codigo: str, arquivo_nome: str, assinatura: str,
    dag_id: str | None = None, task_id: str | None = None, run_id: str | None = None,
    rascunho_id: str | None = None,
) -> UUID:
    motivo = f"assinatura desconhecida={assinatura}"
    if rascunho_id:
        motivo += f"; rascunho criado: {rascunho_id}"
    tentativa_id = await registrar_inicio_tentativa(
        dominio=dominio, dataset_codigo=dataset_codigo,
        dag_id=dag_id, task_id=task_id, run_id=run_id,
        arquivo_nome=arquivo_nome, motivo=motivo,
    )
    await registrar_final_tentativa(
        tentativa_id,
        status_final="LAYOUT_NAO_MAPEADO",
        erro_tipo="LAYOUT",
        erro_mensagem=motivo,
    )
    return tentativa_id


async def registrar_erro_parse(
    *, dominio: str, dataset_codigo: str, arquivo_nome: str,
    erro_mensagem: str, dag_id: str | None = None, task_id: str | None = None,
    run_id: str | None = None, linhas_lidas: int | None = None,
) -> UUID:
    tentativa_id = await registrar_inicio_tentativa(
        dominio=dominio, dataset_codigo=dataset_codigo,
        dag_id=dag_id, task_id=task_id, run_id=run_id,
        arquivo_nome=arquivo_nome,
    )
    await registrar_final_tentativa(
        tentativa_id,
        status_final="ERRO_PARSE",
        erro_tipo="PARSE",
        erro_mensagem=erro_mensagem,
        linhas_lidas=linhas_lidas,
    )
    return tentativa_id


async def registrar_erro_carga(
    *, dominio: str, dataset_codigo: str, tabela_destino: str,
    erro_mensagem: str, dag_id: str | None = None, task_id: str | None = None,
    run_id: str | None = None, arquivo_hash: str | None = None,
    lote_ingestao_id: UUID | str | None = None,
) -> UUID:
    tentativa_id = await registrar_inicio_tentativa(
        dominio=dominio, dataset_codigo=dataset_codigo,
        dag_id=dag_id, task_id=task_id, run_id=run_id,
        tabela_destino=tabela_destino, arquivo_hash=arquivo_hash,
    )
    await registrar_final_tentativa(
        tentativa_id,
        status_final="ERRO_CARGA",
        erro_tipo="CARGA",
        erro_mensagem=erro_mensagem,
        tabela_destino=tabela_destino,
        lote_ingestao_id=lote_ingestao_id,
    )
    return tentativa_id


async def registrar_sucesso_carga(
    *, dominio: str, dataset_codigo: str, tabela_destino: str,
    linhas_inseridas: int, dag_id: str | None = None, task_id: str | None = None,
    run_id: str | None = None, arquivo_hash: str | None = None,
    linhas_lidas: int | None = None, linhas_validas: int | None = None,
    linhas_invalidas: int | None = None,
    lote_ingestao_id: UUID | str | None = None,
    arquivo_fonte_ans_id: UUID | str | None = None,
) -> UUID:
    tentativa_id = await registrar_inicio_tentativa(
        dominio=dominio, dataset_codigo=dataset_codigo,
        dag_id=dag_id, task_id=task_id, run_id=run_id,
        tabela_destino=tabela_destino, arquivo_hash=arquivo_hash,
    )
    status_final = "CARREGADO" if linhas_inseridas > 0 else "CARREGADO_SEM_LINHAS"
    await registrar_final_tentativa(
        tentativa_id,
        status_final=status_final,
        linhas_lidas=linhas_lidas,
        linhas_validas=linhas_validas,
        linhas_invalidas=linhas_invalidas,
        linhas_inseridas=linhas_inseridas,
        tabela_destino=tabela_destino,
        lote_ingestao_id=lote_ingestao_id,
        arquivo_fonte_ans_id=arquivo_fonte_ans_id,
    )
    return tentativa_id


# ============================================================================
# Wrappers síncronos para uso em PythonOperator (Airflow)
# ============================================================================

def _run_sync(coro: Any) -> Any:
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            return asyncio.run_coroutine_threadsafe(coro, loop).result()
    except RuntimeError:
        pass
    return asyncio.run(coro)


def registrar_inicio_tentativa_sync(**kwargs: Any) -> UUID:
    return _run_sync(registrar_inicio_tentativa(**kwargs))


def registrar_evento_tentativa_sync(*args: Any, **kwargs: Any) -> None:
    _run_sync(registrar_evento_tentativa(*args, **kwargs))


def registrar_final_tentativa_sync(*args: Any, **kwargs: Any) -> None:
    _run_sync(registrar_final_tentativa(*args, **kwargs))


def registrar_sem_novos_arquivos_sync(**kwargs: Any) -> UUID:
    return _run_sync(registrar_sem_novos_arquivos(**kwargs))


def registrar_arquivo_ja_carregado_sync(**kwargs: Any) -> UUID:
    return _run_sync(registrar_arquivo_ja_carregado(**kwargs))


def registrar_fonte_indisponivel_sync(**kwargs: Any) -> UUID:
    return _run_sync(registrar_fonte_indisponivel(**kwargs))


def registrar_layout_nao_mapeado_sync(**kwargs: Any) -> UUID:
    return _run_sync(registrar_layout_nao_mapeado(**kwargs))


def registrar_erro_parse_sync(**kwargs: Any) -> UUID:
    return _run_sync(registrar_erro_parse(**kwargs))


def registrar_erro_carga_sync(**kwargs: Any) -> UUID:
    return _run_sync(registrar_erro_carga(**kwargs))


def registrar_sucesso_carga_sync(**kwargs: Any) -> UUID:
    return _run_sync(registrar_sucesso_carga(**kwargs))
