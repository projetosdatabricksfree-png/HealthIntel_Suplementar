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

FINANCEIRO_LAYOUTS = [
    {
        "fonte": FonteDatasetCreate(
            dataset_codigo="diops",
            nome="DIOPS Financeiro",
            descricao="Serie financeira trimestral derivada do DIOPS-XML.",
            formato_esperado="xml",
            tabela_raw_destino="bruto_ans.diops_operadora_trimestral",
        ),
        "layout": LayoutCreate(
            dataset_codigo="diops",
            nome="DIOPS Financeiro",
            descricao="Layout financeiro trimestral em DIOPS-XML.",
            tabela_raw_destino="bruto_ans.diops_operadora_trimestral",
            formato_esperado="xml",
        ),
        "versao": "v1",
        "colunas": [
            ColunaLayout(nome_canonico="trimestre", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="registro_ans", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="cnpj", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="ativo_total", tipo="numeric"),
            ColunaLayout(nome_canonico="passivo_total", tipo="numeric"),
            ColunaLayout(nome_canonico="patrimonio_liquido", tipo="numeric"),
            ColunaLayout(nome_canonico="receita_total", tipo="numeric"),
            ColunaLayout(nome_canonico="despesa_total", tipo="numeric"),
            ColunaLayout(nome_canonico="resultado_periodo", tipo="numeric"),
            ColunaLayout(nome_canonico="provisao_tecnica", tipo="numeric"),
            ColunaLayout(nome_canonico="margem_solvencia_calculada", tipo="numeric"),
            ColunaLayout(nome_canonico="fonte_publicacao", tipo="string"),
        ],
        "aliases": [
            LayoutAliasCreate(nome_fisico="Trimestre", destino_raw="trimestre"),
            LayoutAliasCreate(nome_fisico="Registro ANS", destino_raw="registro_ans"),
            LayoutAliasCreate(nome_fisico="CNPJ", destino_raw="cnpj"),
            LayoutAliasCreate(nome_fisico="Ativo Total", destino_raw="ativo_total"),
            LayoutAliasCreate(nome_fisico="Passivo Total", destino_raw="passivo_total"),
            LayoutAliasCreate(
                nome_fisico="Patrimonio Liquido",
                destino_raw="patrimonio_liquido",
            ),
            LayoutAliasCreate(nome_fisico="Receita Total", destino_raw="receita_total"),
            LayoutAliasCreate(nome_fisico="Despesa Total", destino_raw="despesa_total"),
            LayoutAliasCreate(
                nome_fisico="Resultado Periodo",
                destino_raw="resultado_periodo",
            ),
            LayoutAliasCreate(
                nome_fisico="Provisao Tecnica",
                destino_raw="provisao_tecnica",
            ),
            LayoutAliasCreate(
                nome_fisico="Margem Solvencia Calculada",
                destino_raw="margem_solvencia_calculada",
            ),
            LayoutAliasCreate(nome_fisico="Fonte", destino_raw="fonte_publicacao"),
        ],
    },
    {
        "fonte": FonteDatasetCreate(
            dataset_codigo="fip",
            nome="FIP historico financeiro",
            descricao="Serie historica de sinistros e contraprestacoes.",
            formato_esperado="csv",
            tabela_raw_destino="bruto_ans.fip_operadora_trimestral",
        ),
        "layout": LayoutCreate(
            dataset_codigo="fip",
            nome="FIP historico financeiro",
            descricao="Layout historico em CSV para compatibilidade financeira.",
            tabela_raw_destino="bruto_ans.fip_operadora_trimestral",
            formato_esperado="csv",
        ),
        "versao": "v1",
        "colunas": [
            ColunaLayout(nome_canonico="trimestre", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="registro_ans", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="modalidade", tipo="string"),
            ColunaLayout(nome_canonico="tipo_contratacao", tipo="string"),
            ColunaLayout(nome_canonico="sinistro_total", tipo="numeric"),
            ColunaLayout(nome_canonico="contraprestacao_total", tipo="numeric"),
            ColunaLayout(nome_canonico="sinistralidade_bruta", tipo="numeric"),
            ColunaLayout(nome_canonico="ressarcimento_sus", tipo="numeric"),
            ColunaLayout(nome_canonico="evento_indenizavel", tipo="numeric"),
            ColunaLayout(nome_canonico="fonte_publicacao", tipo="string"),
        ],
        "aliases": [
            LayoutAliasCreate(nome_fisico="Trimestre", destino_raw="trimestre"),
            LayoutAliasCreate(nome_fisico="Registro ANS", destino_raw="registro_ans"),
            LayoutAliasCreate(nome_fisico="Modalidade", destino_raw="modalidade"),
            LayoutAliasCreate(
                nome_fisico="Tipo Contratacao",
                destino_raw="tipo_contratacao",
            ),
            LayoutAliasCreate(nome_fisico="Sinistro Total", destino_raw="sinistro_total"),
            LayoutAliasCreate(
                nome_fisico="Contraprestacao Total",
                destino_raw="contraprestacao_total",
            ),
            LayoutAliasCreate(
                nome_fisico="Sinistralidade Bruta",
                destino_raw="sinistralidade_bruta",
            ),
            LayoutAliasCreate(
                nome_fisico="Ressarcimento SUS",
                destino_raw="ressarcimento_sus",
            ),
            LayoutAliasCreate(
                nome_fisico="Evento Indenizavel",
                destino_raw="evento_indenizavel",
            ),
            LayoutAliasCreate(nome_fisico="Fonte", destino_raw="fonte_publicacao"),
        ],
    },
]


async def bootstrap() -> None:
    repository = LayoutRepository(get_database())
    service = LayoutService(repository)
    await service.inicializar()

    for definicao in FINANCEIRO_LAYOUTS:
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
                motivo="bootstrap_sprint_09",
            ),
        )

    get_mongo_client().close()


if __name__ == "__main__":
    asyncio.run(bootstrap())
