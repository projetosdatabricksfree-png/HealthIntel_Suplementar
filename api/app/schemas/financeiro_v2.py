from datetime import date

from pydantic import BaseModel


class FinanceiroOperadoraResponse(BaseModel):
    operadora_id: int
    registro_ans: str
    nome: str | None = None
    nome_fantasia: str | None = None
    modalidade: str | None = None
    uf_sede: str | None = None
    competencia: str
    trimestre_referencia: str | None = None
    ativo_total: float | None = None
    passivo_total: float | None = None
    patrimonio_liquido: float | None = None
    receita_total: float | None = None
    despesa_total: float | None = None
    resultado_periodo: float | None = None
    resultado_operacional: float | None = None
    provisao_tecnica: float | None = None
    margem_solvencia_calculada: float | None = None
    sinistro_total: float | None = None
    contraprestacao_total: float | None = None
    sinistralidade_bruta: float | None = None
    ressarcimento_sus: float | None = None
    evento_indenizavel: float | None = None
    sinistralidade_liquida: float | None = None
    taxa_sinistralidade_calculada: float | None = None
    indice_sinistralidade: float | None = None
    margem_liquida_pct: float | None = None
    cobertura_provisao: float | None = None
    resultado_operacional_bruto: float | None = None
    score_financeiro_base: float | None = None
    rating_financeiro: str | None = None
    vda_valor_devido: float | None = None
    vda_valor_pago: float | None = None
    vda_saldo_devedor: float | None = None
    vda_situacao_cobranca: str | None = None
    vda_inadimplente: bool | None = None
    vda_meses_inadimplente_consecutivos: int | None = None
    vda_data_vencimento: date | None = None
    qt_glosa: float | None = None
    valor_glosa: float | None = None
    valor_faturado: float | None = None
    glosa_taxa_glosa_calculada: float | None = None
    severidade_glosa: str | None = None
    tipos_glosa: str | None = None
    versao_dataset: str | None = None


class ScoreV2OperadoraResponse(BaseModel):
    operadora_id: int
    registro_ans: str
    nome: str | None = None
    nome_fantasia: str | None = None
    modalidade: str | None = None
    uf_sede: str | None = None
    competencia: str
    trimestre_financeiro: str | None = None
    score_core: float
    score_regulatorio: float
    score_financeiro_trimestral: float
    inadimplente: bool = False
    saldo_devedor: float | None = None
    valor_devido: float | None = None
    valor_pago: float | None = None
    situacao_cobranca: str | None = None
    taxa_glosa_calculada: float | None = None
    valor_glosa_total: float | None = None
    valor_faturado_total: float | None = None
    penalizacao_vda: float = 0
    penalizacao_glosa: float = 0
    score_penalizacoes: float
    score_v2_base: float
    score_v2: float
    rating: str
    componentes: dict[str, float]
    versao_metodologia: str | None = None
