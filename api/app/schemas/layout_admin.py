from pydantic import BaseModel, Field


class LayoutColunaCreate(BaseModel):
    nome_canonico: str
    tipo: str = "string"
    obrigatorio: bool = False
    descricao: str | None = None


class LayoutAliasCreate(BaseModel):
    nome_fisico: str
    destino_raw: str
    obrigatorio: bool = False
    layout_versao_id: str | None = None
    regra_transformacao: str = "identity"
    ativo: bool = True


class LayoutVersaoCreate(BaseModel):
    versao: str
    colunas: list[LayoutColunaCreate]
    assinatura_colunas: str | None = None
    vigencia_inicio: str | None = None
    vigencia_fim: str | None = None


class LayoutCreate(BaseModel):
    dataset_codigo: str = Field(..., description="Identificador canonico do dataset.")
    nome: str
    descricao: str
    tabela_raw_destino: str
    formato_esperado: str = "csv"
    delimitador: str = ";"


class LayoutValidacaoArquivoRequest(BaseModel):
    dataset_codigo: str
    colunas_detectadas: list[str]
    nome_arquivo: str


class LayoutStatusUpdateRequest(BaseModel):
    status: str
    layout_versao_id: str | None = None
    motivo: str | None = None


class LayoutReprocessamentoRequest(BaseModel):
    layout_id: str
    layout_versao_id: str | None = None
    motivo: str
    arquivo_origem: str | None = None
    lote_ids: list[str] = Field(default_factory=list)
