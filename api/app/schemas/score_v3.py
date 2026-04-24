from pydantic import BaseModel

from api.app.schemas.meta import MetaEnvelope


class ScoreV3Item(BaseModel):
    operadora_id: int
    competencia_id: str
    registro_ans: str
    nome: str | None = None
    nome_fantasia: str | None = None
    modalidade: str | None = None
    uf_sede: str | None = None
    trimestre_financeiro: str | None = None
    score_core: float | None = None
    score_regulatorio: float | None = None
    score_financeiro: float | None = None
    score_rede: float | None = None
    score_estrutural: float | None = None
    score_completo: bool = False
    score_v3_final: float
    versao_metodologia: str | None = None


class ScoreV3Response(BaseModel):
    dados: list[ScoreV3Item]
    meta: MetaEnvelope
