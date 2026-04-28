"""Sprint 37 — Última versão vigente para datasets de referência/cadastro.

Este módulo fornece o controle de manifesto da versão vigente para datasets
classificados como `referencia_versionada` (TUSS, ROL, DE-PARA SIP-TUSS) e
`snapshot_atual` (prestador_cadastral, qualiss). A carga padrão da VPS deve
manter apenas a última versão vigente; histórico antigo é responsabilidade
da Sprint 38 (histórico sob demanda).

Notas operacionais:
- Tabela física: `plataforma.versao_dataset_vigente` (NÃO confundir com
  `plataforma.versao_dataset` do baseline 002, que é log per-carga).
- Política consultada em `plataforma.politica_dataset` (Sprint 34).
- Hash padrão: SHA-256 calculado em chunks.
- Apenas uma vigente por `dataset_codigo` (garantido por unique index parcial).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Literal

import structlog
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ingestao.app.carregar_postgres import SessionLocal

logger = structlog.get_logger(__name__)

ResultadoRegistro = Literal["nova_versao", "nada_a_fazer"]


@dataclass(slots=True)
class VersaoDataset:
    dataset_codigo: str
    versao: str
    url_fonte: str
    hash_arquivo: str
    publicado_em: date | None = None
    carregado_em: datetime | None = None
    arquivo_bytes: int | None = None
    metadados: dict[str, Any] | None = None
    vigente: bool = True
    id: int | None = None


class PoliticaVersaoDatasetNaoEncontradaError(Exception):
    """Dataset não cadastrado em `plataforma.politica_dataset` ou inativo."""


class DatasetNaoVersionadoError(Exception):
    """Dataset não pertence a classe que comporta manifesto de versão vigente."""


class VersaoDatasetInvalidaError(Exception):
    """Parâmetros de versão inválidos para registro."""


class DuasVersoesVigentesError(Exception):
    """Inconsistência: mais de uma linha vigente para o mesmo dataset_codigo."""


_CLASSES_COM_MANIFESTO = ("referencia_versionada", "snapshot_atual")


async def politica_exige_apenas_ultima_versao(
    dataset_codigo: str,
    conn: AsyncSession | None = None,
) -> bool:
    """Retorna `True` quando a política exige carga de apenas a última versão.

    Levanta `PoliticaVersaoDatasetNaoEncontradaError` se o dataset não existir
    ou estiver inativo.
    """

    async def _executar(session: AsyncSession) -> bool:
        resultado = await session.execute(
            text(
                """
                select carregar_apenas_ultima_versao, classe_dataset
                from plataforma.politica_dataset
                where dataset_codigo = :dataset_codigo
                  and ativo is true
                """
            ),
            {"dataset_codigo": dataset_codigo},
        )
        linha = resultado.mappings().one_or_none()
        if linha is None:
            raise PoliticaVersaoDatasetNaoEncontradaError(
                f"Dataset {dataset_codigo} nao encontrado ou inativo "
                "em plataforma.politica_dataset."
            )
        return bool(linha["carregar_apenas_ultima_versao"])

    if conn is not None:
        return await _executar(conn)
    async with SessionLocal() as session:
        return await _executar(session)


async def obter_versao_vigente(
    dataset_codigo: str,
    conn: AsyncSession | None = None,
) -> VersaoDataset | None:
    """Retorna a versão vigente do dataset ou `None` se nunca houve carga."""

    async def _executar(session: AsyncSession) -> VersaoDataset | None:
        resultado = await session.execute(
            text(
                """
                select
                    id,
                    dataset_codigo,
                    versao,
                    url_fonte,
                    hash_arquivo,
                    publicado_em,
                    carregado_em,
                    arquivo_bytes,
                    metadados,
                    vigente
                from plataforma.versao_dataset_vigente
                where dataset_codigo = :dataset_codigo
                  and vigente is true
                """
            ),
            {"dataset_codigo": dataset_codigo},
        )
        linhas = resultado.mappings().all()
        if not linhas:
            return None
        if len(linhas) > 1:
            raise DuasVersoesVigentesError(
                f"Dataset {dataset_codigo} possui {len(linhas)} versoes vigentes; "
                "esperado exatamente 1."
            )
        linha = linhas[0]
        return VersaoDataset(
            id=int(linha["id"]),
            dataset_codigo=str(linha["dataset_codigo"]),
            versao=str(linha["versao"]),
            url_fonte=str(linha["url_fonte"]),
            hash_arquivo=str(linha["hash_arquivo"]),
            publicado_em=linha["publicado_em"],
            carregado_em=linha["carregado_em"],
            arquivo_bytes=(
                int(linha["arquivo_bytes"]) if linha["arquivo_bytes"] is not None else None
            ),
            metadados=linha["metadados"],
            vigente=bool(linha["vigente"]),
        )

    if conn is not None:
        return await _executar(conn)
    async with SessionLocal() as session:
        return await _executar(session)


async def registrar_nova_versao(
    dataset_codigo: str,
    versao: str,
    url_fonte: str,
    hash_arquivo: str,
    publicado_em: date | None = None,
    arquivo_bytes: int | None = None,
    metadados: dict[str, Any] | None = None,
    conn: AsyncSession | None = None,
) -> ResultadoRegistro:
    """Registra nova versão vigente, marcando a anterior como `vigente=false`.

    Comportamento:
    - Idempotente: se a versão vigente atual tem o mesmo `hash_arquivo`,
      retorna `'nada_a_fazer'` sem inserir nova linha.
    - Caso contrário, executa em transação:
      1) `update vigente=false` na linha vigente atual (se existir);
      2) `insert` da nova linha vigente.
      Retorna `'nova_versao'`.
    """

    if not dataset_codigo or not versao or not url_fonte or not hash_arquivo:
        raise VersaoDatasetInvalidaError(
            "dataset_codigo, versao, url_fonte e hash_arquivo sao obrigatorios."
        )

    async def _executar(session: AsyncSession) -> ResultadoRegistro:
        politica_resultado = await session.execute(
            text(
                """
                select classe_dataset
                from plataforma.politica_dataset
                where dataset_codigo = :dataset_codigo
                  and ativo is true
                """
            ),
            {"dataset_codigo": dataset_codigo},
        )
        politica = politica_resultado.mappings().one_or_none()
        if politica is None:
            raise PoliticaVersaoDatasetNaoEncontradaError(
                f"Dataset {dataset_codigo} nao encontrado ou inativo "
                "em plataforma.politica_dataset."
            )
        if politica["classe_dataset"] not in _CLASSES_COM_MANIFESTO:
            raise DatasetNaoVersionadoError(
                f"Dataset {dataset_codigo} tem classe {politica['classe_dataset']!r}; "
                "manifesto de versao vigente cobre apenas "
                f"{_CLASSES_COM_MANIFESTO}."
            )

        atual_resultado = await session.execute(
            text(
                """
                select id, hash_arquivo
                from plataforma.versao_dataset_vigente
                where dataset_codigo = :dataset_codigo
                  and vigente is true
                """
            ),
            {"dataset_codigo": dataset_codigo},
        )
        atual = atual_resultado.mappings().one_or_none()

        if atual is not None and str(atual["hash_arquivo"]) == hash_arquivo:
            logger.info(
                "versao_vigente_inalterada",
                dataset_codigo=dataset_codigo,
                hash_arquivo=hash_arquivo,
                versao=versao,
            )
            return "nada_a_fazer"

        if atual is not None:
            await session.execute(
                text(
                    """
                    update plataforma.versao_dataset_vigente
                       set vigente = false
                     where id = :id
                    """
                ),
                {"id": atual["id"]},
            )

        await session.execute(
            text(
                """
                insert into plataforma.versao_dataset_vigente (
                    dataset_codigo,
                    versao,
                    url_fonte,
                    hash_arquivo,
                    publicado_em,
                    arquivo_bytes,
                    metadados,
                    vigente
                ) values (
                    :dataset_codigo,
                    :versao,
                    :url_fonte,
                    :hash_arquivo,
                    :publicado_em,
                    :arquivo_bytes,
                    cast(:metadados as jsonb),
                    true
                )
                """
            ),
            {
                "dataset_codigo": dataset_codigo,
                "versao": versao,
                "url_fonte": url_fonte,
                "hash_arquivo": hash_arquivo,
                "publicado_em": publicado_em,
                "arquivo_bytes": arquivo_bytes,
                "metadados": _serializar_metadados(metadados),
            },
        )
        logger.info(
            "versao_vigente_registrada",
            dataset_codigo=dataset_codigo,
            versao=versao,
            hash_arquivo=hash_arquivo,
            substituiu_anterior=atual is not None,
        )
        return "nova_versao"

    if conn is not None:
        return await _executar(conn)
    async with SessionLocal() as session:
        async with session.begin():
            resultado = await _executar(session)
        return resultado


def _serializar_metadados(metadados: dict[str, Any] | None) -> str | None:
    if metadados is None:
        return None
    import json

    return json.dumps(metadados, ensure_ascii=False, sort_keys=True, default=str)


def calcular_hash_arquivo(
    caminho: Path | str,
    algoritmo: str = "sha256",
    tamanho_chunk: int = 1024 * 1024,
) -> str:
    """Calcula hash criptográfico do arquivo lido em chunks.

    Default `sha256`. `md5` é proibido como hash principal por questão de
    integridade.
    """

    if algoritmo.lower() == "md5":
        raise VersaoDatasetInvalidaError(
            "MD5 nao e permitido como hash principal; use sha256."
        )
    caminho = Path(caminho)
    hasher = hashlib.new(algoritmo)
    with caminho.open("rb") as arquivo:
        while True:
            bloco = arquivo.read(tamanho_chunk)
            if not bloco:
                break
            hasher.update(bloco)
    return hasher.hexdigest()


async def descartar_versoes_antigas_em_bruto(
    schema: str,
    tabela: str,
    dataset_codigo: str,
    coluna_versao: str = "versao_dataset",
    conn: AsyncSession | None = None,
) -> int:
    """Remove linhas de versões antigas em uma tabela bruta.

    Só executa se `politica_exige_apenas_ultima_versao(dataset_codigo)=True`.
    Se a tabela ou a coluna não existirem, retorna `0` e não falha; isso
    permite cargas que ainda não têm coluna `versao_dataset` no schema raw.
    """

    async def _executar(session: AsyncSession) -> int:
        if not await politica_exige_apenas_ultima_versao(dataset_codigo, session):
            logger.info(
                "descartar_versoes_antigas_skip_politica",
                dataset_codigo=dataset_codigo,
                motivo="carregar_apenas_ultima_versao=false",
            )
            return 0

        vigente = await obter_versao_vigente(dataset_codigo, session)
        if vigente is None:
            raise VersaoDatasetInvalidaError(
                f"Dataset {dataset_codigo} sem versao vigente registrada; "
                "registre antes de descartar versoes antigas."
            )

        tabela_existe = await session.scalar(
            text(
                """
                select exists (
                    select 1
                    from information_schema.tables
                    where table_schema = :schema and table_name = :tabela
                )
                """
            ),
            {"schema": schema, "tabela": tabela},
        )
        if not tabela_existe:
            logger.info(
                "descartar_versoes_antigas_tabela_inexistente",
                schema=schema,
                tabela=tabela,
                dataset_codigo=dataset_codigo,
            )
            return 0

        coluna_existe = await session.scalar(
            text(
                """
                select exists (
                    select 1
                    from information_schema.columns
                    where table_schema = :schema
                      and table_name = :tabela
                      and column_name = :coluna
                )
                """
            ),
            {"schema": schema, "tabela": tabela, "coluna": coluna_versao},
        )
        if not coluna_existe:
            logger.info(
                "descartar_versoes_antigas_coluna_inexistente",
                schema=schema,
                tabela=tabela,
                coluna=coluna_versao,
                dataset_codigo=dataset_codigo,
            )
            return 0

        # SQL com identificadores validados acima — uso de format() é seguro.
        comando_sql = (
            f'delete from "{schema}"."{tabela}" '
            f'where "{coluna_versao}" is distinct from :versao_vigente'
        )
        resultado = await session.execute(
            text(comando_sql),
            {"versao_vigente": vigente.versao},
        )
        removidas = int(resultado.rowcount or 0)
        logger.info(
            "descartar_versoes_antigas_concluido",
            schema=schema,
            tabela=tabela,
            dataset_codigo=dataset_codigo,
            versao_vigente=vigente.versao,
            linhas_removidas=removidas,
        )
        return removidas

    if conn is not None:
        return await _executar(conn)
    async with SessionLocal() as session:
        async with session.begin():
            removidas = await _executar(session)
        return removidas


async def garantir_unica_versao_vigente(
    dataset_codigo: str,
    conn: AsyncSession | None = None,
) -> None:
    """Valida que existe no máximo uma linha vigente para o dataset.

    Levanta `DuasVersoesVigentesError` se houver mais de uma vigente. Não
    falha se houver zero (cargas iniciais ainda podem não ter ocorrido).
    """

    async def _executar(session: AsyncSession) -> None:
        total = await session.scalar(
            text(
                """
                select count(*)
                from plataforma.versao_dataset_vigente
                where dataset_codigo = :dataset_codigo
                  and vigente is true
                """
            ),
            {"dataset_codigo": dataset_codigo},
        )
        if total is not None and int(total) > 1:
            raise DuasVersoesVigentesError(
                f"Dataset {dataset_codigo} possui {total} versoes vigentes; "
                "esperado no maximo 1."
            )

    if conn is not None:
        await _executar(conn)
        return
    async with SessionLocal() as session:
        await _executar(session)
