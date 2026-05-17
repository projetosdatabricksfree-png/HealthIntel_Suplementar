from pydantic import BaseModel


class MetaEnvelope(BaseModel):
    competencia_referencia: str
    versao_dataset: str
    total: int
    pagina: int
    por_pagina: int | None = None
    janela_temporal: dict | None = None


class DatasetMetaResponse(BaseModel):
    nome: str
    descricao: str
    cadencia: str
    status: str
    produto: str | None = None
    fonte_serving: str | None = None
    row_count: int | None = None
    cobertura_temporal_inicio: str | int | None = None
    cobertura_temporal_fim: str | int | None = None
    qtd_competencias: int | None = None
    qtd_trimestres: int | None = None
    qtd_anos: int | None = None
    status_cobertura_3_anos: str | None = None
    ultima_atualizacao: str | None = None
    status_publicacao: str | None = None


class PipelineMetaResponse(BaseModel):
    dag_id: str
    dataset: str | None = None
    status: str
    iniciado_em: str
    finalizado_em: str | None = None


class VersaoDatasetResponse(BaseModel):
    dataset: str
    versao: str
    carregado_em: str
    competencia: str | None = None
    status: str


class EndpointMetaResponse(BaseModel):
    metodo: str
    rota: str
    descricao: str
    autenticacao: str
    plano_minimo: str
    camada: str | None = None
    dataset_origem: str | None = None
    versao: str
    method: str | None = None
    path: str | None = None
    grupo: str | None = None
    status: str | None = None
    produto: str | None = None
    fonte_serving: str | None = None
    requer_api_key: bool | None = None
    row_count: int | None = None
    aparece_catalogo_publico: bool | None = None
    tipo_status: str | None = None
    observacao_limite: str | None = None
    exige_3_anos: bool | None = None
    status_cobertura_3_anos: str | None = None
    tipo_granularidade_temporal: str | None = None
    endpoint_temporal: bool | None = None
    status_publicacao: str | None = None
