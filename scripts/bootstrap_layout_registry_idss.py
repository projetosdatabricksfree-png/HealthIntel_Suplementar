"""Bootstrap do layout IDSS no MongoDB.

GUARD: nao recria layouts ja existentes. Se o layout 'layout_idss_csv' ja
existir com status='ativo', o script falha com instrucoes para usar POST /aliases.

Uso:
    python scripts/bootstrap_layout_registry_idss.py

Pre-requisito: consultar GET /layout/layouts?dataset_codigo=idss antes de rodar.
Se ja existir layout ativo, use POST /layout/layouts/{id}/aliases para adicionar aliases.
"""

import asyncio

from mongo_layout_service.app.core.database import get_database, get_mongo_client
from mongo_layout_service.app.repositories.layout_repository import LayoutRepository
from mongo_layout_service.app.schemas.layout import (
    ColunaLayout,
    FonteDatasetCreate,
    LayoutAliasCreate,
    LayoutCreate,
    LayoutVersaoCreate,
    StatusLayoutUpdateRequest,
)
from mongo_layout_service.app.services.layout_service import LayoutService

DATASET_CODIGO = "idss"
VERSAO = "v1"
LAYOUT_ID = f"layout_{DATASET_CODIGO}_csv"

FONTE = FonteDatasetCreate(
    dataset_codigo=DATASET_CODIGO,
    nome="IDSS anual por operadora",
    descricao="Indice de Desempenho da Saude Suplementar anual publicado pela ANS.",
    formato_esperado="csv",
    tabela_raw_destino="bruto_ans.idss",
)

LAYOUT = LayoutCreate(
    dataset_codigo=DATASET_CODIGO,
    nome="IDSS anual por operadora",
    descricao="Layout base para carga anual do IDSS (dag_anual_idss).",
    tabela_raw_destino="bruto_ans.idss",
    formato_esperado="csv",
)

COLUNAS = [
    ColunaLayout(nome_canonico="ano_base", tipo="string", obrigatorio=True),
    ColunaLayout(nome_canonico="registro_ans", tipo="string", obrigatorio=True),
    ColunaLayout(nome_canonico="idss_total", tipo="numeric", obrigatorio=True),
    ColunaLayout(nome_canonico="idqs", tipo="numeric"),
    ColunaLayout(nome_canonico="idga", tipo="numeric"),
    ColunaLayout(nome_canonico="idsm", tipo="numeric"),
    ColunaLayout(nome_canonico="idgr", tipo="numeric"),
    ColunaLayout(nome_canonico="faixa_idss", tipo="string"),
    ColunaLayout(nome_canonico="fonte_publicacao", tipo="string"),
]

ALIASES = [
    LayoutAliasCreate(nome_fisico="Ano Base", destino_raw="ano_base"),
    LayoutAliasCreate(nome_fisico="Competencia", destino_raw="ano_base"),
    LayoutAliasCreate(nome_fisico="Registro ANS", destino_raw="registro_ans"),
    LayoutAliasCreate(nome_fisico="IDSS Total", destino_raw="idss_total"),
    LayoutAliasCreate(nome_fisico="IDSS", destino_raw="idss_total"),
    LayoutAliasCreate(nome_fisico="IDQS", destino_raw="idqs"),
    LayoutAliasCreate(nome_fisico="IDGA", destino_raw="idga"),
    LayoutAliasCreate(nome_fisico="IDSM", destino_raw="idsm"),
    LayoutAliasCreate(nome_fisico="IDGR", destino_raw="idgr"),
    LayoutAliasCreate(nome_fisico="Faixa IDSS", destino_raw="faixa_idss"),
    LayoutAliasCreate(nome_fisico="Faixa", destino_raw="faixa_idss"),
    LayoutAliasCreate(nome_fisico="Fonte", destino_raw="fonte_publicacao"),
]


async def bootstrap() -> None:
    repository = LayoutRepository(get_database())
    service = LayoutService(repository)
    await service.inicializar()

    # GUARD: nao criar se layout ativo ja existe
    layout_existente = await repository.obter_layout(LAYOUT_ID)
    if layout_existente:
        status = layout_existente.get("status", "desconhecido")
        raise SystemExit(
            f"\nGUARD: layout '{LAYOUT_ID}' ja existe no MongoDB (status='{status}').\n"
            f"Para adicionar aliases ausentes, use:\n"
            f"  POST /layout/layouts/{LAYOUT_ID}/aliases\n"
            f"Nao recrie o layout — isso quebraria o mapeamento existente.\n"
            f"Abortando."
        )

    await repository.upsert_dataset(FONTE)
    layout = await service.criar_layout(LAYOUT)
    layout_id = layout["layout_id"]
    layout_versao_id = f"{layout_id}:{VERSAO}"

    await service.criar_versao_layout(
        layout_id,
        LayoutVersaoCreate(versao=VERSAO, colunas=COLUNAS),
    )

    for alias in ALIASES:
        alias.layout_versao_id = layout_versao_id
        await service.criar_alias(layout_id, alias)

    await service.atualizar_status_layout(
        layout_id,
        StatusLayoutUpdateRequest(
            status="ativo",
            layout_versao_id=layout_versao_id,
            motivo="bootstrap_fase13",
        ),
    )

    print(f"[bootstrap_idss] Layout '{layout_id}' criado e ativo.")
    get_mongo_client().close()


if __name__ == "__main__":
    asyncio.run(bootstrap())
