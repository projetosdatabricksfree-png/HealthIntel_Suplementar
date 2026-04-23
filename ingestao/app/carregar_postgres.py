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
    "idss": {
        "tabela_destino": "bruto_ans.idss",
        "colunas": [
            "ano_base",
            "registro_ans",
            "idss_total",
            "idqs",
            "idga",
            "idsm",
            "idgr",
            "faixa_idss",
            "fonte_publicacao",
        ],
    },
    "regime_especial": {
        "tabela_destino": "bruto_ans.regime_especial_operadora_trimestral",
        "colunas": [
            "trimestre",
            "registro_ans",
            "tipo_regime",
            "data_inicio",
            "data_fim",
            "descricao",
            "fonte_publicacao",
        ],
    },
    "prudencial": {
        "tabela_destino": "bruto_ans.prudencial_operadora_trimestral",
        "colunas": [
            "trimestre",
            "registro_ans",
            "margem_solvencia",
            "capital_minimo_requerido",
            "capital_disponivel",
            "indice_liquidez",
            "situacao_prudencial",
            "fonte_publicacao",
        ],
    },
    "portabilidade": {
        "tabela_destino": "bruto_ans.portabilidade_operadora_mensal",
        "colunas": [
            "competencia",
            "registro_ans",
            "modalidade",
            "tipo_contratacao",
            "qt_portabilidade_entrada",
            "qt_portabilidade_saida",
            "fonte_publicacao",
        ],
    },
    "taxa_resolutividade": {
        "tabela_destino": "bruto_ans.taxa_resolutividade_operadora_trimestral",
        "colunas": [
            "trimestre",
            "registro_ans",
            "modalidade",
            "taxa_resolutividade",
            "n_reclamacao_resolvida",
            "n_reclamacao_total",
            "fonte_publicacao",
        ],
    },
    "diops": {
        "tabela_destino": "bruto_ans.diops_operadora_trimestral",
        "colunas": [
            "trimestre",
            "registro_ans",
            "cnpj",
            "ativo_total",
            "passivo_total",
            "patrimonio_liquido",
            "receita_total",
            "despesa_total",
            "resultado_periodo",
            "provisao_tecnica",
            "margem_solvencia_calculada",
            "fonte_publicacao",
        ],
    },
    "fip": {
        "tabela_destino": "bruto_ans.fip_operadora_trimestral",
        "colunas": [
            "trimestre",
            "registro_ans",
            "modalidade",
            "tipo_contratacao",
            "sinistro_total",
            "contraprestacao_total",
            "sinistralidade_bruta",
            "ressarcimento_sus",
            "evento_indenizavel",
            "fonte_publicacao",
        ],
    },
    "vda": {
        "tabela_destino": "bruto_ans.vda_operadora_mensal",
        "colunas": [
            "competencia",
            "registro_ans",
            "valor_devido",
            "valor_pago",
            "saldo_devedor",
            "situacao_cobranca",
            "data_vencimento",
            "fonte_publicacao",
        ],
    },
    "glosa": {
        "tabela_destino": "bruto_ans.glosa_operadora_mensal",
        "colunas": [
            "competencia",
            "registro_ans",
            "tipo_glosa",
            "qt_glosa",
            "valor_glosa",
            "valor_faturado",
            "fonte_publicacao",
        ],
    },
    "rede_assistencial": {
        "tabela_destino": "bruto_ans.rede_prestador_municipio",
        "colunas": [
            "competencia",
            "registro_ans",
            "cd_municipio",
            "nm_municipio",
            "sg_uf",
            "segmento",
            "tipo_prestador",
            "qt_prestador",
            "qt_especialidade_disponivel",
            "fonte_publicacao",
        ],
    },
    "cnes_estabelecimento": {
        "tabela_destino": "bruto_ans.cnes_estabelecimento",
        "colunas": [
            "competencia",
            "cnes",
            "cnpj",
            "razao_social",
            "nome_fantasia",
            "sg_uf",
            "cd_municipio",
            "nm_municipio",
            "tipo_unidade",
            "tipo_unidade_desc",
            "esfera_administrativa",
            "vinculo_sus",
            "leitos_existentes",
            "leitos_sus",
            "latitude",
            "longitude",
            "situacao",
            "fonte_publicacao",
        ],
    },
    "tiss_procedimento": {
        "tabela_destino": "bruto_ans.tiss_procedimento_trimestral",
        "colunas": [
            "trimestre",
            "registro_ans",
            "sg_uf",
            "grupo_procedimento",
            "grupo_desc",
            "subgrupo_procedimento",
            "qt_procedimentos",
            "qt_beneficiarios_distintos",
            "valor_total",
            "modalidade",
            "tipo_contratacao",
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


async def carregar_idss_bruto(
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
        "idss",
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


async def carregar_regime_especial_bruto(
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
        "regime_especial",
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


async def carregar_prudencial_bruto(
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
        "prudencial",
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


async def carregar_portabilidade_bruto(
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
        "portabilidade",
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


async def carregar_taxa_resolutividade_bruto(
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
        "taxa_resolutividade",
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


async def carregar_diops_bruto(
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
        "diops",
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


async def carregar_fip_bruto(
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
        "fip",
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


async def carregar_vda_bruto(
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
        "vda",
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


async def carregar_glosa_bruto(
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
        "glosa",
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


async def carregar_rede_assistencial_bruto(
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
        "rede_assistencial",
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


async def carregar_cnes_bruto(
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
        "cnes_estabelecimento",
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


async def carregar_tiss_procedimento_bruto(
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
        "tiss_procedimento",
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
        if valor_competencia is None:
            valor_competencia = registros_brutos[0].get("ano_base")
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
                hash_sha256,
                hash_estrutura,
                registros,
                status
            ) values (
                :id,
                :dataset,
                :versao,
                :competencia,
                :hash_arquivo,
                :hash_sha256,
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
            "hash_sha256": hash_arquivo,
            "hash_estrutura": hash_estrutura,
            "registros": registros,
            "status": status,
        },
    )
