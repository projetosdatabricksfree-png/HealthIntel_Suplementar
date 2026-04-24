from pydantic import BaseModel

from api.app.schemas.meta import MetaEnvelope


class CnesMunicipioItem(BaseModel):
    competencia: str
    cd_municipio: str
    nm_municipio: str | None = None
    nm_uf: str | None = None
    sg_uf: str | None = None
    regiao: str | None = None
    tipo_unidade: str
    tipo_unidade_desc: str | None = None
    total_estabelecimentos: int
    total_estabelecimentos_vinculo_sus: int | None = None
    total_leitos: int | None = None
    total_leitos_sus: int | None = None
    pct_leitos_sus: float | None = None
    pct_vinculo_sus: float | None = None
    pop_estimada_ibge: int | None = None
    porte_municipio: str | None = None
    versao_dataset: str | None = None


class CnesUfItem(BaseModel):
    competencia: str
    sg_uf: str
    nm_uf: str | None = None
    tipo_unidade: str
    tipo_unidade_desc: str | None = None
    total_estabelecimentos: int
    total_estabelecimentos_vinculo_sus: int | None = None
    total_leitos: int | None = None
    total_leitos_sus: int | None = None
    pct_leitos_sus: float | None = None
    pct_vinculo_sus: float | None = None
    versao_dataset: str | None = None


class CnesResponse(BaseModel):
    dados: list[CnesMunicipioItem] | list[CnesUfItem]
    meta: MetaEnvelope
