from pydantic import BaseModel


class PremiumMetaResponse(BaseModel):
    fonte: str
    competencia: str
    versao_dataset: str
    total: int
    pagina: int
    por_pagina: int
    cache: str | None = None


class PremiumPaginacaoResponse(BaseModel):
    total: int
    pagina: int
    por_pagina: int


class PremiumQualidadeResponse(BaseModel):
    quality_score: float | None = None
    quality_status: str | None = None
    taxa_valido: float | None = None


# ---------------------------------------------------------------------------
# Item schemas (uma por dataset premium)
# ---------------------------------------------------------------------------


class PremiumOperadora360ValidadoItem(BaseModel):
    competencia: str
    registro_ans: str
    razao_social: str | None = None
    nome_fantasia: str | None = None
    modalidade: str | None = None
    uf: str | None = None
    qt_beneficiarios: int | None = None
    variacao_12m_pct: float | None = None
    score_total: float | None = None
    componente_core: float | None = None
    componente_regulatorio: float | None = None
    componente_financeiro: float | None = None
    componente_rede: float | None = None
    componente_estrutural: float | None = None
    versao_metodologia: str | None = None
    cnpj_normalizado: str
    registro_ans_formato_valido: bool
    cnpj_digito_valido: bool
    documento_quality_status: str
    motivo_invalidade_documento: str | None = None
    quality_score_documental: float


class PremiumCnesEstabelecimentoValidadoItem(BaseModel):
    competencia: str
    cnes: str
    cnes_normalizado: str
    cnpj_normalizado: str
    razao_social: str | None = None
    nome_fantasia: str | None = None
    sg_uf: str | None = None
    cd_municipio: str
    nm_municipio: str | None = None
    tipo_unidade: str | None = None
    tipo_unidade_desc: str | None = None
    cnes_formato_valido: bool
    cnpj_digito_valido: bool
    documento_quality_status: str
    motivo_invalidade_documento: str | None = None
    quality_score_cnes: float


class PremiumTissProcedimentoTussValidadoItem(BaseModel):
    trimestre: str
    registro_ans: str
    operadora_master_id: str
    razao_social: str | None = None
    cd_procedimento_tuss: str
    grupo_desc: str | None = None
    subgrupo_procedimento: str | None = None
    qt_procedimentos: int | None = None
    vl_total: float | None = None
    custo_medio_procedimento: float | None = None
    sinistralidade_pct: float | None = None
    rank_por_valor: int | None = None
    status_mdm: str | None = None
    mdm_confidence_score: float | None = None
    procedimento_quality_status: str | None = None
    quality_score_procedimento: float | None = None


class PremiumTussProcedimentoItem(BaseModel):
    codigo_tuss: str
    descricao_tuss: str | None = None
    grupo: str | None = None
    subgrupo: str | None = None
    capitulo: str | None = None
    vigencia_inicio: str | None = None
    vigencia_fim: str | None = None
    versao_tuss: str | None = None
    is_tuss_vigente: bool | None = None
    rol_segmento: str | None = None
    rol_obrigatorio_medico: bool | None = None
    rol_obrigatorio_odonto: bool | None = None
    rol_carencia_dias: int | None = None
    rol_vigencia_inicio: str | None = None
    rol_vigencia_fim: str | None = None
    quality_score_tuss: float | None = None
    dt_processamento: str | None = None


class PremiumMdmOperadoraItem(BaseModel):
    operadora_master_id: str
    registro_ans_canonico: str
    cnpj_canonico: str | None = None
    razao_social_canonica: str | None = None
    nome_fantasia_canonico: str | None = None
    modalidade_canonica: str | None = None
    uf_canonica: str | None = None
    municipio_sede_canonico: str | None = None
    documento_quality_status: str | None = None
    status_mdm: str | None = None
    mdm_confidence_score: float | None = None
    mdm_created_at: str | None = None
    mdm_updated_at: str | None = None


class PremiumMdmPrestadorItem(BaseModel):
    prestador_master_id: str
    estabelecimento_master_id: str | None = None
    operadora_master_id: str | None = None
    cnes_canonico: str | None = None
    cnpj_canonico: str | None = None
    nome_prestador_canonico: str | None = None
    tipo_prestador_canonico: str | None = None
    cd_municipio_canonico: str | None = None
    uf_canonica: str | None = None
    documento_quality_status: str | None = None
    status_mdm: str | None = None
    mdm_confidence_score: float | None = None
    mdm_created_at: str | None = None
    mdm_updated_at: str | None = None


class PremiumContratoValidadoItem(BaseModel):
    contrato_master_id: str
    tenant_id: str
    operadora_master_id: str | None = None
    numero_contrato_canonico: str | None = None
    numero_contrato_normalizado: str | None = None
    registro_ans_canonico: str | None = None
    cnpj_operadora_canonico: str | None = None
    tipo_contrato: str | None = None
    vigencia_inicio: str | None = None
    vigencia_fim: str | None = None
    status_contrato: str | None = None
    is_operadora_mdm_resolvida: bool | None = None
    is_cnpj_operadora_estrutural_valido: bool | None = None
    has_excecao_bloqueante: bool | None = None
    mdm_confidence_score: float | None = None
    mdm_status: str | None = None
    dt_processamento: str | None = None


class PremiumSubfaturaValidadaItem(BaseModel):
    subfatura_master_id: str
    contrato_master_id: str
    tenant_id: str
    codigo_subfatura_canonico: str | None = None
    codigo_subfatura_normalizado: str | None = None
    numero_contrato_normalizado: str | None = None
    competencia: str | None = None
    centro_custo: str | None = None
    unidade_negocio: str | None = None
    vigencia_inicio: str | None = None
    vigencia_fim: str | None = None
    status_subfatura: str | None = None
    is_contrato_resolvido: bool | None = None
    has_excecao_bloqueante: bool | None = None
    mdm_confidence_score: float | None = None
    mdm_status: str | None = None
    dt_processamento: str | None = None


class PremiumQualityDatasetItem(BaseModel):
    fonte_documento: str
    documento_quality_status: str
    total_registro: int
    total_fonte: int
    total_valido: int
    total_invalido: int
    taxa_valido: float
    quality_score_documental: float


# ---------------------------------------------------------------------------
# Response envelopes
# ---------------------------------------------------------------------------


class PremiumOperadora360ValidadoResponse(BaseModel):
    dados: list[PremiumOperadora360ValidadoItem]
    meta: PremiumMetaResponse


class PremiumCnesEstabelecimentoValidadoResponse(BaseModel):
    dados: list[PremiumCnesEstabelecimentoValidadoItem]
    meta: PremiumMetaResponse


class PremiumTissProcedimentoResponse(BaseModel):
    dados: list[PremiumTissProcedimentoTussValidadoItem]
    meta: PremiumMetaResponse


class PremiumTussProcedimentoResponse(BaseModel):
    dados: list[PremiumTussProcedimentoItem]
    meta: PremiumMetaResponse


class PremiumMdmOperadoraResponse(BaseModel):
    dados: list[PremiumMdmOperadoraItem]
    meta: PremiumMetaResponse


class PremiumMdmPrestadorResponse(BaseModel):
    dados: list[PremiumMdmPrestadorItem]
    meta: PremiumMetaResponse


class PremiumContratoResponse(BaseModel):
    dados: list[PremiumContratoValidadoItem]
    meta: PremiumMetaResponse


class PremiumSubfaturaResponse(BaseModel):
    dados: list[PremiumSubfaturaValidadaItem]
    meta: PremiumMetaResponse


class PremiumQualityDatasetResponse(BaseModel):
    dados: list[PremiumQualityDatasetItem]
    meta: PremiumMetaResponse