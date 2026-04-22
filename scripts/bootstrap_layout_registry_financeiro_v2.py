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

FINANCEIRO_V2_LAYOUTS = [
    {
        "fonte": FonteDatasetCreate(
            dataset_codigo="vda",
            nome="VDA mensal",
            descricao="Valor Devido à ANS mensal por operadora.",
            formato_esperado="csv",
            tabela_raw_destino="bruto_ans.vda_operadora_mensal",
        ),
        "layout": LayoutCreate(
            dataset_codigo="vda",
            nome="VDA mensal",
            descricao="Layout mensal da série de VDA.",
            tabela_raw_destino="bruto_ans.vda_operadora_mensal",
            formato_esperado="csv",
        ),
        "versao": "v1",
        "colunas": [
            ColunaLayout(nome_canonico="competencia", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="registro_ans", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="valor_devido", tipo="numeric"),
            ColunaLayout(nome_canonico="valor_pago", tipo="numeric"),
            ColunaLayout(nome_canonico="saldo_devedor", tipo="numeric"),
            ColunaLayout(nome_canonico="situacao_cobranca", tipo="string"),
            ColunaLayout(nome_canonico="data_vencimento", tipo="date"),
            ColunaLayout(nome_canonico="fonte_publicacao", tipo="string"),
        ],
        "aliases": [
            LayoutAliasCreate(nome_fisico="Competencia", destino_raw="competencia"),
            LayoutAliasCreate(nome_fisico="Registro ANS", destino_raw="registro_ans"),
            LayoutAliasCreate(nome_fisico="Valor Devido", destino_raw="valor_devido"),
            LayoutAliasCreate(nome_fisico="Valor Pago", destino_raw="valor_pago"),
            LayoutAliasCreate(nome_fisico="Saldo Devedor", destino_raw="saldo_devedor"),
            LayoutAliasCreate(
                nome_fisico="Situacao Cobranca",
                destino_raw="situacao_cobranca",
            ),
            LayoutAliasCreate(nome_fisico="Data Vencimento", destino_raw="data_vencimento"),
            LayoutAliasCreate(nome_fisico="Fonte", destino_raw="fonte_publicacao"),
        ],
    },
    {
        "fonte": FonteDatasetCreate(
            dataset_codigo="glosa",
            nome="Glosa mensal",
            descricao="Glosa mensal por operadora e tipo de glosa.",
            formato_esperado="csv",
            tabela_raw_destino="bruto_ans.glosa_operadora_mensal",
        ),
        "layout": LayoutCreate(
            dataset_codigo="glosa",
            nome="Glosa mensal",
            descricao="Layout mensal da série de glosa por tipo.",
            tabela_raw_destino="bruto_ans.glosa_operadora_mensal",
            formato_esperado="csv",
        ),
        "versao": "v1",
        "colunas": [
            ColunaLayout(nome_canonico="competencia", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="registro_ans", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="tipo_glosa", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="qt_glosa", tipo="integer"),
            ColunaLayout(nome_canonico="valor_glosa", tipo="numeric"),
            ColunaLayout(nome_canonico="valor_faturado", tipo="numeric"),
            ColunaLayout(nome_canonico="fonte_publicacao", tipo="string"),
        ],
        "aliases": [
            LayoutAliasCreate(nome_fisico="Competencia", destino_raw="competencia"),
            LayoutAliasCreate(nome_fisico="Registro ANS", destino_raw="registro_ans"),
            LayoutAliasCreate(nome_fisico="Tipo Glosa", destino_raw="tipo_glosa"),
            LayoutAliasCreate(nome_fisico="Qt Glosa", destino_raw="qt_glosa"),
            LayoutAliasCreate(nome_fisico="Valor Glosa", destino_raw="valor_glosa"),
            LayoutAliasCreate(
                nome_fisico="Valor Faturado",
                destino_raw="valor_faturado",
            ),
            LayoutAliasCreate(nome_fisico="Fonte", destino_raw="fonte_publicacao"),
        ],
    },
]


async def bootstrap() -> None:
    repository = LayoutRepository(get_database())
    service = LayoutService(repository)
    await service.inicializar()

    for definicao in FINANCEIRO_V2_LAYOUTS:
        await repository.upsert_dataset(definicao["fonte"])
        layout = await repository.obter_layout(
            f"layout_{definicao['layout'].dataset_codigo}_{definicao['layout'].formato_esperado}"
        )
        if not layout:
            layout = await service.criar_layout(definicao["layout"])
        layout_id = layout["layout_id"]
        layout_versao_id = f"{layout_id}:{definicao['versao']}"
        if not await repository.obter_versao(layout_versao_id):
            await service.criar_versao_layout(
                layout_id,
                LayoutVersaoCreate(versao=definicao["versao"], colunas=definicao["colunas"]),
            )
        for alias in definicao["aliases"]:
            alias.layout_versao_id = layout_versao_id
            await service.criar_alias(layout_id, alias)
        await service.atualizar_status_layout(
            layout_id,
            StatusLayoutUpdateRequest(
                status="ativo",
                layout_versao_id=layout_versao_id,
                motivo="bootstrap_sprint_10",
            ),
        )

    get_mongo_client().close()


if __name__ == "__main__":
    asyncio.run(bootstrap())
