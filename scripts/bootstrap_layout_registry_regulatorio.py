import asyncio

from mongo_layout_service.app.core.database import get_database, get_mongo_client
from mongo_layout_service.app.repositories.layout_repository import LayoutRepository
from mongo_layout_service.app.schemas.layout import (
    ColunaLayout,
    LayoutAliasCreate,
    LayoutCreate,
    LayoutVersaoCreate,
    StatusLayoutUpdateRequest,
)
from mongo_layout_service.app.services.layout_service import LayoutService

REGULATORY_LAYOUTS = [
    {
        "dataset_codigo": "igr",
        "nome": "IGR trimestral por operadora",
        "descricao": "Layout base para cargas trimestrais de IGR e meta regulatoria.",
        "tabela_raw_destino": "bruto_ans.igr_operadora_trimestral",
        "versao": "v1",
        "colunas": [
            ColunaLayout(nome_canonico="trimestre", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="registro_ans", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="modalidade", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="porte", tipo="string"),
            ColunaLayout(nome_canonico="total_reclamacoes", tipo="integer"),
            ColunaLayout(nome_canonico="beneficiarios", tipo="integer"),
            ColunaLayout(nome_canonico="igr", tipo="numeric", obrigatorio=True),
            ColunaLayout(nome_canonico="meta_igr", tipo="numeric"),
            ColunaLayout(nome_canonico="atingiu_meta", tipo="boolean"),
            ColunaLayout(nome_canonico="fonte_publicacao", tipo="string"),
        ],
        "aliases": [
            LayoutAliasCreate(nome_fisico="Trimestre", destino_raw="trimestre"),
            LayoutAliasCreate(nome_fisico="Registro ANS", destino_raw="registro_ans"),
            LayoutAliasCreate(nome_fisico="Modalidade", destino_raw="modalidade"),
            LayoutAliasCreate(nome_fisico="Porte", destino_raw="porte"),
            LayoutAliasCreate(
                nome_fisico="Qtd Reclamações",
                destino_raw="total_reclamacoes",
            ),
            LayoutAliasCreate(nome_fisico="Beneficiários", destino_raw="beneficiarios"),
            LayoutAliasCreate(nome_fisico="IGR", destino_raw="igr"),
            LayoutAliasCreate(nome_fisico="Meta IGR", destino_raw="meta_igr"),
            LayoutAliasCreate(nome_fisico="Atingiu Meta", destino_raw="atingiu_meta"),
            LayoutAliasCreate(nome_fisico="Fonte", destino_raw="fonte_publicacao"),
        ],
    },
    {
        "dataset_codigo": "nip",
        "nome": "NIP e TIR trimestral por operadora",
        "descricao": "Layout base para demandas NIP e taxas de intermediação.",
        "tabela_raw_destino": "bruto_ans.nip_operadora_trimestral",
        "versao": "v1",
        "colunas": [
            ColunaLayout(nome_canonico="trimestre", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="registro_ans", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="modalidade", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="demandas_nip", tipo="integer", obrigatorio=True),
            ColunaLayout(nome_canonico="demandas_resolvidas", tipo="integer"),
            ColunaLayout(nome_canonico="beneficiarios", tipo="integer"),
            ColunaLayout(
                nome_canonico="taxa_intermediacao_resolvida",
                tipo="numeric",
            ),
            ColunaLayout(nome_canonico="taxa_resolutividade", tipo="numeric"),
            ColunaLayout(nome_canonico="fonte_publicacao", tipo="string"),
        ],
        "aliases": [
            LayoutAliasCreate(nome_fisico="Trimestre", destino_raw="trimestre"),
            LayoutAliasCreate(nome_fisico="Registro ANS", destino_raw="registro_ans"),
            LayoutAliasCreate(nome_fisico="Modalidade", destino_raw="modalidade"),
            LayoutAliasCreate(nome_fisico="Demandas NIP", destino_raw="demandas_nip"),
            LayoutAliasCreate(
                nome_fisico="Demandas Resolvidas",
                destino_raw="demandas_resolvidas",
            ),
            LayoutAliasCreate(nome_fisico="Beneficiários", destino_raw="beneficiarios"),
            LayoutAliasCreate(
                nome_fisico="TIR",
                destino_raw="taxa_intermediacao_resolvida",
            ),
            LayoutAliasCreate(
                nome_fisico="Taxa Resolutividade",
                destino_raw="taxa_resolutividade",
            ),
            LayoutAliasCreate(nome_fisico="Fonte", destino_raw="fonte_publicacao"),
        ],
    },
    {
        "dataset_codigo": "rn623_lista",
        "nome": "Listas RN 623 por trimestre",
        "descricao": "Layout base para listas de excelencia e reducao da RN 623/2024.",
        "tabela_raw_destino": "bruto_ans.rn623_lista_operadora_trimestral",
        "versao": "v1",
        "colunas": [
            ColunaLayout(nome_canonico="trimestre", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="registro_ans", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="modalidade", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="tipo_lista", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="total_nip", tipo="integer"),
            ColunaLayout(nome_canonico="beneficiarios", tipo="integer"),
            ColunaLayout(nome_canonico="igr", tipo="numeric"),
            ColunaLayout(nome_canonico="meta_igr", tipo="numeric"),
            ColunaLayout(nome_canonico="elegivel", tipo="boolean"),
            ColunaLayout(nome_canonico="observacao", tipo="string"),
            ColunaLayout(nome_canonico="fonte_publicacao", tipo="string"),
        ],
        "aliases": [
            LayoutAliasCreate(nome_fisico="Trimestre", destino_raw="trimestre"),
            LayoutAliasCreate(nome_fisico="Registro ANS", destino_raw="registro_ans"),
            LayoutAliasCreate(nome_fisico="Modalidade", destino_raw="modalidade"),
            LayoutAliasCreate(nome_fisico="Tipo Lista", destino_raw="tipo_lista"),
            LayoutAliasCreate(nome_fisico="Qtd NIP", destino_raw="total_nip"),
            LayoutAliasCreate(nome_fisico="Beneficiários", destino_raw="beneficiarios"),
            LayoutAliasCreate(nome_fisico="IGR", destino_raw="igr"),
            LayoutAliasCreate(nome_fisico="Meta IGR", destino_raw="meta_igr"),
            LayoutAliasCreate(nome_fisico="Elegível", destino_raw="elegivel"),
            LayoutAliasCreate(nome_fisico="Observação", destino_raw="observacao"),
            LayoutAliasCreate(nome_fisico="Fonte", destino_raw="fonte_publicacao"),
        ],
    },
]


async def bootstrap() -> None:
    repository = LayoutRepository(get_database())
    service = LayoutService(repository)
    await service.inicializar()

    for definicao in REGULATORY_LAYOUTS:
        payload_layout = LayoutCreate(
            dataset_codigo=definicao["dataset_codigo"],
            nome=definicao["nome"],
            descricao=definicao["descricao"],
            tabela_raw_destino=definicao["tabela_raw_destino"],
            formato_esperado="csv",
        )
        layout_id = f"layout_{payload_layout.dataset_codigo}_{payload_layout.formato_esperado}"
        layout = await repository.obter_layout(layout_id)
        if not layout:
            layout = await service.criar_layout(payload_layout)

        layout_versao_id = f"{layout_id}:{definicao['versao']}"
        versao = await repository.obter_versao(layout_versao_id)
        if not versao:
            await service.criar_versao_layout(
                layout_id,
                LayoutVersaoCreate(
                    versao=definicao["versao"],
                    colunas=definicao["colunas"],
                ),
            )

        for alias in definicao["aliases"]:
            alias.layout_versao_id = layout_versao_id
            await service.criar_alias(layout_id, alias)

        await service.atualizar_status_layout(
            layout_id,
            StatusLayoutUpdateRequest(
                status="ativo",
                layout_versao_id=layout_versao_id,
                motivo="bootstrap_sprint_07",
            ),
        )

    get_mongo_client().close()


if __name__ == "__main__":
    asyncio.run(bootstrap())
