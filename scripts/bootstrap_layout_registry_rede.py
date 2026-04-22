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
        dataset_codigo="rede_assistencial",
        nome="Rede assistencial ANS",
        descricao="Cobertura territorial de prestadores e especialidades por operadora.",
        formato_esperado="csv",
        tabela_raw_destino="bruto_ans.rede_prestador_municipio",
    )
    layout = LayoutCreate(
        dataset_codigo="rede_assistencial",
        nome="Rede assistencial ANS",
        descricao="Layout manual para rede assistencial com compatibilidade por municipio.",
        tabela_raw_destino="bruto_ans.rede_prestador_municipio",
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
                    ColunaLayout(nome_canonico="registro_ans", tipo="string", obrigatorio=True),
                    ColunaLayout(nome_canonico="cd_municipio", tipo="string", obrigatorio=True),
                    ColunaLayout(nome_canonico="nm_municipio", tipo="string"),
                    ColunaLayout(nome_canonico="sg_uf", tipo="string"),
                    ColunaLayout(nome_canonico="segmento", tipo="string", obrigatorio=True),
                    ColunaLayout(nome_canonico="tipo_prestador", tipo="string"),
                    ColunaLayout(nome_canonico="qt_prestador", tipo="integer"),
                    ColunaLayout(
                        nome_canonico="qt_especialidade_disponivel",
                        tipo="integer",
                    ),
                    ColunaLayout(nome_canonico="fonte_publicacao", tipo="string"),
                ],
            ),
        )

    for alias in [
        LayoutAliasCreate(nome_fisico="Competencia", destino_raw="competencia"),
        LayoutAliasCreate(nome_fisico="Registro ANS", destino_raw="registro_ans"),
        LayoutAliasCreate(nome_fisico="Codigo IBGE", destino_raw="cd_municipio"),
        LayoutAliasCreate(nome_fisico="CD MUNICIPIO", destino_raw="cd_municipio"),
        LayoutAliasCreate(nome_fisico="Municipio", destino_raw="nm_municipio"),
        LayoutAliasCreate(nome_fisico="UF", destino_raw="sg_uf"),
        LayoutAliasCreate(nome_fisico="Segmento", destino_raw="segmento"),
        LayoutAliasCreate(nome_fisico="Tipo Prestador", destino_raw="tipo_prestador"),
        LayoutAliasCreate(nome_fisico="Qt Prestador", destino_raw="qt_prestador"),
        LayoutAliasCreate(
            nome_fisico="Qt Especialidade Disponivel",
            destino_raw="qt_especialidade_disponivel",
        ),
        LayoutAliasCreate(nome_fisico="Fonte", destino_raw="fonte_publicacao"),
    ]:
        alias.layout_versao_id = layout_versao_id
        await service.criar_alias(layout_id, alias)

    await service.atualizar_status_layout(
        layout_id,
        StatusLayoutUpdateRequest(
            status="ativo",
            layout_versao_id=layout_versao_id,
            motivo="bootstrap_sprint_11",
        ),
    )

    get_mongo_client().close()


if __name__ == "__main__":
    asyncio.run(bootstrap())
