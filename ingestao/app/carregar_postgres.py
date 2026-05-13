import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from ingestao.app.config import get_settings

settings = get_settings()
engine = create_async_engine(settings.postgres_dsn, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

POLITICA_DATASET_ALIAS = {
    "rede_assistencial": "rede_prestador",
}


@dataclass(slots=True)
class LoteCarga:
    tabela_destino: str
    lote_id: str
    total_registros: int


def preparar_carga(tabela_destino: str, lote_id: str, total_registros: int) -> LoteCarga:
    return LoteCarga(
        tabela_destino=tabela_destino, lote_id=lote_id, total_registros=total_registros
    )


def _hash_sha256_texto(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def _hash_linha_registro(registro: dict) -> str:
    payload = json.dumps(
        registro,
        sort_keys=True,
        ensure_ascii=False,
        default=str,
        separators=(",", ":"),
    )
    return _hash_sha256_texto(payload)


def _extrair_competencia(registros: list[dict]) -> str | None:
    if not registros:
        return None
    for chave in ("competencia", "trimestre", "ano_base"):
        valor = registros[0].get(chave)
        if valor is not None:
            return str(valor)
    return None


async def _obter_janela_temporal_se_aplicavel(dataset_codigo: str):
    from ingestao.app.janela_carga import (
        DatasetNaoTemporalError,
        PoliticaDatasetNaoEncontradaError,
        obter_janela,
    )

    politica_dataset_codigo = POLITICA_DATASET_ALIAS.get(dataset_codigo, dataset_codigo)
    try:
        return await obter_janela(politica_dataset_codigo)
    except (DatasetNaoTemporalError, PoliticaDatasetNaoEncontradaError):
        return None


async def _validar_janela_temporal(
    dataset_codigo: str,
    competencia: str | None,
):
    from ingestao.app.janela_carga import (
        ConfiguracaoJanelaInvalidaError,
        assegurar_dentro_da_janela_ou_falhar,
        garantir_particoes_dataset,
        normalizar_competencia,
    )

    janela = await _obter_janela_temporal_se_aplicavel(dataset_codigo)
    if janela is None:
        return None, None
    if competencia is None:
        raise ConfiguracaoJanelaInvalidaError(
            f"Dataset temporal {dataset_codigo} sem competencia derivavel para validar janela."
        )
    competencia_normalizada = normalizar_competencia(competencia)
    await garantir_particoes_dataset(janela)
    await assegurar_dentro_da_janela_ou_falhar(
        competencia_normalizada,
        janela,
        permitir_historico=False,
    )
    return janela, competencia_normalizada


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
    "produto_caracteristica": {
        "tabela_destino": "bruto_ans.produto_caracteristica",
        "include_hash_linha": False,
        "colunas": [
            "competencia",
            "registro_ans",
            "codigo_produto",
            "nome_produto",
            "segmentacao",
            "tipo_contratacao",
            "abrangencia_geografica",
            "cobertura_area",
            "modalidade",
            "uf_comercializacao",
        ],
    },
    "produto_tabela_auxiliar": {
        "tabela_destino": "bruto_ans.produto_tabela_auxiliar",
        "include_hash_linha": False,
        "colunas": [
            "competencia",
            "registro_ans",
            "codigo_produto",
            "tipo_tabela",
            "descricao_tabela",
            "codigo_item",
            "descricao_item",
        ],
    },
    "historico_plano": {
        "tabela_destino": "bruto_ans.historico_plano",
        "include_hash_linha": False,
        "colunas": [
            "competencia",
            "registro_ans",
            "codigo_plano",
            "nome_plano",
            "situacao",
            "data_situacao",
            "segmentacao",
            "tipo_contratacao",
            "abrangencia_geografica",
            "uf",
        ],
    },
    "plano_servico_opcional": {
        "tabela_destino": "bruto_ans.plano_servico_opcional",
        "include_hash_linha": False,
        "colunas": [
            "competencia",
            "registro_ans",
            "codigo_plano",
            "codigo_servico",
            "descricao_servico",
            "tipo_servico",
        ],
    },
    "quadro_auxiliar_corresponsabilidade": {
        "tabela_destino": "bruto_ans.quadro_auxiliar_corresponsabilidade",
        "include_hash_linha": False,
        "colunas": [
            "competencia",
            "registro_ans",
            "codigo_plano",
            "tipo_corresponsabilidade",
            "percentual_corresponsabilidade",
            "valor_corresponsabilidade",
            "descricao",
        ],
    },
    "tuss_oficial": {
        "tabela_destino": "bruto_ans.tuss_terminologia_oficial",
        "include_hash_linha": False,
        "colunas": [
            "codigo_tuss",
            "descricao",
            "versao_tuss",
            "vigencia_inicio",
            "vigencia_fim",
            "is_tuss_vigente",
            "grupo",
            "subgrupo",
        ],
    },
    "tiss_ambulatorial": {
        "tabela_destino": "bruto_ans.tiss_ambulatorial",
        "include_hash_linha": False,
        "colunas": [
            "competencia",
            "registro_ans",
            "cd_municipio",
            "nm_municipio",
            "sg_uf",
            "tipo_evento",
            "qt_eventos",
            "vl_pago",
            "vl_informado",
        ],
    },
    "tiss_hospitalar": {
        "tabela_destino": "bruto_ans.tiss_hospitalar",
        "include_hash_linha": False,
        "colunas": [
            "competencia",
            "registro_ans",
            "cd_municipio",
            "nm_municipio",
            "sg_uf",
            "tipo_evento",
            "qt_internacoes",
            "qt_diarias",
            "vl_pago",
            "vl_informado",
        ],
    },
    "tiss_dados_plano": {
        "tabela_destino": "bruto_ans.tiss_dados_plano",
        "include_hash_linha": False,
        "colunas": [
            "competencia",
            "registro_ans",
            "codigo_plano",
            "segmentacao",
            "tipo_contratacao",
            "qt_beneficiarios",
            "qt_eventos",
            "vl_pago",
        ],
    },
    "sip_mapa_assistencial": {
        "tabela_destino": "bruto_ans.sip_mapa_assistencial",
        "include_hash_linha": False,
        "colunas": [
            "competencia",
            "registro_ans",
            "cd_municipio",
            "nm_municipio",
            "sg_uf",
            "nm_regiao",
            "tipo_assistencial",
            "qt_beneficiarios",
            "qt_eventos",
            "indicador_cobertura",
        ],
    },
    "ressarcimento_beneficiario_abi": {
        "tabela_destino": "bruto_ans.ressarcimento_beneficiario_abi",
        "include_hash_linha": False,
        "colunas": [
            "competencia",
            "registro_ans",
            "nu_abi",
            "cd_municipio",
            "nm_municipio",
            "sg_uf",
            "qt_beneficiarios",
            "vl_ressarcimento",
            "status_ressarcimento",
        ],
    },
    "ressarcimento_sus_operadora_plano": {
        "tabela_destino": "bruto_ans.ressarcimento_sus_operadora_plano",
        "include_hash_linha": False,
        "colunas": [
            "competencia",
            "registro_ans",
            "codigo_plano",
            "qt_autorizacoes",
            "vl_cobrado",
            "vl_pago",
            "vl_pendente",
            "status_cobranca",
        ],
    },
    "ressarcimento_hc": {
        "tabela_destino": "bruto_ans.ressarcimento_hc",
        "include_hash_linha": False,
        "colunas": [
            "competencia",
            "registro_ans",
            "nu_hc",
            "vl_hc",
            "status_hc",
            "fase_cobranca",
        ],
    },
    "ressarcimento_cobranca_arrecadacao": {
        "tabela_destino": "bruto_ans.ressarcimento_cobranca_arrecadacao",
        "include_hash_linha": False,
        "colunas": [
            "competencia",
            "registro_ans",
            "vl_cobrado",
            "vl_arrecadado",
            "vl_inadimplente",
            "qt_guias",
        ],
    },
    "ressarcimento_indice_pagamento": {
        "tabela_destino": "bruto_ans.ressarcimento_indice_pagamento",
        "include_hash_linha": False,
        "colunas": [
            "competencia",
            "registro_ans",
            "indice_efetivo_pagamento",
            "valor_total_cobrado",
            "valor_total_pago",
        ],
    },
    "ntrp_area_comercializacao": {
        "tabela_destino": "bruto_ans.ntrp_area_comercializacao",
        "include_hash_linha": False,
        "colunas": [
            "competencia",
            "registro_ans",
            "codigo_plano",
            "cd_municipio",
            "nm_municipio",
            "sg_uf",
            "area_comercializacao",
        ],
    },
    "painel_precificacao": {
        "tabela_destino": "bruto_ans.painel_precificacao",
        "include_hash_linha": False,
        "colunas": [
            "competencia",
            "registro_ans",
            "codigo_plano",
            "segmentacao",
            "faixa_etaria",
            "sg_uf",
            "tipo_contratacao",
            "vl_mensalidade_media",
            "vl_mensalidade_min",
            "vl_mensalidade_max",
            "qt_beneficiarios",
        ],
    },
    "percentual_reajuste_agrupamento": {
        "tabela_destino": "bruto_ans.percentual_reajuste_agrupamento",
        "include_hash_linha": False,
        "colunas": [
            "competencia",
            "registro_ans",
            "tipo_contratacao",
            "agrupamento",
            "percentual_reajuste",
            "data_aplicacao",
        ],
    },
    "ntrp_vcm_faixa_etaria": {
        "tabela_destino": "bruto_ans.ntrp_vcm_faixa_etaria",
        "include_hash_linha": False,
        "colunas": [
            "competencia",
            "registro_ans",
            "codigo_plano",
            "faixa_etaria",
            "sg_uf",
            "vcm",
            "vl_minimo",
            "vl_maximo",
        ],
    },
    "valor_comercial_medio_municipio": {
        "tabela_destino": "bruto_ans.valor_comercial_medio_municipio",
        "include_hash_linha": False,
        "colunas": [
            "competencia",
            "cd_municipio",
            "nm_municipio",
            "sg_uf",
            "segmentacao",
            "faixa_etaria",
            "vcm_municipio",
            "qt_planos",
        ],
    },
    "faixa_preco": {
        "tabela_destino": "bruto_ans.faixa_preco",
        "include_hash_linha": False,
        "colunas": [
            "competencia",
            "registro_ans",
            "codigo_plano",
            "faixa_etaria",
            "sg_uf",
            "vl_faixa_min",
            "vl_faixa_max",
        ],
    },
    "operadora_cancelada": {
        "tabela_destino": "bruto_ans.operadora_cancelada",
        "include_hash_linha": False,
        "colunas": [
            "registro_ans",
            "razao_social",
            "cnpj",
            "modalidade",
            "data_cancelamento",
            "motivo_cancelamento",
            "sg_uf",
        ],
    },
    "operadora_acreditada": {
        "tabela_destino": "bruto_ans.operadora_acreditada",
        "include_hash_linha": False,
        "colunas": [
            "registro_ans",
            "razao_social",
            "acreditadora",
            "nivel_acreditacao",
            "data_acreditacao",
            "data_validade",
        ],
    },
    "prestador_acreditado": {
        "tabela_destino": "bruto_ans.prestador_acreditado",
        "include_hash_linha": False,
        "colunas": [
            "cnes",
            "nm_prestador",
            "cnpj",
            "cd_municipio",
            "nm_municipio",
            "sg_uf",
            "acreditadora",
            "nivel_acreditacao",
            "data_acreditacao",
            "data_validade",
        ],
    },
    "produto_prestador_hospitalar": {
        "tabela_destino": "bruto_ans.produto_prestador_hospitalar",
        "include_hash_linha": False,
        "colunas": [
            "competencia",
            "registro_ans",
            "codigo_produto",
            "cnes",
            "nm_prestador",
            "cd_municipio",
            "sg_uf",
            "tipo_vinculo",
        ],
    },
    "operadora_prestador_nao_hospitalar": {
        "tabela_destino": "bruto_ans.operadora_prestador_nao_hospitalar",
        "include_hash_linha": False,
        "colunas": [
            "competencia",
            "registro_ans",
            "cnes",
            "nm_prestador",
            "cd_municipio",
            "sg_uf",
            "tipo_servico",
            "tipo_vinculo",
        ],
    },
    "solicitacao_alteracao_rede_hospitalar": {
        "tabela_destino": "bruto_ans.solicitacao_alteracao_rede_hospitalar",
        "include_hash_linha": False,
        "colunas": [
            "competencia",
            "registro_ans",
            "nu_solicitacao",
            "tipo_alteracao",
            "cnes",
            "nm_prestador",
            "cd_municipio",
            "sg_uf",
            "data_solicitacao",
            "status_solicitacao",
        ],
    },
    "penalidade_operadora": {
        "tabela_destino": "bruto_ans.penalidade_operadora",
        "include_hash_linha": False,
        "colunas": [
            "competencia",
            "registro_ans",
            "nu_processo",
            "tipo_penalidade",
            "descricao_infracao",
            "vl_multa",
            "data_penalidade",
            "status_penalidade",
        ],
    },
    "monitoramento_garantia_atendimento": {
        "tabela_destino": "bruto_ans.monitoramento_garantia_atendimento",
        "include_hash_linha": False,
        "colunas": [
            "competencia",
            "registro_ans",
            "tipo_garantia",
            "qt_ocorrencias",
            "qt_resolvidas",
            "qt_pendentes",
            "prazo_medio_resolucao",
        ],
    },
    "peona_sus": {
        "tabela_destino": "bruto_ans.peona_sus",
        "include_hash_linha": False,
        "colunas": [
            "competencia",
            "registro_ans",
            "vl_peona",
            "qt_beneficiarios_sus",
            "indicador_utilizacao_sus",
            "sg_uf",
        ],
    },
    "promoprev": {
        "tabela_destino": "bruto_ans.promoprev",
        "include_hash_linha": False,
        "colunas": [
            "competencia",
            "registro_ans",
            "tipo_programa",
            "qt_beneficiarios_programa",
            "vl_investimento",
            "indicador_participacao",
        ],
    },
    "rpc": {
        "tabela_destino": "bruto_ans.rpc",
        "include_hash_linha": False,
        "colunas": [
            "competencia",
            "registro_ans",
            "cd_municipio",
            "sg_uf",
            "tipo_reclamacao",
            "qt_reclamacoes",
            "qt_resolvidas",
            "indice_resolucao",
            "nota_rpc",
        ],
    },
    "iap": {
        "tabela_destino": "bruto_ans.iap",
        "include_hash_linha": False,
        "colunas": [
            "competencia",
            "registro_ans",
            "dimensao",
            "indicador",
            "valor_indicador",
            "peso_indicador",
            "pontuacao",
        ],
    },
    "pfa": {
        "tabela_destino": "bruto_ans.pfa",
        "include_hash_linha": False,
        "colunas": [
            "competencia",
            "registro_ans",
            "indicador",
            "valor_indicador",
            "meta",
            "status_meta",
        ],
    },
    "programa_qualificacao_institucional": {
        "tabela_destino": "bruto_ans.programa_qualificacao_institucional",
        "include_hash_linha": False,
        "colunas": [
            "competencia",
            "registro_ans",
            "nivel_qualificacao",
            "pontuacao_qualificacao",
            "data_avaliacao",
            "status_qualificacao",
        ],
    },
    "beneficiario_regiao_geografica": {
        "tabela_destino": "bruto_ans.beneficiario_regiao_geografica",
        "include_hash_linha": False,
        "colunas": [
            "competencia",
            "cd_regiao",
            "nm_regiao",
            "sg_uf",
            "tipo_plano",
            "segmentacao",
            "qt_beneficiarios",
        ],
    },
    "beneficiario_informacao_consolidada": {
        "tabela_destino": "bruto_ans.beneficiario_informacao_consolidada",
        "include_hash_linha": False,
        "colunas": [
            "competencia",
            "sg_uf",
            "cd_municipio",
            "nm_municipio",
            "segmentacao",
            "tipo_contratacao",
            "faixa_etaria",
            "sexo",
            "qt_beneficiarios",
        ],
    },
    "taxa_cobertura_plano": {
        "tabela_destino": "bruto_ans.taxa_cobertura_plano",
        "include_hash_linha": False,
        "colunas": [
            "competencia",
            "sg_uf",
            "cd_municipio",
            "nm_municipio",
            "populacao_total",
            "qt_beneficiarios",
            "taxa_cobertura",
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
        if config.get("include_hash_linha", True):
            linha["_hash_linha"] = _hash_linha_registro(linha)
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
    registros_quarentena: list[dict] | None = None,
) -> LoteCarga:
    competencia = _extrair_competencia(registros)
    janela_carga, competencia_janela = await _validar_janela_temporal(
        dataset_codigo,
        competencia,
    )
    async with SessionLocal() as session:
        resultado_dup = await session.execute(
            text(
                """
                select 1
                from plataforma.lote_ingestao
                where dataset = :dataset
                  and hash_arquivo = :hash_arquivo
                  and status in ('sucesso', 'sucesso_com_alertas')
                limit 1
                """
            ),
            {
                "dataset": dataset_codigo,
                "hash_arquivo": hash_arquivo,
                "competencia": competencia,
            },
        )
        duplicado = resultado_dup.scalar_one_or_none() is not None

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
    if duplicado:
        await registrar_lote_ingestao(
            lote_id=lote.lote_id,
            dataset_codigo=dataset_codigo,
            competencia=competencia,
            arquivo_origem=arquivo_origem,
            hash_arquivo=hash_arquivo,
            hash_estrutura=hash_estrutura,
            versao_layout=layout_versao_id,
            status="ignorado_duplicata",
            total_linhas_raw=len(registros),
            total_aprovadas=0,
            total_quarentena=0,
            origem_execucao="carregar_postgres",
            erro_mensagem=(
                "Lote duplicado rejeitado por hash_arquivo com carga anterior bem-sucedida."
            ),
        )
        await registrar_job_carga(
            dataset_codigo=dataset_codigo,
            hash_arquivo=hash_arquivo,
            status="ignorado_duplicata",
            total_processado=0,
            total_erro=0,
            camada="bronze",
            mensagem_erro="Lote duplicado rejeitado por hash_arquivo e competencia.",
        )
        return preparar_carga(
            tabela_destino=lote.tabela_destino,
            lote_id=lote.lote_id,
            total_registros=0,
        )

    if registros_quarentena:
        for registro_quarentena in registros_quarentena:
            await registrar_quarentena(
                dataset_codigo=dataset_codigo,
                arquivo_origem=arquivo_origem,
                hash_arquivo=hash_arquivo,
                hash_estrutura=hash_estrutura,
                motivo=str(registro_quarentena.get("motivo", "registro inválido")),
                status=str(registro_quarentena.get("status", "pendente")),
            )

    if not registros_preparados:
        total_erro = len(registros_quarentena or [])
        await registrar_lote_ingestao(
            lote_id=lote.lote_id,
            dataset_codigo=dataset_codigo,
            competencia=competencia,
            arquivo_origem=arquivo_origem,
            hash_arquivo=hash_arquivo,
            hash_estrutura=hash_estrutura,
            versao_layout=layout_versao_id,
            status="sucesso_com_alertas" if total_erro else "sucesso",
            total_linhas_raw=len(registros),
            total_aprovadas=0,
            total_quarentena=total_erro,
            origem_execucao="carregar_postgres",
        )
        await registrar_job_carga(
            dataset_codigo=dataset_codigo,
            hash_arquivo=hash_arquivo,
            status="sucesso",
            total_processado=0,
            total_erro=total_erro,
            camada="bronze",
        )
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
        await registrar_lote_ingestao_session(
            session=session,
            lote_id=lote.lote_id,
            dataset_codigo=dataset_codigo,
            competencia=competencia,
            arquivo_origem=arquivo_origem,
            hash_arquivo=hash_arquivo,
            hash_estrutura=hash_estrutura,
            versao_layout=layout_versao_id,
            status="sucesso_com_alertas" if len(registros_quarentena or []) else "sucesso",
            total_linhas_raw=len(registros),
            total_aprovadas=lote.total_registros,
            total_quarentena=len(registros_quarentena or []),
            origem_execucao="carregar_postgres",
        )
        await session.commit()
    total_quarentena = len(registros_quarentena or [])
    await registrar_job_carga(
        dataset_codigo=dataset_codigo,
        hash_arquivo=hash_arquivo,
        status="sucesso_com_alertas" if total_quarentena > 0 else "sucesso",
        total_processado=lote.total_registros,
        total_erro=total_quarentena,
        camada="bronze",
    )
    if janela_carga is not None and competencia_janela is not None:
        from ingestao.app.janela_carga import registrar_decisao

        await registrar_decisao(
            janela_carga.dataset_codigo,
            competencia_janela,
            "carregado",
            janela_carga,
            "Carga concluida dentro da janela dinamica.",
        )
    return lote


async def carregar_dataset_bruto_em_batches(
    dataset_codigo: str,
    batch: list[dict],
    *,
    arquivo_origem: str,
    layout_id: str,
    layout_versao_id: str,
    hash_arquivo: str,
    hash_estrutura: str,
    lote_id: str,
    status_parse: str = "sucesso",
    colunas_mapeadas: list[dict] | None = None,
) -> int:
    if not batch:
        return 0

    if dataset_codigo not in DATASET_CONFIG:
        raise ValueError(f"Dataset nao suportado para carga bronze: {dataset_codigo}")

    competencia = _extrair_competencia(batch)
    await _validar_janela_temporal(dataset_codigo, competencia)

    config = DATASET_CONFIG[dataset_codigo]
    carregado_em = datetime.now(tz=UTC)
    colunas_negocio = config["colunas"]
    registros_preparados: list[dict] = []

    for registro in batch:
        linha = {coluna: registro.get(coluna) for coluna in colunas_negocio}
        if config.get("include_hash_linha", True):
            linha["_hash_linha"] = _hash_linha_registro(linha)
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

    if not registros_preparados:
        return 0

    colunas = list(registros_preparados[0].keys())
    placeholders = ", ".join(f":{coluna}" for coluna in colunas)
    sql = text(
        f"""
        insert into {config["tabela_destino"]} ({", ".join(colunas)})
        values ({placeholders})
        """
    )
    async with SessionLocal() as session:
        await session.execute(sql, registros_preparados)
        await session.commit()

    return len(registros_preparados)


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


async def registrar_lote_ingestao_session(
    *,
    session: AsyncSession,
    lote_id: str,
    dataset_codigo: str,
    competencia: str | None,
    arquivo_origem: str,
    hash_arquivo: str,
    hash_estrutura: str | None,
    versao_layout: str | None,
    status: str,
    total_linhas_raw: int,
    total_aprovadas: int,
    total_quarentena: int,
    origem_execucao: str,
    erro_mensagem: str | None = None,
) -> None:
    await session.execute(
        text(
            """
            insert into plataforma.lote_ingestao (
                id,
                dataset,
                competencia,
                arquivo_origem,
                hash_arquivo,
                total_linhas_raw,
                total_aprovadas,
                total_quarentena,
                status,
                erro_mensagem,
                concluido_em,
                versao_layout,
                checksum_layout,
                origem_execucao
            ) values (
                :id,
                :dataset,
                :competencia,
                :arquivo_origem,
                :hash_arquivo,
                :total_linhas_raw,
                :total_aprovadas,
                :total_quarentena,
                :status,
                :erro_mensagem,
                now(),
                :versao_layout,
                :checksum_layout,
                :origem_execucao
            )
            """
        ),
        {
            "id": lote_id,
            "dataset": dataset_codigo,
            "competencia": competencia,
            "arquivo_origem": arquivo_origem,
            "hash_arquivo": hash_arquivo,
            "total_linhas_raw": total_linhas_raw,
            "total_aprovadas": total_aprovadas,
            "total_quarentena": total_quarentena,
            "status": status,
            "erro_mensagem": erro_mensagem,
            "versao_layout": versao_layout,
            "checksum_layout": hash_estrutura,
            "origem_execucao": origem_execucao,
        },
    )


async def registrar_lote_ingestao(**kwargs) -> None:
    async with SessionLocal() as session:
        await registrar_lote_ingestao_session(session=session, **kwargs)
        await session.commit()


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


async def registrar_job_carga(
    *,
    dataset_codigo: str,
    hash_arquivo: str,
    status: str,
    total_processado: int,
    total_erro: int,
    camada: str,
    mensagem_erro: str | None = None,
) -> None:
    async with SessionLocal() as session:
        await session.execute(
            text(
                """
                insert into plataforma.job (
                    id,
                    dag_id,
                    nome_job,
                    fonte_ans,
                    hash_arquivo,
                    camada,
                    status,
                    iniciado_em,
                    finalizado_em,
                    registro_processado,
                    registro_com_falha,
                    mensagem_erro
                ) values (
                    :id,
                    :dag_id,
                    :nome_job,
                    :fonte_ans,
                    :hash_arquivo,
                    :camada,
                    :status,
                    now(),
                    now(),
                    :registro_processado,
                    :registro_com_falha,
                    :mensagem_erro
                )
                """
            ),
            {
                "id": str(uuid4()),
                "dag_id": f"ingestao_{dataset_codigo}",
                "nome_job": f"carga_{dataset_codigo}",
                "fonte_ans": dataset_codigo,
                "hash_arquivo": hash_arquivo,
                "camada": camada,
                "status": status,
                "registro_processado": total_processado,
                "registro_com_falha": total_erro,
                "mensagem_erro": mensagem_erro,
            },
        )
        await session.commit()


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
