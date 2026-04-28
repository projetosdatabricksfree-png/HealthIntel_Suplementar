"""Carga Bronze de datasets com versão vigente.

Contrato:
- entrada: arquivo tabular local (`csv`, `txt` ou `zip` contendo CSV/TXT),
  `dataset_codigo`, `versao`, `url_fonte` e metadados opcionais;
- saída: linhas carregadas em tabelas `bruto_ans.*` da Sprint 37 e manifesto
  atualizado em `plataforma.versao_dataset_vigente`;
- ponto de integração: DAGs `dag_ingest_tuss`, `dag_ingest_rol`,
  `dag_ingest_depara_sip_tuss`, `dag_ingest_prestador_cadastral` e
  `dag_ingest_qualiss`.

A responsabilidade deste módulo é operacionalizar a regra "apenas última
versão vigente" sem alterar dbt, API ou tabelas legadas. O histórico antigo é
descartado da carga padrão quando a política exige `carregar_apenas_ultima_versao`.
"""

from __future__ import annotations

import csv
import io
import json
import unicodedata
import zipfile
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ingestao.app.carregar_postgres import SessionLocal
from ingestao.app.versao_vigente import (
    ResultadoRegistro,
    calcular_hash_arquivo,
    descartar_versoes_antigas_em_bruto,
    registrar_nova_versao,
)


@dataclass(frozen=True, slots=True)
class ConfiguracaoDatasetVigente:
    dataset_codigo: str
    schema: str
    tabela: str
    campos_canonicos: tuple[str, ...]
    aliases: dict[str, tuple[str, ...]]
    campo_chave: str
    snapshot_atual: bool = False
    tabela_snapshot_anterior: str | None = None


@dataclass(frozen=True, slots=True)
class ResultadoCargaVersaoVigente:
    dataset_codigo: str
    tabela_destino: str
    versao: str
    hash_arquivo: str
    status_manifesto: ResultadoRegistro
    linhas_carregadas: int
    linhas_removidas: int


class CargaVersaoVigenteError(Exception):
    """Erro de carga de versão vigente."""


class DatasetVigenteNaoSuportadoError(CargaVersaoVigenteError):
    """Dataset não possui configuração de carga vigente nesta sprint."""


class ArquivoVersaoVigenteInvalidoError(CargaVersaoVigenteError):
    """Arquivo de entrada inválido ou sem linhas úteis."""


DATASETS_VIGENTES: dict[str, ConfiguracaoDatasetVigente] = {
    "tuss_procedimento": ConfiguracaoDatasetVigente(
        dataset_codigo="tuss_procedimento",
        schema="bruto_ans",
        tabela="tuss_procedimento",
        campos_canonicos=("codigo_procedimento", "descricao", "grupo", "subgrupo", "capitulo"),
        aliases={
            "codigo_procedimento": ("codigo_tuss", "codigo_procedimento", "codigo"),
            "descricao": ("descricao", "descricao_tuss", "termo"),
            "grupo": ("grupo", "grupo_procedimento"),
            "subgrupo": ("subgrupo", "subgrupo_procedimento"),
            "capitulo": ("capitulo",),
        },
        campo_chave="codigo_procedimento",
    ),
    "rol_procedimento": ConfiguracaoDatasetVigente(
        dataset_codigo="rol_procedimento",
        schema="bruto_ans",
        tabela="rol_procedimento",
        campos_canonicos=(
            "codigo_procedimento",
            "descricao",
            "segmento",
            "obrigatorio_medico",
            "obrigatorio_odonto",
        ),
        aliases={
            "codigo_procedimento": ("codigo_tuss", "codigo_procedimento", "codigo"),
            "descricao": ("descricao", "descricao_rol"),
            "segmento": ("segmento",),
            "obrigatorio_medico": ("obrigatorio_medico", "cobertura_medica"),
            "obrigatorio_odonto": ("obrigatorio_odonto", "cobertura_odontologica"),
        },
        campo_chave="codigo_procedimento",
    ),
    "depara_sip_tuss": ConfiguracaoDatasetVigente(
        dataset_codigo="depara_sip_tuss",
        schema="bruto_ans",
        tabela="depara_sip_tuss",
        campos_canonicos=("codigo_procedimento_tuss", "codigo_procedimento_sip", "descricao"),
        aliases={
            "codigo_procedimento_tuss": ("codigo_tuss", "codigo_procedimento_tuss"),
            "codigo_procedimento_sip": ("codigo_sip", "codigo_procedimento_sip"),
            "descricao": ("descricao", "descricao_procedimento"),
        },
        campo_chave="codigo_procedimento_tuss",
    ),
    "prestador_cadastral": ConfiguracaoDatasetVigente(
        dataset_codigo="prestador_cadastral",
        schema="bruto_ans",
        tabela="prestador_cadastral",
        campos_canonicos=(
            "codigo_prestador",
            "cnes",
            "cnpj",
            "razao_social",
            "nome_fantasia",
            "sg_uf",
            "cd_municipio",
        ),
        aliases={
            "codigo_prestador": ("codigo_prestador", "cnes", "cnpj", "registro_ans"),
            "cnes": ("cnes", "codigo_cnes"),
            "cnpj": ("cnpj",),
            "razao_social": ("razao_social", "nome_razao_social"),
            "nome_fantasia": ("nome_fantasia",),
            "sg_uf": ("sg_uf", "uf"),
            "cd_municipio": ("cd_municipio", "codigo_municipio", "codigo_ibge"),
        },
        campo_chave="codigo_prestador",
        snapshot_atual=True,
        tabela_snapshot_anterior="prestador_cadastral_snapshot_anterior",
    ),
    "qualiss": ConfiguracaoDatasetVigente(
        dataset_codigo="qualiss",
        schema="bruto_ans",
        tabela="qualiss",
        campos_canonicos=(
            "identificador_qualiss",
            "codigo_prestador",
            "cnes",
            "cnpj",
            "atributo_qualidade",
            "resultado",
        ),
        aliases={
            "identificador_qualiss": (
                "identificador_qualiss",
                "codigo_qualiss",
                "codigo_prestador",
                "cnes",
            ),
            "codigo_prestador": ("codigo_prestador", "cnes", "cnpj", "registro_ans"),
            "cnes": ("cnes", "codigo_cnes"),
            "cnpj": ("cnpj",),
            "atributo_qualidade": ("atributo_qualidade", "indicador", "programa"),
            "resultado": ("resultado", "situacao", "classificacao"),
        },
        campo_chave="identificador_qualiss",
        snapshot_atual=True,
        tabela_snapshot_anterior="qualiss_snapshot_anterior",
    ),
}


def _normalizar_nome_coluna(nome: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", nome)
    ascii_nome = "".join(char for char in sem_acento if not unicodedata.combining(char))
    normalizado = "".join(char.lower() if char.isalnum() else "_" for char in ascii_nome)
    while "__" in normalizado:
        normalizado = normalizado.replace("__", "_")
    return normalizado.strip("_")


def _detectar_dialect(amostra: str) -> csv.Dialect:
    try:
        return csv.Sniffer().sniff(amostra, delimiters=";,|\t,")
    except csv.Error:
        dialect = csv.excel
        dialect.delimiter = ";"
        return dialect


def _iter_linhas_csv(stream: io.TextIOBase) -> Iterator[tuple[int, dict[str, str]]]:
    amostra = stream.read(8192)
    stream.seek(0)
    reader = csv.DictReader(stream, dialect=_detectar_dialect(amostra))
    if not reader.fieldnames:
        return
    for linha_origem, linha in enumerate(reader, start=2):
        yield linha_origem, {
            _normalizar_nome_coluna(str(chave)): "" if valor is None else str(valor).strip()
            for chave, valor in linha.items()
            if chave is not None
        }


def _iter_linhas_arquivo(caminho: Path) -> Iterator[tuple[int, dict[str, str]]]:
    if caminho.suffix.lower() == ".zip":
        with zipfile.ZipFile(caminho) as pacote:
            nomes = sorted(
                nome
                for nome in pacote.namelist()
                if not nome.endswith("/") and nome.lower().endswith((".csv", ".txt"))
            )
            if not nomes:
                raise ArquivoVersaoVigenteInvalidoError(
                    f"Arquivo ZIP {caminho} nao contem CSV/TXT."
                )
            with pacote.open(nomes[0], "r") as binario:
                wrapper = io.TextIOWrapper(binario, encoding="utf-8-sig", newline="")
                yield from _iter_linhas_csv(wrapper)
        return

    with caminho.open("r", encoding="utf-8-sig", newline="") as arquivo:
        yield from _iter_linhas_csv(arquivo)


def _obter_valor(linha: dict[str, str], aliases: Iterable[str]) -> str | None:
    for alias in aliases:
        valor = linha.get(_normalizar_nome_coluna(alias))
        if valor:
            return valor
    return None


def _montar_linha_canonica(
    config: ConfiguracaoDatasetVigente,
    linha_origem: int,
    linha: dict[str, str],
    *,
    versao: str,
    url_fonte: str,
    hash_arquivo: str,
    arquivo_origem: str,
) -> dict[str, Any]:
    canonica = {
        campo: _obter_valor(linha, config.aliases.get(campo, (campo,)))
        for campo in config.campos_canonicos
    }
    chave = canonica.get(config.campo_chave)
    if not chave:
        chave = f"linha_{linha_origem}"
        canonica[config.campo_chave] = chave
    canonica.update(
        {
            "versao_dataset": versao,
            "url_fonte": url_fonte,
            "hash_arquivo": hash_arquivo,
            "arquivo_origem": arquivo_origem,
            "linha_origem": linha_origem,
            "dados": json.dumps(linha, ensure_ascii=False, sort_keys=True),
        }
    )
    return canonica


async def _copiar_snapshot_anterior(
    session: AsyncSession,
    config: ConfiguracaoDatasetVigente,
) -> None:
    if not config.snapshot_atual or not config.tabela_snapshot_anterior:
        return
    await session.execute(
        text(f'truncate table "{config.schema}"."{config.tabela_snapshot_anterior}"')
    )
    await session.execute(
        text(
            f"""
            insert into "{config.schema}"."{config.tabela_snapshot_anterior}"
            select * from "{config.schema}"."{config.tabela}"
            """
        )
    )
    await session.execute(text(f'truncate table "{config.schema}"."{config.tabela}"'))


async def _inserir_linhas(
    session: AsyncSession,
    config: ConfiguracaoDatasetVigente,
    linhas: list[dict[str, Any]],
) -> int:
    if not linhas:
        return 0
    colunas = [*config.campos_canonicos, "versao_dataset", "url_fonte", "hash_arquivo"]
    colunas.extend(["arquivo_origem", "linha_origem", "dados"])
    lista_colunas = ", ".join(f'"{coluna}"' for coluna in colunas)
    placeholders = ", ".join(
        "cast(:dados as jsonb)" if coluna == "dados" else f":{coluna}" for coluna in colunas
    )
    await session.execute(
        text(
            f"""
            insert into "{config.schema}"."{config.tabela}" ({lista_colunas})
            values ({placeholders})
            """
        ),
        linhas,
    )
    return len(linhas)


async def carregar_arquivo_versao_vigente(
    dataset_codigo: str,
    caminho_arquivo: Path | str,
    *,
    versao: str,
    url_fonte: str | None = None,
    publicado_em: date | None = None,
    conn: AsyncSession | None = None,
) -> ResultadoCargaVersaoVigente:
    """Carrega um arquivo local como versão vigente de um dataset de referência."""

    config = DATASETS_VIGENTES.get(dataset_codigo)
    if config is None:
        raise DatasetVigenteNaoSuportadoError(
            f"Dataset {dataset_codigo} nao possui carga vigente configurada."
        )

    caminho = Path(caminho_arquivo)
    if not caminho.exists():
        raise ArquivoVersaoVigenteInvalidoError(f"Arquivo inexistente: {caminho}")

    hash_arquivo = calcular_hash_arquivo(caminho)
    url_resolvida = url_fonte or caminho.as_uri()
    linhas = [
        _montar_linha_canonica(
            config,
            linha_origem,
            linha,
            versao=versao,
            url_fonte=url_resolvida,
            hash_arquivo=hash_arquivo,
            arquivo_origem=caminho.name,
        )
        for linha_origem, linha in _iter_linhas_arquivo(caminho)
    ]
    if not linhas:
        raise ArquivoVersaoVigenteInvalidoError(f"Arquivo {caminho} sem linhas úteis.")

    async def _executar(session: AsyncSession) -> ResultadoCargaVersaoVigente:
        status_manifesto = await registrar_nova_versao(
            dataset_codigo,
            versao,
            url_resolvida,
            hash_arquivo,
            publicado_em=publicado_em,
            arquivo_bytes=caminho.stat().st_size,
            metadados={"arquivo_origem": caminho.name, "linhas": len(linhas)},
            conn=session,
        )
        if status_manifesto == "nada_a_fazer":
            return ResultadoCargaVersaoVigente(
                dataset_codigo=dataset_codigo,
                tabela_destino=f"{config.schema}.{config.tabela}",
                versao=versao,
                hash_arquivo=hash_arquivo,
                status_manifesto=status_manifesto,
                linhas_carregadas=0,
                linhas_removidas=0,
            )

        await _copiar_snapshot_anterior(session, config)
        await session.execute(
            text(
                f"""
                delete from "{config.schema}"."{config.tabela}"
                where versao_dataset = :versao
                """
            ),
            {"versao": versao},
        )
        linhas_carregadas = await _inserir_linhas(session, config, linhas)
        linhas_removidas = await descartar_versoes_antigas_em_bruto(
            config.schema,
            config.tabela,
            dataset_codigo,
            conn=session,
        )
        return ResultadoCargaVersaoVigente(
            dataset_codigo=dataset_codigo,
            tabela_destino=f"{config.schema}.{config.tabela}",
            versao=versao,
            hash_arquivo=hash_arquivo,
            status_manifesto=status_manifesto,
            linhas_carregadas=linhas_carregadas,
            linhas_removidas=linhas_removidas,
        )

    if conn is not None:
        return await _executar(conn)
    async with SessionLocal() as session:
        async with session.begin():
            return await _executar(session)
