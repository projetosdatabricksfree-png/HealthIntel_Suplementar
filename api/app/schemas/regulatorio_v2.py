from datetime import date

from pydantic import BaseModel


class ScoreRegulatorioResponse(BaseModel):
    operadora_id: int
    registro_ans: str
    nome: str | None = None
    nome_fantasia: str | None = None
    modalidade: str | None = None
    uf_sede: str | None = None
    competencia: str
    score_igr: float | None = None
    score_nip: float | None = None
    score_rn623: float | None = None
    score_prudencial: float | None = None
    score_taxa_resolutividade: float | None = None
    regime_especial_ativo: bool = False
    tipo_regime: str | None = None
    situacao_inadequada: bool = False
    qt_portabilidade_entrada: int | None = None
    qt_portabilidade_saida: int | None = None
    saldo_portabilidade: int | None = None
    score_regulatorio_base: float
    score_regulatorio: float
    rating: str
    versao_regulatoria: str | None = None


class RegimeEspecialResponse(BaseModel):
    operadora_id: int
    registro_ans: str
    nome: str | None = None
    nome_fantasia: str | None = None
    modalidade: str | None = None
    uf_sede: str | None = None
    trimestre: str
    trimestre_fim: str | None = None
    tipo_regime: str
    ativo: bool
    duracao_trimestres: int | None = None
    data_inicio: date
    data_fim: date | None = None
    versao_dataset: str | None = None


class PortabilidadeResponse(BaseModel):
    operadora_id: int
    registro_ans: str
    nome: str | None = None
    nome_fantasia: str | None = None
    modalidade: str | None = None
    uf_sede: str | None = None
    competencia: int
    competencia_data: date | None = None
    modalidade_descricao: str | None = None
    tipo_contratacao: str | None = None
    qt_portabilidade_entrada: int | None = None
    qt_portabilidade_saida: int | None = None
    saldo_portabilidade: int | None = None
    fonte_publicacao: str | None = None
    versao_dataset: str | None = None
