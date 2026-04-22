from datetime import UTC, datetime
from uuid import uuid4

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError

from mongo_layout_service.app.core.exceptions import LayoutRegistryError
from mongo_layout_service.app.schemas.layout import (
    FonteDatasetCreate,
    LayoutAliasCreate,
    LayoutCreate,
    LayoutVersaoCreate,
)


class LayoutRepository:
    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        self.database = database
        self.datasets = database["fonte_dataset"]
        self.layouts = database["layout"]
        self.layout_versoes = database["layout_versao"]
        self.layout_aliases = database["layout_alias"]
        self.layout_execucoes = database["layout_execucao"]
        self.layout_eventos = database["evento_layout"]

    async def ensure_indexes(self) -> None:
        await self.datasets.create_index([("dataset_codigo", ASCENDING)], unique=True)
        await self.layouts.create_index([("layout_id", ASCENDING)], unique=True)
        await self.layouts.create_index([("dataset_codigo", ASCENDING), ("status", ASCENDING)])
        await self.layout_versoes.create_index([("layout_versao_id", ASCENDING)], unique=True)
        await self.layout_versoes.create_index(
            [("layout_id", ASCENDING), ("versao", ASCENDING)], unique=True
        )
        await self.layout_aliases.create_index(
            [
                ("layout_id", ASCENDING),
                ("nome_fisico_normalizado", ASCENDING),
                ("layout_versao_id", ASCENDING),
            ],
            unique=True,
        )
        await self.layout_execucoes.create_index(
            [("compativel", ASCENDING), ("executado_em", DESCENDING)]
        )
        await self.layout_eventos.create_index(
            [("layout_id", ASCENDING), ("criado_em", DESCENDING)]
        )

    async def upsert_dataset(self, payload: FonteDatasetCreate) -> dict:
        timestamp = self._agora()
        documento = payload.model_dump()
        await self.datasets.update_one(
            {"dataset_codigo": payload.dataset_codigo},
            {
                "$set": {**documento, "atualizado_em": timestamp},
                "$setOnInsert": {"criado_em": timestamp},
            },
            upsert=True,
        )
        dataset = await self.obter_dataset(payload.dataset_codigo)
        if not dataset:
            raise LayoutRegistryError(
                "Falha ao persistir dataset.", status_code=500, code="DATASET_PERSIST_FAIL"
            )
        return dataset

    async def obter_dataset(self, dataset_codigo: str) -> dict | None:
        return await self.datasets.find_one({"dataset_codigo": dataset_codigo}, {"_id": 0})

    async def listar_datasets(self) -> list[dict]:
        cursor = self.datasets.find({}, {"_id": 0}).sort("dataset_codigo", ASCENDING)
        return await cursor.to_list(length=500)

    async def criar_layout(self, payload: LayoutCreate) -> dict:
        timestamp = self._agora()
        layout_id = f"layout_{payload.dataset_codigo}_{payload.formato_esperado}".lower()
        documento = {
            "layout_id": layout_id,
            **payload.model_dump(),
            "status": "rascunho",
            "criado_em": timestamp,
            "atualizado_em": timestamp,
        }
        try:
            await self.layouts.insert_one(documento)
        except DuplicateKeyError as exc:
            raise LayoutRegistryError(
                f"Layout `{layout_id}` ja cadastrado.", status_code=409, code="LAYOUT_DUPLICADO"
            ) from exc
        return documento

    async def listar_layouts(self, dataset_codigo: str | None = None) -> list[dict]:
        filtro: dict = {}
        if dataset_codigo:
            filtro["dataset_codigo"] = dataset_codigo
        cursor = self.layouts.find(filtro, {"_id": 0}).sort("layout_id", ASCENDING)
        return await cursor.to_list(length=500)

    async def obter_layout(self, layout_id: str) -> dict | None:
        return await self.layouts.find_one({"layout_id": layout_id}, {"_id": 0})

    async def criar_versao(
        self, layout_id: str, payload: LayoutVersaoCreate, assinatura_colunas: str
    ) -> dict:
        timestamp = self._agora()
        documento = {
            "layout_id": layout_id,
            "layout_versao_id": f"{layout_id}:{payload.versao}",
            "versao": payload.versao,
            "colunas": [coluna.model_dump() for coluna in payload.colunas],
            "assinatura_colunas": assinatura_colunas,
            "vigencia_inicio": payload.vigencia_inicio,
            "vigencia_fim": payload.vigencia_fim,
            "status": "em_validacao",
            "criado_em": timestamp,
            "atualizado_em": timestamp,
        }
        try:
            await self.layout_versoes.insert_one(documento)
        except DuplicateKeyError as exc:
            raise LayoutRegistryError(
                f"Versao `{payload.versao}` ja cadastrada para `{layout_id}`.",
                status_code=409,
                code="LAYOUT_VERSAO_DUPLICADA",
            ) from exc
        return documento

    async def listar_versoes(self, layout_id: str, statuses: list[str] | None = None) -> list[dict]:
        filtro: dict = {"layout_id": layout_id}
        if statuses:
            filtro["status"] = {"$in": statuses}
        cursor = self.layout_versoes.find(filtro, {"_id": 0}).sort("criado_em", DESCENDING)
        return await cursor.to_list(length=500)

    async def criar_alias(
        self, layout_id: str, payload: LayoutAliasCreate, nome_normalizado: str
    ) -> dict:
        existente = await self.layout_aliases.find_one(
            {
                "layout_id": layout_id,
                "nome_fisico_normalizado": nome_normalizado,
                "layout_versao_id": payload.layout_versao_id,
            },
            {"_id": 0},
        )
        if existente and existente["destino_raw"] != payload.destino_raw:
            raise LayoutRegistryError(
                "Alias ja cadastrado com destino_raw diferente.",
                status_code=409,
                code="ALIAS_CONFLITO",
            )

        timestamp = self._agora()
        documento = {
            "layout_id": layout_id,
            **payload.model_dump(),
            "nome_fisico_normalizado": nome_normalizado,
            "criado_em": timestamp,
            "atualizado_em": timestamp,
        }
        if existente:
            await self.layout_aliases.update_one(
                {
                    "layout_id": layout_id,
                    "nome_fisico_normalizado": nome_normalizado,
                    "layout_versao_id": payload.layout_versao_id,
                },
                {"$set": documento},
            )
            return documento

        try:
            await self.layout_aliases.insert_one(documento)
        except DuplicateKeyError as exc:
            raise LayoutRegistryError(
                "Alias duplicado.", status_code=409, code="ALIAS_DUPLICADO"
            ) from exc
        return documento

    async def listar_aliases(self, layout_id: str) -> list[dict]:
        cursor = self.layout_aliases.find({"layout_id": layout_id}, {"_id": 0}).sort(
            "nome_fisico_normalizado", ASCENDING
        )
        return await cursor.to_list(length=1000)

    async def atualizar_status_layout(self, layout_id: str, status: str) -> dict:
        timestamp = self._agora()
        await self.layouts.update_one(
            {"layout_id": layout_id}, {"$set": {"status": status, "atualizado_em": timestamp}}
        )
        layout = await self.obter_layout(layout_id)
        if not layout:
            raise LayoutRegistryError(
                "Layout nao encontrado.", status_code=404, code="LAYOUT_NAO_ENCONTRADO"
            )
        return layout

    async def atualizar_status_versao(self, layout_versao_id: str, status: str) -> dict | None:
        timestamp = self._agora()
        await self.layout_versoes.update_one(
            {"layout_versao_id": layout_versao_id},
            {"$set": {"status": status, "atualizado_em": timestamp}},
        )
        return await self.layout_versoes.find_one(
            {"layout_versao_id": layout_versao_id}, {"_id": 0}
        )

    async def obter_versao(self, layout_versao_id: str) -> dict | None:
        return await self.layout_versoes.find_one(
            {"layout_versao_id": layout_versao_id}, {"_id": 0}
        )

    async def registrar_execucao_validacao(self, documento: dict) -> dict:
        await self.layout_execucoes.insert_one(documento)
        return documento

    async def listar_incompativeis(self) -> list[dict]:
        cursor = self.layout_execucoes.find({"compativel": False}, {"_id": 0}).sort(
            "executado_em", DESCENDING
        )
        return await cursor.to_list(length=200)

    async def registrar_evento(self, documento: dict) -> dict:
        await self.layout_eventos.insert_one(documento)
        return documento

    async def obter_ultima_versao(self, layout_id: str) -> dict | None:
        cursor = (
            self.layout_versoes.find({"layout_id": layout_id}, {"_id": 0})
            .sort("criado_em", DESCENDING)
            .limit(1)
        )
        itens = await cursor.to_list(length=1)
        return itens[0] if itens else None

    async def listar_layouts_por_status(
        self, dataset_codigo: str, statuses: list[str]
    ) -> list[dict]:
        cursor = self.layouts.find(
            {"dataset_codigo": dataset_codigo, "status": {"$in": statuses}},
            {"_id": 0},
        ).sort("layout_id", ASCENDING)
        return await cursor.to_list(length=200)

    async def obter_aliases_por_layout(self, layout_id: str) -> list[dict]:
        return await self.listar_aliases(layout_id)

    @staticmethod
    def novo_evento_id(prefixo: str) -> str:
        return f"{prefixo}_{uuid4().hex}"

    @staticmethod
    def _agora() -> str:
        return datetime.now(tz=UTC).isoformat()
