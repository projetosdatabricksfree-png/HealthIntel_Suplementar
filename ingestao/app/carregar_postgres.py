from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from ingestao.app.config import get_settings

settings = get_settings()
engine = create_async_engine(settings.postgres_dsn, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


@dataclass(slots=True)
class LoteCarga:
    tabela_destino: str
    lote_id: str
    total_registros: int


def preparar_carga(tabela_destino: str, lote_id: str, total_registros: int) -> LoteCarga:
    return LoteCarga(
        tabela_destino=tabela_destino, lote_id=lote_id, total_registros=total_registros
    )


DATASET_CONFIG = {
    "cadop": {
        "tabela_destino": "bruto_ans.cadop",
        "colunas": [
            "registro_ans",
            "cnpj",
            "razao_social",
            "nome_fantasia",
            "modalidade",
            "cidade",
            "uf",
            "competencia",
        ],
    },
    "sib_operadora": {
        "tabela_destino": "bruto_ans.sib_beneficiario_operadora",
        "colunas": [
            "competencia",
            "registro_ans",
            "beneficiario_medico",
            "beneficiario_odonto",
            "beneficiario_total",
        ],
    },
    "sib_municipio": {
        "tabela_destino": "bruto_ans.sib_beneficiario_municipio",
        "colunas": [
            "competencia",
            "registro_ans",
            "codigo_ibge",
            "municipio",
            "uf",
            "beneficiario_medico",
            "beneficiario_odonto",
            "beneficiario_total",
        ],
    },
    "igr": {
        "tabela_destino": "bruto_ans.igr_operadora_trimestral",
        "colunas": [
            "trimestre",
            "registro_ans",
            "modalidade",
            "porte",
            "total_reclamacoes",
            "beneficiarios",
            "igr",
            "meta_igr",
            "atingiu_meta",
            "fonte_publicacao",
        ],
    },
    "nip": {
        "tabela_destino": "bruto_ans.nip_operadora_trimestral",
        "colunas": [
            "trimestre",
            "registro_ans",
            "modalidade",
            "demandas_nip",
            "demandas_resolvidas",
            "beneficiarios",
            "taxa_intermediacao_resolvida",
            "taxa_resolutividade",
            "fonte_publicacao",
        ],
    },
    "rn623_lista": {
        "tabela_destino": "bruto_ans.rn623_lista_operadora_trimestral",
        "colunas": [
            "trimestre",
            "registro_ans",
            "modalidade",
            "tipo_lista",
            "total_nip",
            "beneficiarios",
            "igr",
            "meta_igr",
            "elegivel",
            "observacao",
            "fonte_publicacao",
        ],
    },
}


def montar_registros_carga(
    dataset_codigo: str,
    registros: list[dict],
    *,
    arquivo_origem: str,
    layout_id: str,
    layout_versao_id: str,
    hash_arquivo: str,
    hash_estrutura: str,
    status_parse: str = "sucesso",
    lote_id: str | None = None,
) -> tuple[LoteCarga, list[dict]]:
    if dataset_codigo not in DATASET_CONFIG:
        raise ValueError(f"Dataset nao suportado para carga bronze: {dataset_codigo}")

    config = DATASET_CONFIG[dataset_codigo]
    lote_id = lote_id or str(uuid4())
    carregado_em = datetime.now(tz=UTC)
    colunas_negocio = config["colunas"]
    registros_preparados: list[dict] = []
    for registro in registros:
        linha = {coluna: registro.get(coluna) for coluna in colunas_negocio}
        linha.update(
            {
                "_carregado_em": carregado_em,
                "_arquivo_origem": arquivo_origem,
                "_lote_id": lote_id,
                "_layout_id": layout_id,
                "_layout_versao_id": layout_versao_id,
                "_hash_arquivo": hash_arquivo,
                "_hash_estrutura": hash_estrutura,
                "_status_parse": status_parse,
            }
        )
        registros_preparados.append(linha)
    return (
        preparar_carga(
            tabela_destino=config["tabela_destino"],
            lote_id=lote_id,
            total_registros=len(registros_preparados),
        ),
        registros_preparados,
    )


async def carregar_dataset_bruto(
    dataset_codigo: str,
    registros: list[dict],
    *,
    arquivo_origem: str,
    layout_id: str,
    layout_versao_id: str,
    hash_arquivo: str,
    hash_estrutura: str,
    status_parse: str = "sucesso",
    lote_id: str | None = None,
    colunas_mapeadas: list[dict] | None = None,
) -> LoteCarga:
    lote, registros_preparados = montar_registros_carga(
        dataset_codigo,
        registros,
        arquivo_origem=arquivo_origem,
        layout_id=layout_id,
        layout_versao_id=layout_versao_id,
        hash_arquivo=hash_arquivo,
        hash_estrutura=hash_estrutura,
        status_parse=status_parse,
        lote_id=lote_id,
    )
    if not registros_preparados:
        return lote

    colunas = list(registros_preparados[0].keys())
    placeholders = ", ".join(f":{coluna}" for coluna in colunas)
    sql = text(
        f"""
        insert into {lote.tabela_destino} ({", ".join(colunas)})
        values ({placeholders})
        """
    )
    async with SessionLocal() as session:
        await session.execute(sql, registros_preparados)
        await registrar_execucao_layout(
            session=session,
            lote_id=lote.lote_id,
            dataset_codigo=dataset_codigo,
            arquivo_origem=arquivo_origem,
            layout_id=layout_id,
            layout_versao_id=layout_versao_id,
            total_registros=lote.total_registros,
            status=status_parse,
        )
        await registrar_mapeamento_resolvido(
            session=session,
            lote_id=lote.lote_id,
            layout_id=layout_id,
            layout_versao_id=layout_versao_id,
            registros=registros_preparados,
            colunas_mapeadas=colunas_mapeadas,
        )
        await registrar_versao_dataset(
            session=session,
            dataset_codigo=dataset_codigo,
            hash_arquivo=hash_arquivo,
            hash_estrutura=hash_estrutura,
            registros_brutos=registros_preparados,
            registros=lote.total_registros,
            status=status_parse,
        )
        await session.commit()
    return lote


async def carregar_cadop_bruto(
    registros: list[dict],
    *,
    arquivo_origem: str,
    layout_id: str,
    layout_versao_id: str,
    hash_arquivo: str,
    hash_estrutura: str,
    status_parse: str = "sucesso",
    lote_id: str | None = None,
    colunas_mapeadas: list[dict] | None = None,
) -> LoteCarga:
    return await carregar_dataset_bruto(
        "cadop",
        registros,
        arquivo_origem=arquivo_origem,
        layout_id=layout_id,
        layout_versao_id=layout_versao_id,
        hash_arquivo=hash_arquivo,
        hash_estrutura=hash_estrutura,
        status_parse=status_parse,
        lote_id=lote_id,
        colunas_mapeadas=colunas_mapeadas,
    )


async def carregar_sib_operadora_bruto(
    registros: list[dict],
    *,
    arquivo_origem: str,
    layout_id: str,
    layout_versao_id: str,
    hash_arquivo: str,
    hash_estrutura: str,
    status_parse: str = "sucesso",
    lote_id: str | None = None,
    colunas_mapeadas: list[dict] | None = None,
) -> LoteCarga:
    return await carregar_dataset_bruto(
        "sib_operadora",
        registros,
        arquivo_origem=arquivo_origem,
        layout_id=layout_id,
        layout_versao_id=layout_versao_id,
        hash_arquivo=hash_arquivo,
        hash_estrutura=hash_estrutura,
        status_parse=status_parse,
        lote_id=lote_id,
        colunas_mapeadas=colunas_mapeadas,
    )


async def carregar_sib_municipio_bruto(
    registros: list[dict],
    *,
    arquivo_origem: str,
    layout_id: str,
    layout_versao_id: str,
    hash_arquivo: str,
    hash_estrutura: str,
    status_parse: str = "sucesso",
    lote_id: str | None = None,
    colunas_mapeadas: list[dict] | None = None,
) -> LoteCarga:
    return await carregar_dataset_bruto(
        "sib_municipio",
        registros,
        arquivo_origem=arquivo_origem,
        layout_id=layout_id,
        layout_versao_id=layout_versao_id,
        hash_arquivo=hash_arquivo,
        hash_estrutura=hash_estrutura,
        status_parse=status_parse,
        lote_id=lote_id,
        colunas_mapeadas=colunas_mapeadas,
    )


async def carregar_igr_bruto(
    registros: list[dict],
    *,
    arquivo_origem: str,
    layout_id: str,
    layout_versao_id: str,
    hash_arquivo: str,
    hash_estrutura: str,
    status_parse: str = "sucesso",
    lote_id: str | None = None,
    colunas_mapeadas: list[dict] | None = None,
) -> LoteCarga:
    return await carregar_dataset_bruto(
        "igr",
        registros,
        arquivo_origem=arquivo_origem,
        layout_id=layout_id,
        layout_versao_id=layout_versao_id,
        hash_arquivo=hash_arquivo,
        hash_estrutura=hash_estrutura,
        status_parse=status_parse,
        lote_id=lote_id,
        colunas_mapeadas=colunas_mapeadas,
    )


async def carregar_nip_bruto(
    registros: list[dict],
    *,
    arquivo_origem: str,
    layout_id: str,
    layout_versao_id: str,
    hash_arquivo: str,
    hash_estrutura: str,
    status_parse: str = "sucesso",
    lote_id: str | None = None,
    colunas_mapeadas: list[dict] | None = None,
) -> LoteCarga:
    return await carregar_dataset_bruto(
        "nip",
        registros,
        arquivo_origem=arquivo_origem,
        layout_id=layout_id,
        layout_versao_id=layout_versao_id,
        hash_arquivo=hash_arquivo,
        hash_estrutura=hash_estrutura,
        status_parse=status_parse,
        lote_id=lote_id,
        colunas_mapeadas=colunas_mapeadas,
    )


async def carregar_rn623_lista_bruto(
    registros: list[dict],
    *,
    arquivo_origem: str,
    layout_id: str,
    layout_versao_id: str,
    hash_arquivo: str,
    hash_estrutura: str,
    status_parse: str = "sucesso",
    lote_id: str | None = None,
    colunas_mapeadas: list[dict] | None = None,
) -> LoteCarga:
    return await carregar_dataset_bruto(
        "rn623_lista",
        registros,
        arquivo_origem=arquivo_origem,
        layout_id=layout_id,
        layout_versao_id=layout_versao_id,
        hash_arquivo=hash_arquivo,
        hash_estrutura=hash_estrutura,
        status_parse=status_parse,
        lote_id=lote_id,
        colunas_mapeadas=colunas_mapeadas,
    )


async def registrar_quarentena(
    *,
    dataset_codigo: str,
    arquivo_origem: str,
    hash_arquivo: str,
    hash_estrutura: str | None,
    motivo: str,
    status: str = "pendente",
) -> str:
    quarentena_id = str(uuid4())
    sql = text(
        """
        insert into plataforma.arquivo_quarentena (
            id, dataset, arquivo_origem, hash_arquivo, hash_estrutura, motivo, status
        ) values (
            :id, :dataset, :arquivo_origem, :hash_arquivo, :hash_estrutura, :motivo, :status
        )
        """
    )
    async with SessionLocal() as session:
        await session.execute(
            sql,
            {
                "id": quarentena_id,
                "dataset": dataset_codigo,
                "arquivo_origem": arquivo_origem,
                "hash_arquivo": hash_arquivo,
                "hash_estrutura": hash_estrutura,
                "motivo": motivo,
                "status": status,
            },
        )
        await session.commit()
    return quarentena_id


async def registrar_execucao_layout(
    *,
    session: AsyncSession,
    lote_id: str,
    dataset_codigo: str,
    arquivo_origem: str,
    layout_id: str,
    layout_versao_id: str,
    total_registros: int,
    status: str,
) -> None:
    await session.execute(
        text(
            """
            insert into plataforma.execucao_layout (
                id, arquivo_id, dataset, layout_id, layout_versao_id, status,
                iniciado_em, finalizado_em, registros_processados, registros_com_erro
            ) values (
                :id, :arquivo_id, :dataset, :layout_id, :layout_versao_id, :status,
                now(), now(), :registros_processados, 0
            )
            """
        ),
        {
            "id": lote_id,
            "arquivo_id": arquivo_origem,
            "dataset": dataset_codigo,
            "layout_id": layout_id,
            "layout_versao_id": layout_versao_id,
            "status": status,
            "registros_processados": total_registros,
        },
    )


async def registrar_mapeamento_resolvido(
    *,
    session: AsyncSession,
    lote_id: str,
    layout_id: str,
    layout_versao_id: str,
    registros: list[dict],
    colunas_mapeadas: list[dict] | None = None,
) -> None:
    if not registros:
        return
    valores = []
    if colunas_mapeadas:
        valores = [
            {
                "lote_id": lote_id,
                "layout_id": layout_id,
                "layout_versao_id": layout_versao_id,
                "origem_coluna": item["origem"],
                "destino_raw": item["destino_raw"],
                "regra_transformacao": item.get("via", "identity"),
            }
            for item in colunas_mapeadas
        ]
    else:
        colunas_tecnicas = {
            "_carregado_em",
            "_arquivo_origem",
            "_lote_id",
            "_layout_id",
            "_layout_versao_id",
            "_hash_arquivo",
            "_hash_estrutura",
            "_status_parse",
        }
        valores = [
            {
                "lote_id": lote_id,
                "layout_id": layout_id,
                "layout_versao_id": layout_versao_id,
                "origem_coluna": coluna,
                "destino_raw": coluna,
                "regra_transformacao": "identity",
            }
            for coluna in registros[0].keys()
            if coluna not in colunas_tecnicas
        ]
    if not valores:
        return
    await session.execute(
        text(
            """
            insert into plataforma.mapa_layout_resolvido (
                lote_id,
                layout_id,
                layout_versao_id,
                origem_coluna,
                destino_raw,
                regra_transformacao
            ) values (
                :lote_id,
                :layout_id,
                :layout_versao_id,
                :origem_coluna,
                :destino_raw,
                :regra_transformacao
            )
            """
        ),
        valores,
    )


async def registrar_versao_dataset(
    *,
    session: AsyncSession,
    dataset_codigo: str,
    hash_arquivo: str,
    hash_estrutura: str,
    registros_brutos: list[dict],
    registros: int,
    status: str,
) -> None:
    competencia = None
    if registros_brutos:
        valor_competencia = registros_brutos[0].get("competencia")
        if valor_competencia is None:
            valor_competencia = registros_brutos[0].get("trimestre")
        competencia = str(valor_competencia) if valor_competencia is not None else None
    await session.execute(
        text(
            """
            insert into plataforma.versao_dataset (
                id,
                dataset,
                versao,
                competencia,
                hash_arquivo,
                hash_estrutura,
                registros,
                status
            ) values (
                :id,
                :dataset,
                :versao,
                :competencia,
                :hash_arquivo,
                :hash_estrutura,
                :registros,
                :status
            )
            """
        ),
        {
            "id": str(uuid4()),
            "dataset": dataset_codigo,
            "versao": f"{dataset_codigo}_{datetime.now(tz=UTC).strftime('%Y%m%d%H%M%S')}",
            "competencia": competencia,
            "hash_arquivo": hash_arquivo,
            "hash_estrutura": hash_estrutura,
            "registros": registros,
            "status": status,
        },
    )
