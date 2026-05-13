from typing import Literal

from pydantic import BaseModel, Field

EstadoLayout = Literal["rascunho", "em_validacao", "ativo", "depreciado", "inativo", "rejeitado"]


class FonteDatasetCreate(BaseModel):
    dataset_codigo: str
    nome: str
    descricao: str
    formato_esperado: str = "csv"
    tabela_raw_destino: str


class FonteDataset(FonteDatasetCreate):
    criado_em: str | None = None
    atualizado_em: str | None = None


class LayoutCreate(BaseModel):
    dataset_codigo: str = Field(..., description="Identificador canonico do dataset.")
    nome: str
    descricao: str
    tabela_raw_destino: str
    formato_esperado: str = "csv"
    delimitador: str = ";"


class ColunaLayout(BaseModel):
    nome_canonico: str
    tipo: str = "string"
    obrigatorio: bool = False
    descricao: str | None = None


class LayoutVersaoCreate(BaseModel):
    versao: str
    colunas: list[ColunaLayout]
    assinatura_colunas: str | None = None
    vigencia_inicio: str | None = None
    vigencia_fim: str | None = None


class LayoutVersaoDocumento(LayoutVersaoCreate):
    layout_id: str
    layout_versao_id: str
    status: EstadoLayout = Field(default="em_validacao")
    criado_em: str | None = None
    atualizado_em: str | None = None


class LayoutAliasCreate(BaseModel):
    nome_fisico: str
    destino_raw: str
    obrigatorio: bool = False
    layout_versao_id: str | None = None
    regra_transformacao: str = "identity"
    ativo: bool = True


class LayoutAliasDocumento(LayoutAliasCreate):
    layout_id: str
    nome_fisico_normalizado: str
    criado_em: str | None = None
    atualizado_em: str | None = None


class LayoutDocumento(BaseModel):
    layout_id: str
    dataset_codigo: str
    nome: str
    descricao: str
    tabela_raw_destino: str
    formato_esperado: str = "csv"
    delimitador: str = ";"
    status: EstadoLayout = "rascunho"
    criado_em: str | None = None
    atualizado_em: str | None = None


class ValidacaoArquivoRequest(BaseModel):
    dataset_codigo: str
    colunas_detectadas: list[str]
    nome_arquivo: str


class ValidacaoArquivoResponse(BaseModel):
    dataset_codigo: str
    nome_arquivo: str
    assinatura_detectada: str
    compativel: bool
    layout_id: str | None = None
    layout_versao_id: str | None = None
    motivos: list[str] = Field(default_factory=list)
    colunas_mapeadas: list[dict] = Field(default_factory=list)


class StatusLayoutUpdateRequest(BaseModel):
    status: EstadoLayout
    layout_versao_id: str | None = None
    motivo: str | None = None


class ReprocessamentoRequest(BaseModel):
    layout_id: str
    layout_versao_id: str | None = None
    motivo: str
    arquivo_origem: str | None = None
    lote_ids: list[str] = Field(default_factory=list)


class LayoutRascunhoRequest(BaseModel):
    """Sprint 43 — auto-detector: cria layout/versão em estado `rascunho`.

    Usado pelo `ingestao/app/layout_autodetect.py` quando a assinatura de
    colunas detectada em um arquivo ANS não bate com nenhum layout ativo do
    dataset. Cria automaticamente um rascunho aguardando revisão humana,
    sem bloquear a ingestão.
    """

    colunas: list[str] = Field(..., description="Colunas físicas detectadas no arquivo.")
    nome_arquivo: str | None = None
    arquivo_hash: str | None = None
    nome_layout: str | None = Field(
        default=None,
        description="Nome amigável (opcional). Default: f'rascunho-{dataset}-{ts}'.",
    )
    tabela_raw_destino: str | None = Field(
        default=None,
        description="Tabela bruto destino (opcional). Default: f'bruto_ans.{dataset}'.",
    )
    formato_esperado: str = "csv"
    delimitador: str = ";"
    motivo: str | None = Field(
        default=None,
        description="Motivo do rascunho (ex: 'assinatura desconhecida via auto-detector').",
    )
