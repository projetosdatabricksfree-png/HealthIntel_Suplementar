from pydantic import BaseModel


class OperadoraResumoResponse(BaseModel):
    registro_ans: str
    nome: str
    nome_fantasia: str | None = None
    modalidade: str
    uf_sede: str
    competencia_referencia: str | None = None
    score_final: float | None = None
    rating: str | None = None
    versao_score: str | None = None


class OperadoraScoreResponse(BaseModel):
    registro_ans: str
    competencia: str
    nome: str | None = None
    modalidade: str | None = None
    uf_sede: str | None = None
    score_final: float
    rating: str
    score_crescimento: float | None = None
    score_qualidade: float | None = None
    score_estabilidade: float | None = None
    score_presenca: float | None = None
    versao_score: str | None = None
