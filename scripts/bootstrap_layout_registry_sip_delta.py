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

_DATASETS = [
    {
        "dataset_codigo": "sip_mapa_assistencial",
        "nome": "SIP — Mapa Assistencial por Município",
        "descricao": "Sistema de Informação de Produtos: beneficiários e eventos por município e operadora.",  # noqa: E501
        "tabela_raw_destino": "bruto_ans.sip_mapa_assistencial",
        "ftp_path": "SIP/",
        "layout_id": "layout_sip_mapa_assistencial_csv",
        "colunas": [
            ColunaLayout(nome_canonico="competencia", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="registro_ans", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="cd_municipio", tipo="string"),
            ColunaLayout(nome_canonico="nm_municipio", tipo="string"),
            ColunaLayout(nome_canonico="sg_uf", tipo="string"),
            ColunaLayout(nome_canonico="nm_regiao", tipo="string"),
            ColunaLayout(nome_canonico="tipo_assistencial", tipo="string"),
            ColunaLayout(nome_canonico="qt_beneficiarios", tipo="integer"),
            ColunaLayout(nome_canonico="qt_eventos", tipo="integer"),
            ColunaLayout(nome_canonico="indicador_cobertura", tipo="decimal"),
        ],
        "aliases": [
            ("COMPETENCIA", "competencia"),
            ("CD_OPERADORA", "registro_ans"),
            ("REGISTRO_ANS", "registro_ans"),
            ("CD_MUNICIPIO", "cd_municipio"),
            ("NM_MUNICIPIO", "nm_municipio"),
            ("SG_UF", "sg_uf"),
            ("NM_REGIAO", "nm_regiao"),
            ("TP_ASSISTENCIAL", "tipo_assistencial"),
            ("QT_BENEFICIARIOS", "qt_beneficiarios"),
            ("QT_EVENTOS", "qt_eventos"),
            ("IN_COBERTURA", "indicador_cobertura"),
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

        print("Bootstrap de layouts SIP concluído.")
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(bootstrap())
