from pydantic import BaseModel


class MunicipioResponse(BaseModel):
    cd_municipio: str
    nm_municipio: str
    sg_uf: str
    nm_regiao: str | None = None
    competencia: str
    total_beneficiarios: int | None = None
    oportunidade_score: float | None = None
    hhi_municipio: float | None = None
    cobertura_rede: float | None = None
    versao_dataset: str | None = None


class OportunidadeResponse(BaseModel):
    cd_municipio: str
    nm_municipio: str
    sg_uf: str
    nm_regiao: str | None = None
    competencia: str
    oportunidade_score: float | None = None
    total_beneficiarios: int | None = None
    hhi_municipio: float | None = None
    cobertura_rede: float | None = None
    versao_dataset: str | None = None
