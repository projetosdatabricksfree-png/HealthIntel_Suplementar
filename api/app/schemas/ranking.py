from pydantic import BaseModel


class RankingOperadoraScoreResponse(BaseModel):
    operadora_id: int
    registro_ans: str
    nome: str | None = None
    competencia: str
    score_final: float
    rating: str
    ranking_posicao: int
    versao_score: str | None = None


class RankingCrescimentoResponse(BaseModel):
    operadora_id: int
    registro_ans: str
    nome: str | None = None
    competencia: str
    taxa_crescimento_12m: float | None = None
    beneficiario_atual: int | None = None
    beneficiario_12m_anterior: int | None = None
    ranking_posicao: int


class RankingOportunidadeResponse(BaseModel):
    cd_municipio: str
    nm_municipio: str
    sg_uf: str
    competencia: str
    oportunidade_score: float
    ranking_posicao: int


class RankingOportunidadeV2Response(BaseModel):
    cd_municipio: str
    nm_municipio: str
    sg_uf: str
    nm_regiao: str | None = None
    competencia: str
    total_beneficiarios: int | None = None
    hhi_municipio: float | None = None
    cobertura_media_pct: float | None = None
    cobertura_rede: float | None = None
    oportunidade_score_v1: float | None = None
    qt_operadoras_cobertura: int | None = None
    qt_segmentos_cobertos: int | None = None
    qt_segmentos_vazios: int | None = None
    qt_segmentos_parciais: int | None = None
    pct_operadoras_com_cobertura: float | None = None
    pct_operadoras_sem_cobertura: float | None = None
    vazio_assistencial_presente: bool = False
    operadora_melhor_score_v2: str | None = None
    score_v2_maximo: float | None = None
    score_oportunidade_rede: float | None = None
    score_sip: float | None = None
    oportunidade_v2_score: float
    ranking_posicao: int
    sinal_vazio: str | None = None
    versao_algoritmo: str | None = None


class RankingCompostoResponse(BaseModel):
    operadora_id: int
    competencia_id: str
    registro_ans: str
    nome: str | None = None
    nome_fantasia: str | None = None
    modalidade: str | None = None
    uf_sede: str | None = None
    score_v3_final: float
    posicao_geral: int
    posicao_por_modalidade: int
    variacao_posicao_3m: int | None = None
    versao_metodologia: str | None = None
