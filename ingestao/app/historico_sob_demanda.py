from __future__ import annotations

import asyncio
import os
from contextlib import asynccontextmanager
from dataclasses import dataclass

import structlog
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ingestao.app.carregar_postgres import SessionLocal

logger = structlog.get_logger(__name__)


@dataclass(frozen=True, slots=True)
class ResultadoHistoricoSobDemanda:
    solicitacao_id: int | None
    status: str
    dataset_codigo: str | None = None
    mensagem: str | None = None
    dry_run: bool = False


def _dry_run_habilitado() -> bool:
    return os.getenv("HISTORICO_SOB_DEMANDA_DRY_RUN", "false").strip().lower() in {
        "1",
        "true",
        "sim",
        "yes",
    }


def _anos_na_faixa(competencia_inicio: int, competencia_fim: int) -> range:
    return range(competencia_inicio // 100, competencia_fim // 100 + 1)


@asynccontextmanager
async def _transacao_opcional(session: AsyncSession, deve_abrir: bool):
    if deve_abrir:
        async with session.begin():
            yield
        return
    yield


async def _marcar_erro(session: AsyncSession, solicitacao_id: int, mensagem: str) -> None:
    await session.execute(
        text(
            """
            update plataforma.solicitacao_historico
               set status = 'erro',
                   erro = :mensagem,
                   finalizado_em = now()
             where id = :solicitacao_id
            """
        ),
        {"solicitacao_id": solicitacao_id, "mensagem": mensagem[:2000]},
    )


async def processar_proxima_solicitacao_historico(
    *,
    dry_run: bool | None = None,
    conn: AsyncSession | None = None,
) -> ResultadoHistoricoSobDemanda:
    dry_run_ativo = _dry_run_habilitado() if dry_run is None else dry_run
    session = conn or SessionLocal()
    fechar = conn is None
    try:
        async with _transacao_opcional(session, fechar):
            result = await session.execute(
                text(
                    """
                    select
                        id,
                        cliente_id::text as cliente_id,
                        dataset_codigo,
                        competencia_inicio,
                        competencia_fim
                    from plataforma.solicitacao_historico
                    where status = 'aprovada'
                    order by aprovado_em asc nulls last, solicitado_em asc
                    limit 1
                    for update skip locked
                    """
                )
            )
            solicitacao = result.mappings().one_or_none()
            if solicitacao is None:
                return ResultadoHistoricoSobDemanda(
                    solicitacao_id=None,
                    status="sem_solicitacao",
                    dry_run=dry_run_ativo,
                )

            solicitacao_id = int(solicitacao["id"])
            dataset_codigo = str(solicitacao["dataset_codigo"])
            await session.execute(
                text(
                    """
                    update plataforma.solicitacao_historico
                       set status = 'em_execucao',
                           iniciado_em = now(),
                           erro = null
                     where id = :solicitacao_id
                    """
                ),
                {"solicitacao_id": solicitacao_id},
            )

            politica_result = await session.execute(
                text(
                    """
                    select
                        classe_dataset,
                        historico_sob_demanda,
                        schema_destino,
                        tabela_destino
                    from plataforma.politica_dataset
                    where dataset_codigo = :dataset_codigo
                      and ativo is true
                    """
                ),
                {"dataset_codigo": dataset_codigo},
            )
            politica = politica_result.mappings().one_or_none()
            if politica is None:
                mensagem = f"Dataset {dataset_codigo} sem politica ativa."
                await _marcar_erro(session, solicitacao_id, mensagem)
                return ResultadoHistoricoSobDemanda(
                    solicitacao_id=solicitacao_id,
                    dataset_codigo=dataset_codigo,
                    status="erro",
                    mensagem=mensagem,
                    dry_run=dry_run_ativo,
                )
            if politica["classe_dataset"] != "grande_temporal" and not bool(
                politica["historico_sob_demanda"]
            ):
                mensagem = f"Dataset {dataset_codigo} nao permite historico sob demanda."
                await _marcar_erro(session, solicitacao_id, mensagem)
                return ResultadoHistoricoSobDemanda(
                    solicitacao_id=solicitacao_id,
                    dataset_codigo=dataset_codigo,
                    status="erro",
                    mensagem=mensagem,
                    dry_run=dry_run_ativo,
                )
            if not politica["schema_destino"] or not politica["tabela_destino"]:
                mensagem = f"Dataset {dataset_codigo} sem destino fisico para particionamento."
                await _marcar_erro(session, solicitacao_id, mensagem)
                return ResultadoHistoricoSobDemanda(
                    solicitacao_id=solicitacao_id,
                    dataset_codigo=dataset_codigo,
                    status="erro",
                    mensagem=mensagem,
                    dry_run=dry_run_ativo,
                )

            for ano in _anos_na_faixa(
                int(solicitacao["competencia_inicio"]),
                int(solicitacao["competencia_fim"]),
            ):
                await session.execute(
                    text(
                        """
                        select plataforma.criar_particao_anual_competencia(
                            :schema_destino,
                            :tabela_destino,
                            :ano
                        )
                        """
                    ),
                    {
                        "schema_destino": politica["schema_destino"],
                        "tabela_destino": politica["tabela_destino"],
                        "ano": ano,
                    },
                )

            motivo = f"historico_solicitacao={solicitacao_id}; dry_run={str(dry_run_ativo).lower()}"
            await session.execute(
                text(
                    """
                    insert into plataforma.ingestao_janela_decisao (
                        dataset_codigo,
                        competencia,
                        acao,
                        motivo,
                        janela_minima,
                        janela_maxima_exclusiva
                    ) values (
                        :dataset_codigo,
                        :competencia,
                        'carregado',
                        :motivo,
                        :competencia_inicio,
                        :competencia_fim
                    )
                    """
                ),
                {
                    "dataset_codigo": dataset_codigo,
                    "competencia": int(solicitacao["competencia_inicio"]),
                    "motivo": motivo,
                    "competencia_inicio": int(solicitacao["competencia_inicio"]),
                    "competencia_fim": int(solicitacao["competencia_fim"]),
                },
            )

            if not dry_run_ativo:
                mensagem = (
                    "Extractor historico real nao configurado neste clone; "
                    "use HISTORICO_SOB_DEMANDA_DRY_RUN=true em smoke/local."
                )
                await _marcar_erro(session, solicitacao_id, mensagem)
                return ResultadoHistoricoSobDemanda(
                    solicitacao_id=solicitacao_id,
                    dataset_codigo=dataset_codigo,
                    status="erro",
                    mensagem=mensagem,
                    dry_run=False,
                )

            await session.execute(
                text(
                    """
                    update plataforma.solicitacao_historico
                       set status = 'concluida',
                           finalizado_em = now(),
                           erro = null
                     where id = :solicitacao_id
                    """
                ),
                {"solicitacao_id": solicitacao_id},
            )
            logger.info(
                "historico_sob_demanda_concluido",
                solicitacao_id=solicitacao_id,
                dataset_codigo=dataset_codigo,
                dry_run=dry_run_ativo,
            )
            return ResultadoHistoricoSobDemanda(
                solicitacao_id=solicitacao_id,
                dataset_codigo=dataset_codigo,
                status="concluida",
                dry_run=dry_run_ativo,
            )
    finally:
        if fechar:
            await session.close()


def processar_proxima_solicitacao_historico_sync() -> dict:
    resultado = asyncio.run(processar_proxima_solicitacao_historico())
    return {
        "solicitacao_id": resultado.solicitacao_id,
        "dataset_codigo": resultado.dataset_codigo,
        "status": resultado.status,
        "mensagem": resultado.mensagem,
        "dry_run": resultado.dry_run,
    }
