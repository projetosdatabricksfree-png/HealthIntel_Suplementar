from pydantic import BaseModel

from api.app.schemas.meta import MetaEnvelope


class TissProcedimentoItem(BaseModel):
    trimestre: str
    operadora_id: int | None = None
    registro_ans: str
    nome: str | None = None
    nome_fantasia: str | None = None
    modalidade_operadora: str | None = None
    uf_sede: str | None = None
    grupo_procedimento: str
    grupo_desc: str | None = None
    subgrupo_procedimento: str | None = None
    qt_procedimentos: int
    qt_beneficiarios_distintos: int | None = None
    valor_total: float
    valor_medio: float | None = None
    pct_do_total_operadora: float | None = None
    rank_por_valor: int | None = None
    versao_dataset: str | None = None


class SinistralProcedimentoItem(BaseModel):
    trimestre: str
    operadora_id: int | None = None
    registro_ans: str
    nome: str | None = None
    nome_fantasia: str | None = None
    modalidade_operadora: str | None = None
    uf_sede: str | None = None
    grupo_procedimento: str
    grupo_desc: str | None = None
    subgrupo_procedimento: str | None = None
    qt_procedimentos: int
    qt_beneficiarios_distintos: int | None = None
    valor_tiss: float
    receita_total: float | None = None
    sinistralidade_grupo_pct: float
    desvio_padrao_sinistralidade: float | None = None
    flag_sinistralidade_alta: bool = False
    rank_sinistralidade: int | None = None
    versao_dataset: str | None = None


class CnesRedeGapItem(BaseModel):
    competencia: str
    cd_municipio: str
    nm_municipio: str | None = None
    nm_uf: str | None = None
    sg_uf: str | None = None
    regiao: str | None = None
    tipo_unidade: str
    tipo_unidade_desc: str | None = None
    estabelecimentos_cnes: int
    prestadores_credenciados: int
    gap_absoluto: int
    gap_pct: float | None = None
    severidade_gap: str
    flag_gap_critico: bool = False
    versao_dataset: str | None = None


class TissResponse(BaseModel):
    dados: list[TissProcedimentoItem] | list[SinistralProcedimentoItem] | list[CnesRedeGapItem]
    meta: MetaEnvelope
