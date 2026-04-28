from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Literal
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from api.app.core.database import SessionLocal

LIMITE_HISTORICO_PADRAO = 1000


@dataclass(frozen=True, slots=True)
class EntitlementHistorico:
    cliente_id: str
    dataset_codigo: str
    acesso_historico: bool
    competencia_inicio: int | None
    competencia_fim: int | None
    permite_exportacao: bool
    limite_requisicao_mensal: int | None
    ativo: bool


class EntitlementHistoricoAusenteError(Exception):
    pass


class CompetenciaHistoricaNaoAutorizadaError(Exception):
    pass


class ExportacaoHistoricaNaoPermitidaError(Exception):
    pass


class PaginacaoHistoricaInvalidaError(Exception):
    pass


def _normalizar_cliente_id(cliente_id: str | UUID | int) -> str:
    return str(cliente_id)


async def _with_session(conn: AsyncSession | None):
    if conn is not None:
        return conn, False
    return SessionLocal(), True


async def consultar_entitlement(
    cliente_id: str | UUID | int,
    dataset_codigo: str,
    conn: AsyncSession | None = None,
) -> EntitlementHistorico | None:
    session, deve_fechar = await _with_session(conn)
    try:
        result = await session.execute(
            text(
                """
                select
                    cliente_id::text as cliente_id,
                    dataset_codigo,
                    acesso_historico,
                    competencia_inicio,
                    competencia_fim,
                    permite_exportacao,
                    limite_requisicao_mensal,
                    ativo
                from plataforma.cliente_dataset_acesso
                where cliente_id = cast(:cliente_id as uuid)
                  and dataset_codigo = :dataset_codigo
                  and ativo is true
                order by atualizado_em desc
                limit 1
                """
            ),
            {
                "cliente_id": _normalizar_cliente_id(cliente_id),
                "dataset_codigo": dataset_codigo,
            },
        )
        row = result.mappings().one_or_none()
        if row is None:
            return None
        return EntitlementHistorico(
            cliente_id=str(row["cliente_id"]),
            dataset_codigo=str(row["dataset_codigo"]),
            acesso_historico=bool(row["acesso_historico"]),
            competencia_inicio=(
                int(row["competencia_inicio"]) if row["competencia_inicio"] is not None else None
            ),
            competencia_fim=(
                int(row["competencia_fim"]) if row["competencia_fim"] is not None else None
            ),
            permite_exportacao=bool(row["permite_exportacao"]),
            limite_requisicao_mensal=(
                int(row["limite_requisicao_mensal"])
                if row["limite_requisicao_mensal"] is not None
                else None
            ),
            ativo=bool(row["ativo"]),
        )
    finally:
        if deve_fechar:
            await session.close()


async def competencia_na_janela_hot(
    dataset_codigo: str,
    competencia: int,
    conn: AsyncSession | None = None,
) -> bool:
    session, deve_fechar = await _with_session(conn)
    try:
        politica_result = await session.execute(
            text(
                """
                select
                    classe_dataset,
                    estrategia_carga,
                    coalesce(anos_carga_hot, 2) as anos_carga_hot
                from plataforma.politica_dataset
                where dataset_codigo = :dataset_codigo
                  and ativo is true
                """
            ),
            {"dataset_codigo": dataset_codigo},
        )
        politica = politica_result.mappings().one_or_none()
        if politica is None:
            raise CompetenciaHistoricaNaoAutorizadaError(
                f"Dataset {dataset_codigo} nao possui politica ativa."
            )
        temporal = (
            politica["classe_dataset"] == "grande_temporal"
            or politica["estrategia_carga"] == "ano_vigente_mais_ano_anterior"
        )
        if not temporal:
            return True
        janela_result = await session.execute(
            text(
                """
                select competencia_minima, competencia_maxima_exclusiva
                from plataforma.calcular_janela_carga_anual(:anos_carga)
                """
            ),
            {"anos_carga": int(politica["anos_carga_hot"])},
        )
        janela = janela_result.mappings().one()
        return (
            int(janela["competencia_minima"])
            <= int(competencia)
            < int(janela["competencia_maxima_exclusiva"])
        )
    finally:
        if deve_fechar:
            await session.close()


async def validar_acesso_competencia(
    cliente_id: str | UUID | int,
    dataset_codigo: str,
    competencia: int,
    conn: AsyncSession | None = None,
) -> bool:
    if await competencia_na_janela_hot(dataset_codigo, competencia, conn):
        return True

    entitlement = await consultar_entitlement(cliente_id, dataset_codigo, conn)
    if entitlement is None:
        raise EntitlementHistoricoAusenteError(
            "Cliente nao possui entitlement ativo para historico deste dataset."
        )
    if not entitlement.acesso_historico:
        raise CompetenciaHistoricaNaoAutorizadaError(
            "Entitlement ativo nao habilita acesso historico."
        )
    if entitlement.competencia_inicio is None or entitlement.competencia_fim is None:
        raise CompetenciaHistoricaNaoAutorizadaError("Entitlement historico sem faixa valida.")
    if not entitlement.competencia_inicio <= int(competencia) <= entitlement.competencia_fim:
        raise CompetenciaHistoricaNaoAutorizadaError(
            "Competencia historica fora da faixa contratada."
        )
    return True


def validar_paginacao_historica(
    limite: int,
    *,
    permite_exportacao: bool = False,
    modo: Literal["pagina", "csv_completo"] = "pagina",
) -> None:
    if limite < 1 or limite > LIMITE_HISTORICO_PADRAO:
        raise PaginacaoHistoricaInvalidaError(
            f"Rotas historicas exigem paginacao entre 1 e {LIMITE_HISTORICO_PADRAO}."
        )
    if modo == "csv_completo":
        raise ExportacaoHistoricaNaoPermitidaError(
            "Exportacao historica completa e pos-MVP e permanece bloqueada."
        )
    if not permite_exportacao and modo != "pagina":
        raise ExportacaoHistoricaNaoPermitidaError(
            "Cliente nao possui permissao de exportacao historica."
        )


async def obter_historico_solicitacao_aprovada(
    conn: AsyncSession | None = None,
) -> dict | None:
    session, deve_fechar = await _with_session(conn)
    try:
        result = await session.execute(
            text(
                """
                select
                    id,
                    cliente_id::text as cliente_id,
                    dataset_codigo,
                    competencia_inicio,
                    competencia_fim,
                    status,
                    motivo
                from plataforma.solicitacao_historico
                where status = 'aprovada'
                order by aprovado_em asc nulls last, solicitado_em asc
                limit 1
                for update skip locked
                """
            )
        )
        row = result.mappings().one_or_none()
        return dict(row) if row else None
    finally:
        if deve_fechar:
            await session.close()


async def aprovar_solicitacao_via_operacao(
    solicitacao_id: int,
    aprovado_por: str = "runbook",
    conn: AsyncSession | None = None,
) -> None:
    session, deve_fechar = await _with_session(conn)
    try:
        async with _transacao_opcional(session, deve_fechar):
            result = await session.execute(
                text(
                    """
                    update plataforma.solicitacao_historico
                       set status = 'aprovada',
                           aprovado_em = coalesce(aprovado_em, now()),
                           motivo = coalesce(motivo, :motivo)
                     where id = :solicitacao_id
                       and status in ('pendente', 'aprovada')
                    returning
                        cliente_id::text as cliente_id,
                        dataset_codigo,
                        competencia_inicio,
                        competencia_fim
                    """
                ),
                {
                    "solicitacao_id": solicitacao_id,
                    "motivo": f"aprovado_por={aprovado_por}",
                },
            )
            solicitacao = result.mappings().one_or_none()
            if solicitacao is None:
                raise CompetenciaHistoricaNaoAutorizadaError(
                    f"Solicitacao {solicitacao_id} inexistente ou nao aprovavel."
                )
            await session.execute(
                text(
                    """
                    update plataforma.cliente_dataset_acesso
                       set ativo = false
                     where cliente_id = cast(:cliente_id as uuid)
                       and dataset_codigo = :dataset_codigo
                       and ativo is true
                    """
                ),
                {
                    "cliente_id": solicitacao["cliente_id"],
                    "dataset_codigo": solicitacao["dataset_codigo"],
                },
            )
            await session.execute(
                text(
                    """
                    insert into plataforma.cliente_dataset_acesso (
                        cliente_id,
                        dataset_codigo,
                        plano,
                        acesso_historico,
                        competencia_inicio,
                        competencia_fim,
                        ativo
                    ) values (
                        cast(:cliente_id as uuid),
                        :dataset_codigo,
                        'historico_sob_demanda',
                        true,
                        :competencia_inicio,
                        :competencia_fim,
                        true
                    )
                    """
                ),
                {
                    "cliente_id": solicitacao["cliente_id"],
                    "dataset_codigo": solicitacao["dataset_codigo"],
                    "competencia_inicio": solicitacao["competencia_inicio"],
                    "competencia_fim": solicitacao["competencia_fim"],
                },
            )
        if not deve_fechar:
            await session.flush()
    finally:
        if deve_fechar:
            await session.close()


@asynccontextmanager
async def _transacao_opcional(session: AsyncSession, deve_abrir: bool):
    if deve_abrir:
        async with session.begin():
            yield
        return
    yield
