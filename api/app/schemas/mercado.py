from pydantic import BaseModel


class UfResponse(BaseModel):
    sg_uf: str
    total_municipios: int | None = None


class MercadoResumoResponse(BaseModel):
    cd_municipio: str
    nm_municipio: str
    sg_uf: str
    nm_regiao: str | None = None
    segmento: str | None = None
    competencia: str
    operadora_id: int
    registro_ans: str
    nome: str | None = None
    nome_fantasia: str | None = None
    modalidade: str | None = None
    uf_sede: str | None = None
    beneficiario_total: int | None = None
    market_share_pct: float | None = None
    hhi_municipio: float | None = None
    versao_dataset: str | None = None


class VazioAssistencialResponse(BaseModel):
    cd_municipio: str
    nm_municipio: str
    sg_uf: str
    nm_regiao: str | None = None
    competencia: str
    segmento: str
    qt_operadora_presente: int | None = None
    qt_operadora_sem_cobertura: int | None = None
    qt_operadora_total: int | None = None
    pct_operadoras_com_cobertura: float | None = None
    pct_operadoras_sem_cobertura: float | None = None
    vazio_total: bool = False
    vazio_parcial: bool = False
    versao_dataset: str | None = None
