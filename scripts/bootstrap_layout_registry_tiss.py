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


async def bootstrap() -> None:
    repository = LayoutRepository(get_database())
    service = LayoutService(repository)
    await service.inicializar()

    fonte = FonteDatasetCreate(
        dataset_codigo="tiss_procedimento",
        nome="Dados Assistenciais TISS ANS",
        descricao="Procedimentos TISS agregados por operadora, grupo e UF (trimestral).",
        formato_esperado="csv",
        tabela_raw_destino="bruto_ans.tiss_procedimento_trimestral",
    )
    layout = LayoutCreate(
        dataset_codigo="tiss_procedimento",
        nome="TISS Procedimentos ANS",
        descricao="Layout para dados assistenciais TISS agregados por grupo de procedimento.",
        tabela_raw_destino="bruto_ans.tiss_procedimento_trimestral",
        formato_esperado="csv",
    )

    await repository.upsert_dataset(fonte)
    layout_id = f"layout_{layout.dataset_codigo}_{layout.formato_esperado}"
    if not await repository.obter_layout(layout_id):
        await service.criar_layout(layout)

    layout_versao_id = f"{layout_id}:v1"
    if not await repository.obter_versao(layout_versao_id):
        await service.criar_versao_layout(
            layout_id,
            LayoutVersaoCreate(
                versao="v1",
                colunas=[
                    ColunaLayout(nome_canonico="trimestre", tipo="string", obrigatorio=True),
                    ColunaLayout(nome_canonico="registro_ans", tipo="string", obrigatorio=True),
                    ColunaLayout(nome_canonico="sg_uf", tipo="string"),
                    ColunaLayout(nome_canonico="grupo_procedimento", tipo="string"),
                    ColunaLayout(nome_canonico="grupo_desc", tipo="string"),
                    ColunaLayout(nome_canonico="subgrupo_procedimento", tipo="string"),
                    ColunaLayout(nome_canonico="qt_procedimentos", tipo="integer"),
                    ColunaLayout(nome_canonico="qt_beneficiarios_distintos", tipo="integer"),
                    ColunaLayout(nome_canonico="valor_total", tipo="float"),
                    ColunaLayout(nome_canonico="modalidade", tipo="string"),
                    ColunaLayout(nome_canonico="tipo_contratacao", tipo="string"),
                    ColunaLayout(nome_canonico="fonte_publicacao", tipo="string"),
                ],
            ),
        )

    for alias in [
        LayoutAliasCreate(nome_fisico="Trimestre", destino_raw="trimestre"),
        LayoutAliasCreate(nome_fisico="Registro ANS", destino_raw="registro_ans"),
        LayoutAliasCreate(nome_fisico="UF", destino_raw="sg_uf"),
        LayoutAliasCreate(nome_fisico="Grupo Procedimento", destino_raw="grupo_procedimento"),
        LayoutAliasCreate(nome_fisico="Descricao Grupo", destino_raw="grupo_desc"),
        LayoutAliasCreate(nome_fisico="Subgrupo", destino_raw="subgrupo_procedimento"),
        LayoutAliasCreate(nome_fisico="Qt Procedimentos", destino_raw="qt_procedimentos"),
        LayoutAliasCreate(nome_fisico="Qt Beneficiarios", destino_raw="qt_beneficiarios_distintos"),
        LayoutAliasCreate(nome_fisico="Valor Total", destino_raw="valor_total"),
        LayoutAliasCreate(nome_fisico="Modalidade", destino_raw="modalidade"),
        LayoutAliasCreate(nome_fisico="Tipo Contratacao", destino_raw="tipo_contratacao"),
        LayoutAliasCreate(nome_fisico="Fonte", destino_raw="fonte_publicacao"),
    ]:
        alias.layout_versao_id = layout_versao_id
        await service.criar_alias(layout_id, alias)

    await service.atualizar_status_layout(
        layout_id,
        StatusLayoutUpdateRequest(
            status="ativo",
            layout_versao_id=layout_versao_id,
            motivo="bootstrap_fase3_tiss",
        ),
    )

    get_mongo_client().close()


if __name__ == "__main__":
    asyncio.run(bootstrap())
