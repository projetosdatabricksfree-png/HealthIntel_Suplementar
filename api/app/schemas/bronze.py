from datetime import datetime

from pydantic import BaseModel


class BronzeMetaResponse(BaseModel):
    fonte: str
    competencia: str
    lote_id: str
    arquivo_origem: str
    carregado_em: datetime
    versao_dataset: str
    aviso_qualidade: str = "Dado bruto sem garantia semantica. Use camada Prata para analise."


class BronzeResponse(BaseModel):
    dados: list[dict]
    meta: BronzeMetaResponse
