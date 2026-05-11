from __future__ import annotations

import asyncio

from mongo_layout_service.app.core.database import get_database, get_mongo_client
from mongo_layout_service.app.repositories.layout_repository import LayoutRepository
from mongo_layout_service.app.schemas.layout import (
    ColunaLayout,
    FonteDatasetCreate,
    LayoutAliasCreate,
    LayoutCreate,
    LayoutVersaoCreate,
)
from mongo_layout_service.app.services.layout_service import LayoutService

_ANS_BASE = "https://dadosabertos.ans.gov.br/FTP/PDA/"

_DATASETS = [
    {
        "dataset_codigo": "tuss_oficial",
        "nome": "Terminologia Unificada da Saúde Suplementar (TUSS) Oficial",
        "descricao": "Tabela TUSS oficial ANS com vigência e status de validade.",
        "tabela_raw_destino": "bruto_ans.tuss_terminologia_oficial",
        "ftp_path": "TUSS/",
        "layout_id": "layout_tuss_oficial_csv",
        "colunas": [
            ColunaLayout(nome_canonico="codigo_tuss", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="descricao", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="versao_tuss", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="vigencia_inicio", tipo="date"),
            ColunaLayout(nome_canonico="vigencia_fim", tipo="date"),
            ColunaLayout(nome_canonico="is_tuss_vigente", tipo="boolean"),
        ],
        "aliases": [
            ("CD_TUSS", "codigo_tuss"),
            ("CODIGO", "codigo_tuss"),
            ("DS_TUSS", "descricao"),
            ("DESCRICAO", "descricao"),
            ("VERSAO", "versao_tuss"),
            ("DT_INICIO_VIGENCIA", "vigencia_inicio"),
            ("DT_FIM_VIGENCIA", "vigencia_fim"),
        ],
    },
]


async def bootstrap() -> None:
    client = get_mongo_client()
    try:
        repository = LayoutRepository(get_database())
        service = LayoutService(repository)
        await service.inicializar()

        for ds in _DATASETS:
            dataset = FonteDatasetCreate(
                dataset_codigo=ds["dataset_codigo"],
                nome=ds["nome"],
                descricao=ds["descricao"],
                formato_esperado="csv",
                tabela_raw_destino=ds["tabela_raw_destino"],
            )
            await repository.upsert_dataset(dataset)

            layout = LayoutCreate(
                dataset_codigo=ds["dataset_codigo"],
                nome=ds["nome"],
                descricao=ds["descricao"],
                tabela_raw_destino=ds["tabela_raw_destino"],
                formato_esperado="csv",
            )
            layout_id = ds["layout_id"]
            if not await repository.obter_layout(layout_id):
                await service.criar_layout(layout)

            layout_versao_id = f"{layout_id}:v1"
            if not await repository.obter_versao(layout_versao_id):
                await service.criar_versao_layout(
                    layout_id,
                    LayoutVersaoCreate(versao="v1", colunas=ds["colunas"]),
                )

            for nome_fisico, destino_raw in ds["aliases"]:
                try:
                    await service.criar_alias(
                        layout_id,
                        layout_versao_id,
                        LayoutAliasCreate(nome_fisico=nome_fisico, destino_raw=destino_raw),
                    )
                except Exception:
                    pass

        print("Bootstrap de layouts TUSS Oficial concluído.")
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(bootstrap())
