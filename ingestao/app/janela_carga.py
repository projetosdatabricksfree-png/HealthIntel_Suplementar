from __future__ import annotations

import os
from collections.abc import Iterable
from dataclasses import dataclass

import structlog
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ingestao.app.carregar_postgres import SessionLocal

ACOES_DECISAO = {
    "carregado",
    "ignorado_fora_janela",
    "rejeitado_historico_sem_flag",
    "ignorado_versao_antiga",
}

logger = structlog.get_logger(__name__)


@dataclass(frozen=True, slots=True)
class JanelaCarga:
    dataset_codigo: str
    classe_dataset: str
    estrategia_carga: str
    anos_carga_hot: int
    competencia_minima: int
    competencia_maxima_exclusiva: int
    ano_inicial: int
    ano_final: int
    ano_preparado: int
    schema_destino: str | None
    tabela_destino: str | None
    coluna_competencia: str | None
    particionar_por_ano: bool = False


class PoliticaDatasetNaoEncontradaError(Exception):
    pass


class DatasetNaoTemporalError(Exception):
    pass


class HistoricoForaDaJanelaError(Exception):
    pass


class ConfiguracaoJanelaInvalidaError(Exception):
    pass


def obter_anos_carga_default() -> int:
    valor = os.getenv("ANS_ANOS_CARGA_HOT")
    if valor is None or valor == "":
        return 2
    try:
        anos = int(valor)
    except ValueError as exc:
        raise ConfiguracaoJanelaInvalidaError(
            "ANS_ANOS_CARGA_HOT deve ser um inteiro maior ou igual a 1."
        ) from exc
    if anos < 1:
        raise ConfiguracaoJanelaInvalidaError(
            "ANS_ANOS_CARGA_HOT deve ser maior ou igual a 1."
        )
    return anos


def competencia_dentro_janela(competencia: int, janela: JanelaCarga) -> bool:
    return janela.competencia_minima <= competencia < janela.competencia_maxima_exclusiva


def normalizar_competencia(valor: object) -> int:
    texto = str(valor).strip()
    if not texto:
        raise ValueError("Competencia vazia.")
    if not texto.isdigit():
        raise ValueError(f"Competencia deve estar no formato integer YYYYMM: {valor!r}.")
    competencia = int(texto)
    ano = competencia // 100
    mes = competencia % 100
    if ano < 1 or mes < 1 or mes > 12:
        raise ValueError(f"Competencia invalida: {valor!r}.")
    return competencia


async def obter_janela(
    dataset_codigo: str,
    anos: int | None = None,
    conn: AsyncSession | None = None,
) -> JanelaCarga:
    async def _executar(session: AsyncSession) -> JanelaCarga:
        politica_result = await session.execute(
            text(
                """
                select
                    dataset_codigo,
                    classe_dataset,
                    estrategia_carga,
                    schema_destino,
                    tabela_destino,
                    coluna_competencia,
                    anos_carga_hot,
                    particionar_por_ano
                from plataforma.politica_dataset
                where dataset_codigo = :dataset_codigo
                  and ativo is true
                """
            ),
            {"dataset_codigo": dataset_codigo},
        )
        politica = politica_result.mappings().one_or_none()
        if politica is None:
            raise PoliticaDatasetNaoEncontradaError(
                f"Dataset {dataset_codigo} nao encontrado ou inativo "
                "em plataforma.politica_dataset."
            )
        if (
            politica["classe_dataset"] != "grande_temporal"
            and politica["estrategia_carga"] != "ano_vigente_mais_ano_anterior"
        ):
            raise DatasetNaoTemporalError(
                f"Dataset {dataset_codigo} nao usa janela dinamica de carga temporal."
            )

        anos_carga = politica["anos_carga_hot"] or anos or obter_anos_carga_default()
        if int(anos_carga) < 1:
            raise ConfiguracaoJanelaInvalidaError(
                f"anos_carga_hot invalido para {dataset_codigo}: {anos_carga}."
            )

        janela_result = await session.execute(
            text(
                """
                select
                    ano_inicial,
                    ano_final,
                    ano_preparado,
                    competencia_minima,
                    competencia_maxima_exclusiva
                from plataforma.calcular_janela_carga_anual(:anos_carga)
                """
            ),
            {"anos_carga": int(anos_carga)},
        )
        janela = janela_result.mappings().one()
        return JanelaCarga(
            dataset_codigo=str(politica["dataset_codigo"]),
            classe_dataset=str(politica["classe_dataset"]),
            estrategia_carga=str(politica["estrategia_carga"]),
            anos_carga_hot=int(anos_carga),
            competencia_minima=int(janela["competencia_minima"]),
            competencia_maxima_exclusiva=int(janela["competencia_maxima_exclusiva"]),
            ano_inicial=int(janela["ano_inicial"]),
            ano_final=int(janela["ano_final"]),
            ano_preparado=int(janela["ano_preparado"]),
            schema_destino=politica["schema_destino"],
            tabela_destino=politica["tabela_destino"],
            coluna_competencia=politica["coluna_competencia"],
            particionar_por_ano=bool(politica["particionar_por_ano"]),
        )

    if conn is not None:
        return await _executar(conn)
    async with SessionLocal() as session:
        return await _executar(session)


async def registrar_decisao(
    dataset_codigo: str,
    competencia: int,
    acao: str,
    janela: JanelaCarga | None = None,
    motivo: str | None = None,
    conn: AsyncSession | None = None,
) -> None:
    if acao not in ACOES_DECISAO:
        raise ValueError(f"Acao de decisao de janela invalida: {acao}.")

    logger.info(
        "decisao_janela_carga",
        dataset_codigo=dataset_codigo,
        competencia=competencia,
        acao=acao,
        motivo=motivo,
        janela_minima=janela.competencia_minima if janela else None,
        janela_maxima_exclusiva=janela.competencia_maxima_exclusiva if janela else None,
    )

    async def _executar(session: AsyncSession) -> None:
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
                    :acao,
                    :motivo,
                    :janela_minima,
                    :janela_maxima_exclusiva
                )
                """
            ),
            {
                "dataset_codigo": dataset_codigo,
                "competencia": competencia,
                "acao": acao,
                "motivo": motivo,
                "janela_minima": janela.competencia_minima if janela else None,
                "janela_maxima_exclusiva": (
                    janela.competencia_maxima_exclusiva if janela else None
                ),
            },
        )

    if conn is not None:
        await _executar(conn)
        return
    async with SessionLocal() as session:
        await _executar(session)
        await session.commit()


async def assegurar_dentro_da_janela_ou_falhar(
    competencia: int,
    janela: JanelaCarga,
    *,
    permitir_historico: bool = False,
    registrar: bool = True,
    conn: AsyncSession | None = None,
) -> None:
    if competencia_dentro_janela(competencia, janela):
        return
    motivo = (
        f"Competencia {competencia} fora da janela "
        f"[{janela.competencia_minima}, {janela.competencia_maxima_exclusiva})."
    )
    if permitir_historico:
        logger.info(
            "historico_fora_janela_permitido",
            dataset_codigo=janela.dataset_codigo,
            competencia=competencia,
            acao="historico_fora_janela_permitido",
            motivo=motivo,
            janela_minima=janela.competencia_minima,
            janela_maxima_exclusiva=janela.competencia_maxima_exclusiva,
        )
        return
    if registrar:
        await registrar_decisao(
            janela.dataset_codigo,
            competencia,
            "rejeitado_historico_sem_flag",
            janela,
            motivo,
            conn,
        )
    raise HistoricoForaDaJanelaError(
        f"{motivo} Carga historica exige fluxo dedicado da Sprint 38."
    )


async def filtrar_competencias_janela(
    dataset_codigo: str,
    competencias: Iterable[int],
    conn: AsyncSession | None = None,
) -> tuple[list[int], list[int]]:
    janela = await obter_janela(dataset_codigo, conn=conn)
    dentro: list[int] = []
    fora: list[int] = []
    for competencia in competencias:
        competencia_normalizada = normalizar_competencia(competencia)
        if competencia_dentro_janela(competencia_normalizada, janela):
            dentro.append(competencia_normalizada)
            continue
        fora.append(competencia_normalizada)
        await registrar_decisao(
            dataset_codigo,
            competencia_normalizada,
            "ignorado_fora_janela",
            janela,
            "Arquivo fora da janela dinamica de carga.",
            conn,
        )
    return dentro, fora


async def garantir_particoes_dataset(
    janela: JanelaCarga,
    conn: AsyncSession | None = None,
) -> None:
    if not janela.particionar_por_ano or not janela.schema_destino or not janela.tabela_destino:
        return

    async def _executar(session: AsyncSession) -> None:
        await session.execute(
            text(
                """
                select plataforma.preparar_particoes_janela_atual(
                    :schema_destino,
                    :tabela_destino,
                    :anos_carga_hot
                )
                """
            ),
            {
                "schema_destino": janela.schema_destino,
                "tabela_destino": janela.tabela_destino,
                "anos_carga_hot": janela.anos_carga_hot,
            },
        )

    if conn is not None:
        await _executar(conn)
        return
    async with SessionLocal() as session:
        await _executar(session)
        await session.commit()
