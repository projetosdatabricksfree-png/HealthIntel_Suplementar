"""Bootstrap do layout NIP no MongoDB.

GUARD: nao recria layouts ja existentes. Se o layout 'layout_nip_csv' ja
existir com status='ativo', o script falha com instrucoes para usar POST /aliases.

Uso:
    python scripts/bootstrap_layout_registry_nip.py

Pre-requisito: consultar GET /layout/layouts?dataset_codigo=nip antes de rodar.
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

DATASET_CODIGO = "nip"
VERSAO = "v1"
LAYOUT_ID = f"layout_{DATASET_CODIGO}_csv"

FONTE = FonteDatasetCreate(
    dataset_codigo=DATASET_CODIGO,
    nome="NIP e TIR trimestral por operadora",
    descricao="Nucleo de Informacoes das Reclamacoes e Taxa de Intermediacao Resolvida.",
    formato_esperado="csv",
    tabela_raw_destino="bruto_ans.nip_operadora_trimestral",
)

LAYOUT = LayoutCreate(
    dataset_codigo=DATASET_CODIGO,
    nome="NIP e TIR trimestral por operadora",
    descricao="Layout base para demandas NIP e taxas de intermediacao.",
    tabela_raw_destino="bruto_ans.nip_operadora_trimestral",
    formato_esperado="csv",
)

COLUNAS = [
    ColunaLayout(nome_canonico="trimestre", tipo="string", obrigatorio=True),
    ColunaLayout(nome_canonico="registro_ans", tipo="string", obrigatorio=True),
    ColunaLayout(nome_canonico="modalidade", tipo="string", obrigatorio=True),
    ColunaLayout(nome_canonico="demandas_nip", tipo="integer", obrigatorio=True),
    ColunaLayout(nome_canonico="demandas_resolvidas", tipo="integer"),
    ColunaLayout(nome_canonico="beneficiarios", tipo="integer"),
    ColunaLayout(nome_canonico="taxa_intermediacao_resolvida", tipo="numeric"),
    ColunaLayout(nome_canonico="taxa_resolutividade", tipo="numeric"),
    ColunaLayout(nome_canonico="fonte_publicacao", tipo="string"),
]

ALIASES = [
    LayoutAliasCreate(nome_fisico="Trimestre", destino_raw="trimestre"),
    LayoutAliasCreate(nome_fisico="Registro ANS", destino_raw="registro_ans"),
    LayoutAliasCreate(nome_fisico="Modalidade", destino_raw="modalidade"),
    LayoutAliasCreate(nome_fisico="Demandas NIP", destino_raw="demandas_nip"),
    LayoutAliasCreate(nome_fisico="Demandas Resolvidas", destino_raw="demandas_resolvidas"),
    LayoutAliasCreate(nome_fisico="Beneficiarios", destino_raw="beneficiarios"),
    LayoutAliasCreate(nome_fisico="Beneficiários", destino_raw="beneficiarios"),
    LayoutAliasCreate(nome_fisico="TIR", destino_raw="taxa_intermediacao_resolvida"),
    LayoutAliasCreate(
        nome_fisico="Taxa Intermediacao Resolvida",
        destino_raw="taxa_intermediacao_resolvida",
    ),
    LayoutAliasCreate(nome_fisico="Taxa Resolutividade", destino_raw="taxa_resolutividade"),
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

    print(f"[bootstrap_nip] Layout '{layout_id}' criado e ativo.")
    get_mongo_client().close()


if __name__ == "__main__":
    asyncio.run(bootstrap())
