from datetime import UTC, datetime
from hashlib import sha256

from mongo_layout_service.app.core.exceptions import LayoutRegistryError
from mongo_layout_service.app.repositories.layout_repository import LayoutRepository
from mongo_layout_service.app.schemas.layout import (
    ColunaLayout,
    FonteDatasetCreate,
    LayoutAliasCreate,
    LayoutCreate,
    LayoutRascunhoRequest,
    LayoutVersaoCreate,
    ReprocessamentoRequest,
    StatusLayoutUpdateRequest,
    ValidacaoArquivoRequest,
)


class LayoutService:
    def __init__(self, repository: LayoutRepository) -> None:
        self.repository = repository

    async def inicializar(self) -> None:
        await self.repository.ensure_indexes()

    async def listar_datasets(self) -> list[dict]:
        return await self.repository.listar_datasets()

    async def criar_layout(self, payload: LayoutCreate) -> dict:
        await self.repository.upsert_dataset(
            FonteDatasetCreate(
                dataset_codigo=payload.dataset_codigo,
                nome=payload.nome,
                descricao=payload.descricao,
                formato_esperado=payload.formato_esperado,
                tabela_raw_destino=payload.tabela_raw_destino,
            )
        )
        layout = await self.repository.criar_layout(payload)
        await self.repository.registrar_evento(
            {
                "evento_id": self.repository.novo_evento_id("layout"),
                "layout_id": layout["layout_id"],
                "tipo_evento": "layout_criado",
                "criado_em": self._agora(),
            }
        )
        return layout

    async def listar_layouts(self, dataset_codigo: str | None = None) -> list[dict]:
        return await self.repository.listar_layouts(dataset_codigo=dataset_codigo)

    async def obter_layout(self, layout_id: str) -> dict:
        layout = await self.repository.obter_layout(layout_id)
        if not layout:
            raise LayoutRegistryError(
                "Layout nao encontrado.", status_code=404, code="LAYOUT_NAO_ENCONTRADO"
            )
        layout["versoes"] = await self.repository.listar_versoes(layout_id)
        layout["aliases"] = await self.repository.listar_aliases(layout_id)
        return layout

    async def listar_versoes(self, layout_id: str) -> list[dict]:
        if not await self.repository.obter_layout(layout_id):
            raise LayoutRegistryError(
                "Layout nao encontrado.", status_code=404, code="LAYOUT_NAO_ENCONTRADO"
            )
        return await self.repository.listar_versoes(layout_id)

    async def criar_versao_layout(self, layout_id: str, payload: LayoutVersaoCreate) -> dict:
        if not await self.repository.obter_layout(layout_id):
            raise LayoutRegistryError(
                "Layout nao encontrado.", status_code=404, code="LAYOUT_NAO_ENCONTRADO"
            )
        assinatura = payload.assinatura_colunas or self._assinar_colunas(payload.colunas)
        versao = await self.repository.criar_versao(layout_id, payload, assinatura)
        await self.repository.registrar_evento(
            {
                "evento_id": self.repository.novo_evento_id("versao"),
                "layout_id": layout_id,
                "layout_versao_id": versao["layout_versao_id"],
                "tipo_evento": "versao_criada",
                "criado_em": self._agora(),
            }
        )
        return versao

    async def criar_alias(self, layout_id: str, payload: LayoutAliasCreate) -> dict:
        if not await self.repository.obter_layout(layout_id):
            raise LayoutRegistryError(
                "Layout nao encontrado.", status_code=404, code="LAYOUT_NAO_ENCONTRADO"
            )
        if payload.layout_versao_id and not await self.repository.obter_versao(
            payload.layout_versao_id
        ):
            raise LayoutRegistryError(
                "Versao de layout nao encontrada.",
                status_code=404,
                code="LAYOUT_VERSAO_NAO_ENCONTRADA",
            )
        nome_normalizado = self._normalizar_coluna(payload.nome_fisico)
        alias = await self.repository.criar_alias(layout_id, payload, nome_normalizado)
        await self.repository.registrar_evento(
            {
                "evento_id": self.repository.novo_evento_id("alias"),
                "layout_id": layout_id,
                "layout_versao_id": payload.layout_versao_id,
                "tipo_evento": "alias_criado",
                "criado_em": self._agora(),
            }
        )
        return alias

    async def atualizar_status_layout(
        self, layout_id: str, payload: StatusLayoutUpdateRequest
    ) -> dict:
        layout = await self.repository.obter_layout(layout_id)
        if not layout:
            raise LayoutRegistryError(
                "Layout nao encontrado.", status_code=404, code="LAYOUT_NAO_ENCONTRADO"
            )
        atualizado = await self.repository.atualizar_status_layout(layout_id, payload.status)
        versao_id = payload.layout_versao_id
        if payload.status == "ativo" and not versao_id:
            ultima_versao = await self.repository.obter_ultima_versao(layout_id)
            versao_id = ultima_versao["layout_versao_id"] if ultima_versao else None
        if versao_id:
            versao = await self.repository.atualizar_status_versao(versao_id, payload.status)
            if not versao:
                raise LayoutRegistryError(
                    "Versao de layout nao encontrada.",
                    status_code=404,
                    code="LAYOUT_VERSAO_NAO_ENCONTRADA",
                )
            atualizado["layout_versao_id"] = versao_id
        await self.repository.registrar_evento(
            {
                "evento_id": self.repository.novo_evento_id("status"),
                "layout_id": layout_id,
                "layout_versao_id": versao_id,
                "tipo_evento": "status_atualizado",
                "status": payload.status,
                "motivo": payload.motivo,
                "criado_em": self._agora(),
            }
        )
        return atualizado

    async def criar_rascunho_layout(
        self, dataset_codigo: str, payload: LayoutRascunhoRequest
    ) -> dict:
        """Sprint 43 — cria layout+versão em estado `rascunho` a partir de
        colunas físicas detectadas. Idempotente por assinatura: se já existir
        uma versão rascunho com a mesma assinatura, retorna a existente.

        Procura primeiro um Layout ativo do dataset; se não houver, cria.
        """
        assinatura = self._assinar_colunas_fisicas(payload.colunas)
        layouts_existentes = await self.repository.listar_layouts(
            dataset_codigo=dataset_codigo
        )

        layout = None
        if layouts_existentes:
            layout = layouts_existentes[0]
        else:
            tabela_raw = (
                payload.tabela_raw_destino or f"bruto_ans.{dataset_codigo}"
            )
            nome = payload.nome_layout or f"rascunho-{dataset_codigo}"
            layout = await self.repository.criar_layout(
                LayoutCreate(
                    dataset_codigo=dataset_codigo,
                    nome=nome,
                    descricao=(
                        f"Rascunho criado por auto-detector (Sprint 43): "
                        f"{payload.motivo or 'assinatura desconhecida'}"
                    ),
                    tabela_raw_destino=tabela_raw,
                    formato_esperado=payload.formato_esperado,
                    delimitador=payload.delimitador,
                )
            )
            await self.repository.registrar_evento(
                {
                    "evento_id": self.repository.novo_evento_id("layout"),
                    "layout_id": layout["layout_id"],
                    "tipo_evento": "layout_criado",
                    "origem": "auto_detector_sprint43",
                    "criado_em": self._agora(),
                }
            )

        for versao_existente in await self.repository.listar_versoes(layout["layout_id"]):
            if versao_existente.get("assinatura_colunas") == assinatura:
                return {
                    "layout_id": layout["layout_id"],
                    "layout_versao_id": versao_existente["layout_versao_id"],
                    "status": versao_existente.get("status"),
                    "assinatura_colunas": assinatura,
                    "reaproveitado": True,
                }

        colunas_layout = [
            ColunaLayout(nome_canonico=self._normalizar_coluna(c), tipo="string")
            for c in payload.colunas
        ]
        timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
        versao = await self.repository.criar_versao(
            layout["layout_id"],
            LayoutVersaoCreate(
                versao=f"rascunho-{timestamp}",
                colunas=colunas_layout,
                assinatura_colunas=assinatura,
            ),
            assinatura,
        )
        # Marca versão como rascunho (default é em_validacao)
        await self.repository.atualizar_status_versao(versao["layout_versao_id"], "rascunho")
        await self.repository.registrar_evento(
            {
                "evento_id": self.repository.novo_evento_id("versao"),
                "layout_id": layout["layout_id"],
                "layout_versao_id": versao["layout_versao_id"],
                "tipo_evento": "rascunho_criado",
                "origem": "auto_detector_sprint43",
                "nome_arquivo": payload.nome_arquivo,
                "arquivo_hash": payload.arquivo_hash,
                "assinatura_colunas": assinatura,
                "criado_em": self._agora(),
            }
        )
        return {
            "layout_id": layout["layout_id"],
            "layout_versao_id": versao["layout_versao_id"],
            "status": "rascunho",
            "assinatura_colunas": assinatura,
            "reaproveitado": False,
        }

    async def listar_incompativeis(self) -> list[dict]:
        return await self.repository.listar_incompativeis()

    async def reprocessar(self, payload: ReprocessamentoRequest) -> dict:
        if not await self.repository.obter_layout(payload.layout_id):
            raise LayoutRegistryError(
                "Layout nao encontrado.", status_code=404, code="LAYOUT_NAO_ENCONTRADO"
            )
        evento = {
            "evento_id": self.repository.novo_evento_id("reprocessamento"),
            "layout_id": payload.layout_id,
            "layout_versao_id": payload.layout_versao_id,
            "tipo_evento": "reprocessamento_solicitado",
            "motivo": payload.motivo,
            "arquivo_origem": payload.arquivo_origem,
            "lote_ids": payload.lote_ids,
            "criado_em": self._agora(),
        }
        await self.repository.registrar_evento(evento)
        return {"status": "agendado", **evento}

    async def validar_arquivo(self, payload: ValidacaoArquivoRequest) -> dict:
        assinatura = self._assinar_colunas_fisicas(payload.colunas_detectadas)
        candidatos = await self.repository.listar_layouts_por_status(
            payload.dataset_codigo,
            ["ativo", "em_validacao", "rascunho", "depreciado"],
        )
        if not candidatos:
            return await self._registrar_execucao_validacao(
                payload=payload,
                assinatura=assinatura,
                resultado={
                    "dataset_codigo": payload.dataset_codigo,
                    "nome_arquivo": payload.nome_arquivo,
                    "assinatura_detectada": assinatura,
                    "compativel": False,
                    "layout_id": None,
                    "layout_versao_id": None,
                    "motivos": ["Nenhum layout cadastrado para o dataset."],
                    "colunas_mapeadas": [],
                },
            )

        melhor_resultado: dict | None = None
        melhor_score = -10_000
        for layout in candidatos:
            aliases = await self.repository.obter_aliases_por_layout(layout["layout_id"])
            versoes = await self.repository.listar_versoes(
                layout["layout_id"],
                statuses=["ativo", "em_validacao", "rascunho", "depreciado"],
            )
            for versao in versoes:
                resultado = self._avaliar_compatibilidade(layout, versao, aliases, payload)
                if resultado["score"] > melhor_score:
                    melhor_score = resultado["score"]
                    melhor_resultado = resultado

        if not melhor_resultado:
            melhor_resultado = {
                "dataset_codigo": payload.dataset_codigo,
                "nome_arquivo": payload.nome_arquivo,
                "assinatura_detectada": assinatura,
                "compativel": False,
                "layout_id": None,
                "layout_versao_id": None,
                "motivos": ["Nenhuma versao cadastrada para o dataset."],
                "colunas_mapeadas": [],
                "score": -999,
            }

        melhor_resultado.pop("score", None)
        return await self._registrar_execucao_validacao(
            payload=payload, assinatura=assinatura, resultado=melhor_resultado
        )

    def _avaliar_compatibilidade(
        self, layout: dict, versao: dict, aliases: list[dict], payload: ValidacaoArquivoRequest
    ) -> dict:
        aliases_validos = {
            alias["nome_fisico_normalizado"]: alias
            for alias in aliases
            if alias.get("ativo", True)
            and alias.get("layout_versao_id") in (None, versao["layout_versao_id"])
        }
        colunas_canonicas = {
            self._normalizar_coluna(coluna["nome_canonico"]): coluna
            for coluna in versao.get("colunas", [])
        }
        mapeadas: list[dict] = []
        nao_mapeadas: list[str] = []
        destinos_resolvidos: set[str] = set()

        for coluna in payload.colunas_detectadas:
            coluna_normalizada = self._normalizar_coluna(coluna)
            alias = aliases_validos.get(coluna_normalizada)
            if alias:
                destino = alias["destino_raw"]
                mapeadas.append({"origem": coluna, "destino_raw": destino, "via": "alias"})
                destinos_resolvidos.add(destino)
                continue
            if coluna_normalizada in colunas_canonicas:
                mapeadas.append(
                    {"origem": coluna, "destino_raw": coluna_normalizada, "via": "canonico"}
                )
                destinos_resolvidos.add(coluna_normalizada)
                continue
            nao_mapeadas.append(coluna)

        obrigatorias = {
            self._normalizar_coluna(coluna["nome_canonico"])
            for coluna in versao.get("colunas", [])
            if coluna.get("obrigatorio")
        }
        faltantes = sorted(obrigatorias - destinos_resolvidos)
        motivos: list[str] = []
        if nao_mapeadas:
            motivos.append(f"Colunas sem mapeamento: {', '.join(sorted(nao_mapeadas))}.")
        if faltantes:
            motivos.append(f"Colunas obrigatorias ausentes: {', '.join(faltantes)}.")
        compativel = not nao_mapeadas and not faltantes
        score = (len(mapeadas) * 10) - (len(nao_mapeadas) * 8) - (len(faltantes) * 12)
        return {
            "dataset_codigo": payload.dataset_codigo,
            "nome_arquivo": payload.nome_arquivo,
            "assinatura_detectada": self._assinar_colunas_fisicas(payload.colunas_detectadas),
            "compativel": compativel,
            "layout_id": layout["layout_id"],
            "layout_versao_id": versao["layout_versao_id"],
            "motivos": motivos,
            "colunas_mapeadas": mapeadas,
            "score": score,
        }

    async def _registrar_execucao_validacao(
        self, payload: ValidacaoArquivoRequest, assinatura: str, resultado: dict
    ) -> dict:
        documento = {
            "execucao_id": self.repository.novo_evento_id("exec"),
            "dataset_codigo": payload.dataset_codigo,
            "nome_arquivo": payload.nome_arquivo,
            "assinatura_detectada": assinatura,
            "colunas_detectadas": payload.colunas_detectadas,
            "compativel": resultado["compativel"],
            "layout_id": resultado.get("layout_id"),
            "layout_versao_id": resultado.get("layout_versao_id"),
            "motivos": resultado.get("motivos", []),
            "colunas_mapeadas": resultado.get("colunas_mapeadas", []),
            "executado_em": self._agora(),
        }
        await self.repository.registrar_execucao_validacao(documento)
        return resultado

    @staticmethod
    def _normalizar_coluna(valor: str) -> str:
        return " ".join(valor.strip().lower().split())

    def _assinar_colunas(self, colunas: list) -> str:
        assinatura = "|".join(self._normalizar_coluna(coluna.nome_canonico) for coluna in colunas)
        return f"sha256:{sha256(assinatura.encode('utf-8')).hexdigest()}"

    def _assinar_colunas_fisicas(self, colunas: list[str]) -> str:
        assinatura = "|".join(sorted(self._normalizar_coluna(coluna) for coluna in colunas))
        return f"sha256:{sha256(assinatura.encode('utf-8')).hexdigest()}"

    @staticmethod
    def _agora() -> str:
        return datetime.now(tz=UTC).isoformat()
