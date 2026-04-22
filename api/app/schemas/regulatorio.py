from pydantic import BaseModel


class OperadoraRegulatorioResponse(BaseModel):
    registro_ans: str
    trimestre: str
    nome: str | None = None
    nome_fantasia: str | None = None
    modalidade: str | None = None
    uf_sede: str | None = None
    igr: float | None = None
    meta_igr: float | None = None
    atingiu_meta_excelencia: bool = False
    demandas_nip: int | None = None
    demandas_resolvidas: int | None = None
    taxa_intermediacao_resolvida: float | None = None
    taxa_resolutividade: float | None = None
    rn623_excelencia: bool = False
    rn623_reducao: bool = False
    faixa_risco_regulatorio: str | None = None
    status_rn623: str | None = None
    versao_regulatoria: str | None = None


class Rn623ListaResponse(BaseModel):
    trimestre: str
    tipo_lista: str
    registro_ans: str
    nome: str | None = None
    nome_fantasia: str | None = None
    modalidade: str | None = None
    uf_sede: str | None = None
    total_nip: int | None = None
    beneficiarios: int | None = None
    igr: float | None = None
    meta_igr: float | None = None
    elegivel: bool = True
    observacao: str | None = None
