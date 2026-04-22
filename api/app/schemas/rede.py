from pydantic import BaseModel


class RedeOperadoraResponse(BaseModel):
    operadora_id: int
    registro_ans: str
    nome: str | None = None
    nome_fantasia: str | None = None
    modalidade: str | None = None
    uf_sede: str | None = None
    competencia: str
    competencia_id: str | None = None
    cd_municipio: str
    nm_municipio: str | None = None
    sg_uf: str | None = None
    nm_regiao: str | None = None
    segmento: str
    pop_estimada_ibge: int | None = None
    porte_municipio: str | None = None
    qt_prestador: int | None = None
    qt_especialidade_disponivel: int | None = None
    beneficiario_total: int | None = None
    qt_prestador_por_10k_beneficiarios: float | None = None
    limiar_prestador_por_10k: float | None = None
    limiar_especialidade_por_10k: float | None = None
    tem_cobertura: bool | None = None
    cobertura_minima_atendida: bool | None = None
    qt_municipio_coberto: int | None = None
    qt_uf_coberto: int | None = None
    pct_municipios_cobertos: float | None = None
    pct_ufs_cobertos: float | None = None
    score_rede: float | None = None
    versao_dataset: str | None = None


class RedeMunicipioResponse(BaseModel):
    operadora_id: int
    registro_ans: str
    nome: str | None = None
    nome_fantasia: str | None = None
    modalidade: str | None = None
    uf_sede: str | None = None
    competencia: str
    competencia_id: str | None = None
    cd_municipio: str
    nm_municipio: str | None = None
    sg_uf: str | None = None
    nm_regiao: str | None = None
    segmento: str
    pop_estimada_ibge: int | None = None
    porte_municipio: str | None = None
    qt_prestador: int | None = None
    qt_especialidade_disponivel: int | None = None
    beneficiario_total: int | None = None
    qt_prestador_por_10k_beneficiarios: float | None = None
    limiar_prestador_por_10k: float | None = None
    limiar_especialidade_por_10k: float | None = None
    tem_cobertura: bool | None = None
    cobertura_minima_atendida: bool | None = None
    qt_municipio_coberto: int | None = None
    qt_uf_coberto: int | None = None
    pct_municipios_cobertos: float | None = None
    pct_ufs_cobertos: float | None = None
    score_rede: float | None = None
    versao_dataset: str | None = None
