from datetime import date

from pydantic import BaseModel


class ProdutoPlanoItem(BaseModel):
    registro_ans: str
    codigo_produto: str | None = None
    nome_produto: str | None = None
    segmentacao: str | None = None
    tipo_contratacao: str | None = None
    abrangencia_geografica: str | None = None
    modalidade: str | None = None
    uf_comercializacao: str | None = None
    competencia: int | None = None
    situacao_plano: str | None = None
    data_situacao: date | None = None


class HistoricoPlanoItem(BaseModel):
    registro_ans: str
    codigo_plano: str | None = None
    nome_plano: str | None = None
    situacao: str | None = None
    data_situacao: date | None = None
    segmentacao: str | None = None
    tipo_contratacao: str | None = None
    abrangencia_geografica: str | None = None
    uf: str | None = None
    competencia: int | None = None


class RegulatorioItem(BaseModel):
    trimestre: str
    registro_ans: str
    razao_social: str | None = None
    modalidade: str | None = None
    qtd_reclamacoes: int | None = None
    indice_reclamacao: float | None = None
    demandas_nip: int | None = None
    taxa_resolutividade: float | None = None
    nivel_alerta: str | None = None
    tendencia_regulatoria: str | None = None


class IgrItem(BaseModel):
    trimestre: str
    registro_ans: str
    modalidade: str | None = None
    porte: str | None = None
    total_reclamacoes: int | None = None
    beneficiarios: int | None = None
    igr: float | None = None
    meta_igr: float | None = None
    atingiu_meta: bool | None = None


class NipItem(BaseModel):
    trimestre: str
    registro_ans: str
    modalidade: str | None = None
    demandas_nip: int | None = None
    demandas_resolvidas: int | None = None
    beneficiarios: int | None = None
    taxa_intermediacao_resolvida: float | None = None
    taxa_resolutividade: float | None = None


class IdssItem(BaseModel):
    ano_base: int
    registro_ans: str
    idss_total: float | None = None
    idqs: float | None = None
    idga: float | None = None
    idsm: float | None = None
    idgr: float | None = None
    faixa_idss: str | None = None
    versao_metodologia: str | None = None


class FinanceiroItem(BaseModel):
    trimestre: str
    registro_ans: str
    razao_social: str | None = None
    nome_fantasia: str | None = None
    modalidade: str | None = None
    uf: str | None = None
    receita_total: float | None = None
    despesa_total: float | None = None
    resultado_periodo: float | None = None
    resultado_operacional: float | None = None
    patrimonio_liquido: float | None = None
    sinistralidade_bruta: float | None = None
    sinistralidade_liquida: float | None = None
    rating_financeiro: str | None = None
    versao_financeira: str | None = None


class PrudencialItem(BaseModel):
    registro_ans: str
    trimestre: str
    margem_solvencia: float | None = None
    capital_minimo_requerido: float | None = None
    capital_disponivel: float | None = None
    indice_liquidez: float | None = None
    situacao_prudencial: str | None = None
    situacao_inadequada: bool | None = None
    fonte_publicacao: str | None = None
    versao_dataset: str | None = None


class RegimeEspecialItem(BaseModel):
    registro_ans: str
    nome: str | None = None
    modalidade: str | None = None
    uf_sede: str | None = None
    trimestre: str
    trimestre_fim: str | None = None
    tipo_regime: str | None = None
    ativo: bool | None = None
    duracao_trimestres: int | None = None
    data_inicio: date | None = None
    data_fim: date | None = None
    descricao: str | None = None
    versao_dataset: str | None = None


class GlosaItem(BaseModel):
    registro_ans: str
    competencia: int
    tipo_glosa: str | None = None
    qt_glosa: int | None = None
    valor_glosa: float | None = None
    valor_faturado: float | None = None
    taxa_glosa_calculada: float | None = None
    fonte_publicacao: str | None = None
    versao_dataset: str | None = None
