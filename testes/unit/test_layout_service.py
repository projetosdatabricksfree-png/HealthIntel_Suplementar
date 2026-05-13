import pytest

from mongo_layout_service.app.schemas.layout import (
    ColunaLayout,
    LayoutAliasCreate,
    LayoutCreate,
    LayoutRascunhoRequest,
    LayoutVersaoCreate,
    StatusLayoutUpdateRequest,
    ValidacaoArquivoRequest,
)
from mongo_layout_service.app.services.layout_service import LayoutService

pytestmark = pytest.mark.asyncio


class FakeRepository:
    def __init__(self) -> None:
        self.datasets = {}
        self.layouts = {}
        self.versoes = {}
        self.aliases = {}
        self.execucoes = []
        self.eventos = []

    async def ensure_indexes(self) -> None:
        return None

    async def upsert_dataset(self, payload):
        doc = payload.model_dump() | {"criado_em": "agora", "atualizado_em": "agora"}
        self.datasets[payload.dataset_codigo] = doc
        return doc

    async def obter_dataset(self, dataset_codigo):
        return self.datasets.get(dataset_codigo)

    async def listar_datasets(self):
        return list(self.datasets.values())

    async def criar_layout(self, payload):
        layout_id = f"layout_{payload.dataset_codigo}_{payload.formato_esperado}".lower()
        doc = payload.model_dump() | {
            "layout_id": layout_id,
            "status": "rascunho",
            "criado_em": "agora",
            "atualizado_em": "agora",
        }
        self.layouts[layout_id] = doc
        return doc

    async def listar_layouts(self, dataset_codigo=None):
        itens = list(self.layouts.values())
        if dataset_codigo:
            itens = [item for item in itens if item["dataset_codigo"] == dataset_codigo]
        return itens

    async def obter_layout(self, layout_id):
        return self.layouts.get(layout_id)

    async def criar_versao(self, layout_id, payload, assinatura_colunas):
        doc = {
            "layout_id": layout_id,
            "layout_versao_id": f"{layout_id}:{payload.versao}",
            "versao": payload.versao,
            "colunas": [coluna.model_dump() for coluna in payload.colunas],
            "assinatura_colunas": assinatura_colunas,
            "vigencia_inicio": payload.vigencia_inicio,
            "vigencia_fim": payload.vigencia_fim,
            "status": "em_validacao",
            "criado_em": "agora",
            "atualizado_em": "agora",
        }
        self.versoes.setdefault(layout_id, []).append(doc)
        return doc

    async def listar_versoes(self, layout_id, statuses=None):
        itens = self.versoes.get(layout_id, [])
        if statuses:
            itens = [item for item in itens if item["status"] in statuses]
        return itens

    async def criar_alias(self, layout_id, payload, nome_normalizado):
        doc = payload.model_dump() | {
            "layout_id": layout_id,
            "nome_fisico_normalizado": nome_normalizado,
            "criado_em": "agora",
            "atualizado_em": "agora",
        }
        self.aliases.setdefault(layout_id, []).append(doc)
        return doc

    async def listar_aliases(self, layout_id):
        return self.aliases.get(layout_id, [])

    async def atualizar_status_layout(self, layout_id, status):
        self.layouts[layout_id]["status"] = status
        return self.layouts[layout_id]

    async def atualizar_status_versao(self, layout_versao_id, status):
        layout_id = layout_versao_id.split(":")[0]
        for item in self.versoes.get(layout_id, []):
            if item["layout_versao_id"] == layout_versao_id:
                item["status"] = status
                return item
        return None

    async def obter_versao(self, layout_versao_id):
        layout_id = layout_versao_id.split(":")[0]
        for item in self.versoes.get(layout_id, []):
            if item["layout_versao_id"] == layout_versao_id:
                return item
        return None

    async def registrar_execucao_validacao(self, documento):
        self.execucoes.append(documento)
        return documento

    async def listar_incompativeis(self):
        return [item for item in self.execucoes if not item["compativel"]]

    async def registrar_evento(self, documento):
        self.eventos.append(documento)
        return documento

    async def obter_ultima_versao(self, layout_id):
        itens = self.versoes.get(layout_id, [])
        return itens[-1] if itens else None

    async def listar_layouts_por_status(self, dataset_codigo, statuses):
        return [
            item
            for item in self.layouts.values()
            if item["dataset_codigo"] == dataset_codigo and item["status"] in statuses
        ]

    async def obter_aliases_por_layout(self, layout_id):
        return self.aliases.get(layout_id, [])

    @staticmethod
    def novo_evento_id(prefixo):
        return f"{prefixo}_1"


async def _montar_service() -> tuple[LayoutService, str]:
    repository = FakeRepository()
    service = LayoutService(repository)
    layout = await service.criar_layout(
        LayoutCreate(
            dataset_codigo="cadop",
            nome="Cadastro de Operadoras",
            descricao="Base oficial.",
            tabela_raw_destino="bruto_ans.cadop",
        )
    )
    layout_id = layout["layout_id"]
    versao = await service.criar_versao_layout(
        layout_id,
        LayoutVersaoCreate(
            versao="v1",
            colunas=[
                ColunaLayout(nome_canonico="registro_ans", obrigatorio=True),
                ColunaLayout(nome_canonico="competencia", obrigatorio=True),
            ],
        ),
    )
    await service.criar_alias(
        layout_id,
        LayoutAliasCreate(
            nome_fisico="data_atendimento",
            destino_raw="competencia",
            layout_versao_id=versao["layout_versao_id"],
        ),
    )
    await service.atualizar_status_layout(
        layout_id,
        StatusLayoutUpdateRequest(status="ativo", layout_versao_id=versao["layout_versao_id"]),
    )
    return service, layout_id


async def test_valida_arquivo_compativel_com_alias() -> None:
    service, _ = await _montar_service()
    resultado = await service.validar_arquivo(
        ValidacaoArquivoRequest(
            dataset_codigo="cadop",
            nome_arquivo="cadop_202604.csv",
            colunas_detectadas=["registro_ans", "data_atendimento"],
        )
    )
    assert resultado["compativel"] is True
    assert resultado["layout_versao_id"].endswith(":v1")
    assert any(item["destino_raw"] == "competencia" for item in resultado["colunas_mapeadas"])


async def test_valida_arquivo_incompativel_sem_coluna_obrigatoria() -> None:
    service, _ = await _montar_service()
    resultado = await service.validar_arquivo(
        ValidacaoArquivoRequest(
            dataset_codigo="cadop",
            nome_arquivo="cadop_invalido.csv",
            colunas_detectadas=["registro_ans"],
        )
    )
    assert resultado["compativel"] is False
    assert any("Colunas obrigatorias ausentes" in motivo for motivo in resultado["motivos"])


async def test_criar_rascunho_layout_cria_layout_e_versao_quando_dataset_novo() -> None:
    repository = FakeRepository()
    service = LayoutService(repository)
    resultado = await service.criar_rascunho_layout(
        "dataset_inexistente",
        LayoutRascunhoRequest(
            colunas=["COL_A", "COL_B", "COL_C"],
            nome_arquivo="arquivo_x.csv",
            arquivo_hash="abc123",
            motivo="auto-detector",
        ),
    )
    assert resultado["status"] == "rascunho"
    assert resultado["reaproveitado"] is False
    assert resultado["layout_id"] is not None
    assert resultado["layout_versao_id"] is not None
    layout = repository.layouts[resultado["layout_id"]]
    assert layout["dataset_codigo"] == "dataset_inexistente"


async def test_criar_rascunho_layout_e_idempotente_por_assinatura() -> None:
    repository = FakeRepository()
    service = LayoutService(repository)
    primeiro = await service.criar_rascunho_layout(
        "dataset_x",
        LayoutRascunhoRequest(colunas=["A", "B"], nome_arquivo="x.csv"),
    )
    segundo = await service.criar_rascunho_layout(
        "dataset_x",
        LayoutRascunhoRequest(colunas=["a", "b"], nome_arquivo="y.csv"),
    )
    assert primeiro["assinatura_colunas"] == segundo["assinatura_colunas"]
    assert primeiro["layout_versao_id"] == segundo["layout_versao_id"]
    assert segundo["reaproveitado"] is True


async def test_criar_rascunho_layout_reutiliza_layout_existente() -> None:
    service, layout_id = await _montar_service()
    resultado = await service.criar_rascunho_layout(
        "cadop",
        LayoutRascunhoRequest(
            colunas=["NOVA_COL1", "NOVA_COL2"],
            nome_arquivo="cadop_nova_versao.csv",
        ),
    )
    assert resultado["layout_id"] == layout_id
    assert resultado["status"] == "rascunho"
    assert resultado["reaproveitado"] is False
