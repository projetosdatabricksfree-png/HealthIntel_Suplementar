from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class PrataQualidadeMeta(BaseModel):
    taxa_aprovacao: float
    registros_quarentena: int
    motivos_rejeicao: list[str]


class PrataMetaResponse(BaseModel):
    fonte: str
    competencia: str
    versao_dataset: str
    qualidade: PrataQualidadeMeta
    aviso_qualidade: str | None = None
    total: int
    pagina: int
    por_pagina: int
    cache: str | None = None


class PrataResponse(BaseModel):
    dados: list[dict]
    meta: PrataMetaResponse


class QuarentenaResumoItem(BaseModel):
    dataset: str
    arquivo_origem: str
    competencia: str
    hash_arquivo: str
    total_registros: int
    primeiro_registro_em: datetime | None = None
    ultimo_registro_em: datetime | None = None
    status_quarentena: list[str]


class QuarentenaRegistroItem(BaseModel):
    id_quarentena: UUID
    dataset: str
    arquivo_origem: str
    hash_arquivo: str
    hash_estrutura: str | None = None
    motivo: str
    status: str
    criado_em: datetime
