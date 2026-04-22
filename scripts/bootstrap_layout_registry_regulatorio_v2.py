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

REGULATORY_LAYOUTS_V2 = [
    {
        "dataset_codigo": "regime_especial",
        "nome": "Regime especial por operadora",
        "descricao": "Layout para regime especial de direcao fiscal e tecnica.",
        "tabela_raw_destino": "bruto_ans.regime_especial_operadora_trimestral",
        "versao": "v1",
        "colunas": [
            ColunaLayout(nome_canonico="trimestre", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="registro_ans", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="tipo_regime", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="data_inicio", tipo="date", obrigatorio=True),
            ColunaLayout(nome_canonico="data_fim", tipo="date"),
            ColunaLayout(nome_canonico="descricao", tipo="string"),
            ColunaLayout(nome_canonico="fonte_publicacao", tipo="string"),
        ],
        "aliases": [
            LayoutAliasCreate(nome_fisico="Trimestre", destino_raw="trimestre"),
            LayoutAliasCreate(nome_fisico="Registro ANS", destino_raw="registro_ans"),
            LayoutAliasCreate(nome_fisico="Tipo Regime", destino_raw="tipo_regime"),
            LayoutAliasCreate(nome_fisico="Data Inicio", destino_raw="data_inicio"),
            LayoutAliasCreate(nome_fisico="Data Fim", destino_raw="data_fim"),
            LayoutAliasCreate(nome_fisico="Descricao", destino_raw="descricao"),
            LayoutAliasCreate(nome_fisico="Fonte", destino_raw="fonte_publicacao"),
        ],
    },
    {
        "dataset_codigo": "prudencial",
        "nome": "Indicadores prudenciais por operadora",
        "descricao": "Layout para capital regulatorio e indicadores prudenciais.",
        "tabela_raw_destino": "bruto_ans.prudencial_operadora_trimestral",
        "versao": "v1",
        "colunas": [
            ColunaLayout(nome_canonico="trimestre", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="registro_ans", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="margem_solvencia", tipo="numeric"),
            ColunaLayout(nome_canonico="capital_minimo_requerido", tipo="numeric"),
            ColunaLayout(nome_canonico="capital_disponivel", tipo="numeric"),
            ColunaLayout(nome_canonico="indice_liquidez", tipo="numeric"),
            ColunaLayout(nome_canonico="situacao_prudencial", tipo="string"),
            ColunaLayout(nome_canonico="fonte_publicacao", tipo="string"),
        ],
        "aliases": [
            LayoutAliasCreate(nome_fisico="Trimestre", destino_raw="trimestre"),
            LayoutAliasCreate(nome_fisico="Registro ANS", destino_raw="registro_ans"),
            LayoutAliasCreate(nome_fisico="Margem Solvencia", destino_raw="margem_solvencia"),
            LayoutAliasCreate(
                nome_fisico="Capital Minimo Requerido",
                destino_raw="capital_minimo_requerido",
            ),
            LayoutAliasCreate(
                nome_fisico="Capital Disponivel",
                destino_raw="capital_disponivel",
            ),
            LayoutAliasCreate(nome_fisico="Indice Liquidez", destino_raw="indice_liquidez"),
            LayoutAliasCreate(
                nome_fisico="Situacao Prudencial",
                destino_raw="situacao_prudencial",
            ),
            LayoutAliasCreate(nome_fisico="Fonte", destino_raw="fonte_publicacao"),
        ],
    },
    {
        "dataset_codigo": "portabilidade",
        "nome": "Portabilidade mensal por operadora",
        "descricao": "Layout para movimentacao de portabilidade por competencia.",
        "tabela_raw_destino": "bruto_ans.portabilidade_operadora_mensal",
        "versao": "v1",
        "colunas": [
            ColunaLayout(nome_canonico="competencia", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="registro_ans", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="modalidade", tipo="string"),
            ColunaLayout(nome_canonico="tipo_contratacao", tipo="string"),
            ColunaLayout(nome_canonico="qt_portabilidade_entrada", tipo="integer"),
            ColunaLayout(nome_canonico="qt_portabilidade_saida", tipo="integer"),
            ColunaLayout(nome_canonico="fonte_publicacao", tipo="string"),
        ],
        "aliases": [
            LayoutAliasCreate(nome_fisico="Competencia", destino_raw="competencia"),
            LayoutAliasCreate(nome_fisico="Registro ANS", destino_raw="registro_ans"),
            LayoutAliasCreate(nome_fisico="Modalidade", destino_raw="modalidade"),
            LayoutAliasCreate(
                nome_fisico="Tipo Contratacao",
                destino_raw="tipo_contratacao",
            ),
            LayoutAliasCreate(
                nome_fisico="Qtd Portabilidade Entrada",
                destino_raw="qt_portabilidade_entrada",
            ),
            LayoutAliasCreate(
                nome_fisico="Qtd Portabilidade Saida",
                destino_raw="qt_portabilidade_saida",
            ),
            LayoutAliasCreate(nome_fisico="Fonte", destino_raw="fonte_publicacao"),
        ],
    },
    {
        "dataset_codigo": "taxa_resolutividade",
        "nome": "Taxa de resolutividade por operadora",
        "descricao": "Layout para taxa de resolutividade trimestral.",
        "tabela_raw_destino": "bruto_ans.taxa_resolutividade_operadora_trimestral",
        "versao": "v1",
        "colunas": [
            ColunaLayout(nome_canonico="trimestre", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="registro_ans", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="modalidade", tipo="string"),
            ColunaLayout(nome_canonico="taxa_resolutividade", tipo="numeric"),
            ColunaLayout(nome_canonico="n_reclamacao_resolvida", tipo="integer"),
            ColunaLayout(nome_canonico="n_reclamacao_total", tipo="integer"),
            ColunaLayout(nome_canonico="fonte_publicacao", tipo="string"),
        ],
        "aliases": [
            LayoutAliasCreate(nome_fisico="Trimestre", destino_raw="trimestre"),
            LayoutAliasCreate(nome_fisico="Registro ANS", destino_raw="registro_ans"),
            LayoutAliasCreate(nome_fisico="Modalidade", destino_raw="modalidade"),
            LayoutAliasCreate(
                nome_fisico="Taxa Resolutividade",
                destino_raw="taxa_resolutividade",
            ),
            LayoutAliasCreate(
                nome_fisico="Qtd Resolvida",
                destino_raw="n_reclamacao_resolvida",
            ),
            LayoutAliasCreate(
                nome_fisico="Qtd Total",
                destino_raw="n_reclamacao_total",
            ),
            LayoutAliasCreate(nome_fisico="Fonte", destino_raw="fonte_publicacao"),
        ],
    },
]


async def bootstrap() -> None:
    repository = LayoutRepository(get_database())
    service = LayoutService(repository)
    await service.inicializar()

    for definicao in REGULATORY_LAYOUTS_V2:
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
                motivo="bootstrap_sprint_08",
            ),
        )

    get_mongo_client().close()


if __name__ == "__main__":
    asyncio.run(bootstrap())
