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
        dataset_codigo="cnes_estabelecimento",
        nome="CNES Estabelecimentos DATASUS",
        descricao="Cadastro Nacional de Estabelecimentos de Saude (DATASUS/MS).",
        formato_esperado="csv",
        tabela_raw_destino="bruto_ans.cnes_estabelecimento",
    )
    layout = LayoutCreate(
        dataset_codigo="cnes_estabelecimento",
        nome="CNES Estabelecimentos ANS",
        descricao="Layout para estabelecimentos CNES com geolocalização e tipo de unidade.",
        tabela_raw_destino="bruto_ans.cnes_estabelecimento",
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
                    ColunaLayout(nome_canonico="competencia", tipo="string", obrigatorio=True),
                    ColunaLayout(nome_canonico="cnes", tipo="string", obrigatorio=True),
                    ColunaLayout(nome_canonico="cnpj", tipo="string"),
                    ColunaLayout(nome_canonico="razao_social", tipo="string"),
                    ColunaLayout(nome_canonico="nome_fantasia", tipo="string"),
                    ColunaLayout(nome_canonico="sg_uf", tipo="string"),
                    ColunaLayout(nome_canonico="cd_municipio", tipo="string", obrigatorio=True),
                    ColunaLayout(nome_canonico="nm_municipio", tipo="string"),
                    ColunaLayout(nome_canonico="tipo_unidade", tipo="string"),
                    ColunaLayout(nome_canonico="tipo_unidade_desc", tipo="string"),
                    ColunaLayout(nome_canonico="esfera_administrativa", tipo="string"),
                    ColunaLayout(nome_canonico="vinculo_sus", tipo="boolean"),
                    ColunaLayout(nome_canonico="leitos_existentes", tipo="integer"),
                    ColunaLayout(nome_canonico="leitos_sus", tipo="integer"),
                    ColunaLayout(nome_canonico="latitude", tipo="float"),
                    ColunaLayout(nome_canonico="longitude", tipo="float"),
                    ColunaLayout(nome_canonico="situacao", tipo="string"),
                    ColunaLayout(nome_canonico="fonte_publicacao", tipo="string"),
                ],
            ),
        )

    for alias in [
        LayoutAliasCreate(nome_fisico="Competencia", destino_raw="competencia"),
        LayoutAliasCreate(nome_fisico="CO_CNES", destino_raw="cnes"),
        LayoutAliasCreate(nome_fisico="CNES", destino_raw="cnes"),
        LayoutAliasCreate(nome_fisico="NO_CNPJ", destino_raw="cnpj"),
        LayoutAliasCreate(nome_fisico="NO_RAZAO_SOCIAL", destino_raw="razao_social"),
        LayoutAliasCreate(nome_fisico="NO_FANTASIA", destino_raw="nome_fantasia"),
        LayoutAliasCreate(nome_fisico="SG_UF", destino_raw="sg_uf"),
        LayoutAliasCreate(nome_fisico="CO_MUNICIPIO_GESTOR", destino_raw="cd_municipio"),
        LayoutAliasCreate(nome_fisico="NO_MUNICIPIO", destino_raw="nm_municipio"),
        LayoutAliasCreate(nome_fisico="TP_UNIDADE", destino_raw="tipo_unidade"),
        LayoutAliasCreate(nome_fisico="DS_TIPO_UNIDADE", destino_raw="tipo_unidade_desc"),
        LayoutAliasCreate(nome_fisico="TP_ESFERA_ADM", destino_raw="esfera_administrativa"),
        LayoutAliasCreate(nome_fisico="ST_VINCULO_SUS", destino_raw="vinculo_sus"),
        LayoutAliasCreate(nome_fisico="QT_LEITO_EXIST", destino_raw="leitos_existentes"),
        LayoutAliasCreate(nome_fisico="QT_LEITO_SUS", destino_raw="leitos_sus"),
        LayoutAliasCreate(nome_fisico="NU_LATITUDE", destino_raw="latitude"),
        LayoutAliasCreate(nome_fisico="NU_LONGITUDE", destino_raw="longitude"),
        LayoutAliasCreate(nome_fisico="TP_ATIVIDADE", destino_raw="situacao"),
        LayoutAliasCreate(nome_fisico="Fonte", destino_raw="fonte_publicacao"),
    ]:
        alias.layout_versao_id = layout_versao_id
        await service.criar_alias(layout_id, alias)

    await service.atualizar_status_layout(
        layout_id,
        StatusLayoutUpdateRequest(
            status="ativo",
            layout_versao_id=layout_versao_id,
            motivo="bootstrap_fase2_cnes",
        ),
    )

    get_mongo_client().close()


if __name__ == "__main__":
    asyncio.run(bootstrap())
