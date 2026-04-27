from pydantic import BaseModel


class PremiumMetaResponse(BaseModel):
    fonte: str
    competencia: str
    versao_dataset: str
    total: int
    pagina: int
    por_pagina: int
    cache: str | None = None


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


class PremiumQualityDatasetItem(BaseModel):
    fonte_documento: str
    documento_quality_status: str
    total_registro: int
    total_fonte: int
    total_valido: int
    total_invalido: int
    taxa_valido: float
    quality_score_documental: float


class PremiumOperadora360ValidadoResponse(BaseModel):
    dados: list[PremiumOperadora360ValidadoItem]
    meta: PremiumMetaResponse


class PremiumCnesEstabelecimentoValidadoResponse(BaseModel):
    dados: list[PremiumCnesEstabelecimentoValidadoItem]
    meta: PremiumMetaResponse


class PremiumQualityDatasetResponse(BaseModel):
    dados: list[PremiumQualityDatasetItem]
    meta: PremiumMetaResponse
