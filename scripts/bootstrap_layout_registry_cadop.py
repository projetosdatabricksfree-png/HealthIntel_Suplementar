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
    StatusLayoutUpdateRequest,
)
from mongo_layout_service.app.services.layout_service import LayoutService


async def bootstrap() -> None:
    repository = LayoutRepository(get_database())
    service = LayoutService(repository)
    await service.inicializar()
    dataset = FonteDatasetCreate(
        dataset_codigo="cadop",
        nome="CADOP Operadoras Ativas",
        descricao="Cadastro publico de operadoras ativas da ANS.",
        formato_esperado="csv",
        tabela_raw_destino="bruto_ans.cadop",
    )
    await repository.upsert_dataset(dataset)
    layout = LayoutCreate(
        dataset_codigo="cadop",
        nome="CADOP Operadoras Ativas",
        descricao="Layout CSV publico de operadoras ativas.",
        tabela_raw_destino="bruto_ans.cadop",
        formato_esperado="csv",
    )
    layout_id = "layout_cadop_csv"
    if not await repository.obter_layout(layout_id):
        await service.criar_layout(layout)
    layout_versao_id = f"{layout_id}:v1"
    if not await repository.obter_versao(layout_versao_id):
        await service.criar_versao_layout(
            layout_id,
            LayoutVersaoCreate(
                versao="v1",
                colunas=[
                    ColunaLayout(nome_canonico="registro_ans", tipo="string", obrigatorio=True),
                    ColunaLayout(nome_canonico="cnpj", tipo="string", obrigatorio=True),
                    ColunaLayout(nome_canonico="razao_social", tipo="string", obrigatorio=True),
                    ColunaLayout(nome_canonico="nome_fantasia", tipo="string"),
                    ColunaLayout(nome_canonico="modalidade", tipo="string"),
                    ColunaLayout(nome_canonico="cidade", tipo="string"),
                    ColunaLayout(nome_canonico="uf", tipo="string"),
                    ColunaLayout(nome_canonico="competencia", tipo="string"),
                ],
            ),
        )
    for alias in [
        LayoutAliasCreate(nome_fisico="Registro ANS", destino_raw="registro_ans"),
        LayoutAliasCreate(nome_fisico="REGISTRO_OPERADORA", destino_raw="registro_ans"),
        LayoutAliasCreate(nome_fisico="CNPJ", destino_raw="cnpj"),
        LayoutAliasCreate(nome_fisico="Razao Social", destino_raw="razao_social"),
        LayoutAliasCreate(nome_fisico="Razao_Social", destino_raw="razao_social"),
        LayoutAliasCreate(nome_fisico="Nome Fantasia", destino_raw="nome_fantasia"),
        LayoutAliasCreate(nome_fisico="Nome_Fantasia", destino_raw="nome_fantasia"),
        LayoutAliasCreate(nome_fisico="Modalidade", destino_raw="modalidade"),
        LayoutAliasCreate(nome_fisico="Cidade", destino_raw="cidade"),
        LayoutAliasCreate(nome_fisico="UF", destino_raw="uf"),
        LayoutAliasCreate(nome_fisico="Competencia", destino_raw="competencia"),
        LayoutAliasCreate(nome_fisico="Bairro", destino_raw="_ignorado_bairro"),
        LayoutAliasCreate(nome_fisico="CEP", destino_raw="_ignorado_cep"),
        LayoutAliasCreate(nome_fisico="Cargo_Representante", destino_raw="_ignorado_cargo_representante"),
        LayoutAliasCreate(nome_fisico="Complemento", destino_raw="_ignorado_complemento"),
        LayoutAliasCreate(nome_fisico="DDD", destino_raw="_ignorado_ddd"),
        LayoutAliasCreate(nome_fisico="Data_Registro_ANS", destino_raw="_ignorado_data_registro_ans"),
        LayoutAliasCreate(nome_fisico="Endereco_eletronico", destino_raw="_ignorado_endereco_eletronico"),
        LayoutAliasCreate(nome_fisico="Fax", destino_raw="_ignorado_fax"),
        LayoutAliasCreate(nome_fisico="Logradouro", destino_raw="_ignorado_logradouro"),
        LayoutAliasCreate(nome_fisico="Numero", destino_raw="_ignorado_numero"),
        LayoutAliasCreate(nome_fisico="Regiao_de_Comercializacao", destino_raw="_ignorado_regiao_comercializacao"),
        LayoutAliasCreate(nome_fisico="Representante", destino_raw="_ignorado_representante"),
        LayoutAliasCreate(nome_fisico="Telefone", destino_raw="_ignorado_telefone"),
    ]:
        alias.layout_versao_id = layout_versao_id
        await service.criar_alias(layout_id, alias)
    await service.atualizar_status_layout(
        layout_id,
        StatusLayoutUpdateRequest(
            status="ativo",
            layout_versao_id=layout_versao_id,
            motivo="bootstrap_fase4_cadop",
        ),
    )
    get_mongo_client().close()


if __name__ == "__main__":
    asyncio.run(bootstrap())
