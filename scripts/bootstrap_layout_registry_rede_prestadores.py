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
)
from mongo_layout_service.app.services.layout_service import LayoutService

_DATASETS = [
    {
        "dataset_codigo": "operadora_cancelada",
        "nome": "Operadoras Canceladas",
        "descricao": "Cadastro de operadoras com registro ANS cancelado.",
        "tabela_raw_destino": "bruto_ans.operadora_cancelada",
        "ftp_path": "OPERADORAS_DE_PLANOS_DE_SAUDE_DO_BRASIL/",
        "layout_id": "layout_operadora_cancelada_csv",
        "colunas": [
            ColunaLayout(nome_canonico="registro_ans", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="razao_social", tipo="string"),
            ColunaLayout(nome_canonico="cnpj", tipo="string"),
            ColunaLayout(nome_canonico="modalidade", tipo="string"),
            ColunaLayout(nome_canonico="data_cancelamento", tipo="date"),
            ColunaLayout(nome_canonico="motivo_cancelamento", tipo="string"),
            ColunaLayout(nome_canonico="sg_uf", tipo="string"),
        ],
        "aliases": [
            ("CD_OPERADORA", "registro_ans"),
            ("REGISTRO_ANS", "registro_ans"),
            ("RAZAO_SOCIAL", "razao_social"),
            ("CNPJ", "cnpj"),
            ("MODALIDADE", "modalidade"),
            ("DT_CANCELAMENTO", "data_cancelamento"),
            ("MOTIVO_CANCELAMENTO", "motivo_cancelamento"),
            ("SG_UF", "sg_uf"),
        ],
    },
    {
        "dataset_codigo": "operadora_acreditada",
        "nome": "Operadoras Acreditadas",
        "descricao": "Operadoras com acreditação de qualidade vigente.",
        "tabela_raw_destino": "bruto_ans.operadora_acreditada",
        "ftp_path": "ACREDITACAO/operadoras/",
        "layout_id": "layout_operadora_acreditada_csv",
        "colunas": [
            ColunaLayout(nome_canonico="registro_ans", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="razao_social", tipo="string"),
            ColunaLayout(nome_canonico="acreditadora", tipo="string"),
            ColunaLayout(nome_canonico="nivel_acreditacao", tipo="string"),
            ColunaLayout(nome_canonico="data_acreditacao", tipo="date"),
            ColunaLayout(nome_canonico="data_validade", tipo="date"),
        ],
        "aliases": [
            ("CD_OPERADORA", "registro_ans"),
            ("REGISTRO_ANS", "registro_ans"),
            ("RAZAO_SOCIAL", "razao_social"),
            ("ACREDITADORA", "acreditadora"),
            ("NIVEL_ACREDITACAO", "nivel_acreditacao"),
            ("DT_ACREDITACAO", "data_acreditacao"),
            ("DT_VALIDADE", "data_validade"),
        ],
    },
    {
        "dataset_codigo": "prestador_acreditado",
        "nome": "Prestadores Acreditados",
        "descricao": "Prestadores de saúde com acreditação vigente.",
        "tabela_raw_destino": "bruto_ans.prestador_acreditado",
        "ftp_path": "ACREDITACAO/prestadores/",
        "layout_id": "layout_prestador_acreditado_csv",
        "colunas": [
            ColunaLayout(nome_canonico="cnes", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="nm_prestador", tipo="string"),
            ColunaLayout(nome_canonico="cnpj", tipo="string"),
            ColunaLayout(nome_canonico="cd_municipio", tipo="string"),
            ColunaLayout(nome_canonico="nm_municipio", tipo="string"),
            ColunaLayout(nome_canonico="sg_uf", tipo="string"),
            ColunaLayout(nome_canonico="acreditadora", tipo="string"),
            ColunaLayout(nome_canonico="nivel_acreditacao", tipo="string"),
            ColunaLayout(nome_canonico="data_acreditacao", tipo="date"),
            ColunaLayout(nome_canonico="data_validade", tipo="date"),
        ],
        "aliases": [
            ("CNES", "cnes"),
            ("CD_CNES", "cnes"),
            ("NM_PRESTADOR", "nm_prestador"),
            ("CNPJ", "cnpj"),
            ("CD_MUNICIPIO", "cd_municipio"),
            ("NM_MUNICIPIO", "nm_municipio"),
            ("SG_UF", "sg_uf"),
            ("ACREDITADORA", "acreditadora"),
            ("NIVEL_ACREDITACAO", "nivel_acreditacao"),
            ("DT_ACREDITACAO", "data_acreditacao"),
            ("DT_VALIDADE", "data_validade"),
        ],
    },
    {
        "dataset_codigo": "produto_prestador_hospitalar",
        "nome": "Produto x Prestador Hospitalar",
        "descricao": "Vínculo de produtos de saúde suplementar com prestadores hospitalares.",
        "tabela_raw_destino": "bruto_ans.produto_prestador_hospitalar",
        "ftp_path": "PRODUTO_PRESTADOR/hospitalar/",
        "layout_id": "layout_produto_prestador_hospitalar_csv",
        "colunas": [
            ColunaLayout(nome_canonico="competencia", tipo="string"),
            ColunaLayout(nome_canonico="registro_ans", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="codigo_produto", tipo="string"),
            ColunaLayout(nome_canonico="cnes", tipo="string"),
            ColunaLayout(nome_canonico="nm_prestador", tipo="string"),
            ColunaLayout(nome_canonico="cd_municipio", tipo="string"),
            ColunaLayout(nome_canonico="sg_uf", tipo="string"),
            ColunaLayout(nome_canonico="tipo_vinculo", tipo="string"),
        ],
        "aliases": [
            ("COMPETENCIA", "competencia"),
            ("CD_OPERADORA", "registro_ans"),
            ("REGISTRO_ANS", "registro_ans"),
            ("CD_PRODUTO", "codigo_produto"),
            ("CNES", "cnes"),
            ("NM_PRESTADOR", "nm_prestador"),
            ("CD_MUNICIPIO", "cd_municipio"),
            ("SG_UF", "sg_uf"),
            ("TP_VINCULO", "tipo_vinculo"),
        ],
    },
    {
        "dataset_codigo": "operadora_prestador_nao_hospitalar",
        "nome": "Operadora x Prestador Não Hospitalar",
        "descricao": "Vínculo de operadoras com prestadores não hospitalares.",
        "tabela_raw_destino": "bruto_ans.operadora_prestador_nao_hospitalar",
        "ftp_path": "PRODUTO_PRESTADOR/nao_hospitalar/",
        "layout_id": "layout_operadora_prestador_nao_hospitalar_csv",
        "colunas": [
            ColunaLayout(nome_canonico="competencia", tipo="string"),
            ColunaLayout(nome_canonico="registro_ans", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="cnes", tipo="string"),
            ColunaLayout(nome_canonico="nm_prestador", tipo="string"),
            ColunaLayout(nome_canonico="cd_municipio", tipo="string"),
            ColunaLayout(nome_canonico="sg_uf", tipo="string"),
            ColunaLayout(nome_canonico="tipo_servico", tipo="string"),
            ColunaLayout(nome_canonico="tipo_vinculo", tipo="string"),
        ],
        "aliases": [
            ("COMPETENCIA", "competencia"),
            ("CD_OPERADORA", "registro_ans"),
            ("REGISTRO_ANS", "registro_ans"),
            ("CNES", "cnes"),
            ("NM_PRESTADOR", "nm_prestador"),
            ("CD_MUNICIPIO", "cd_municipio"),
            ("SG_UF", "sg_uf"),
            ("TP_SERVICO", "tipo_servico"),
            ("TP_VINCULO", "tipo_vinculo"),
        ],
    },
    {
        "dataset_codigo": "solicitacao_alteracao_rede_hospitalar",
        "nome": "Solicitações de Alteração de Rede Hospitalar",
        "descricao": "Solicitações de inclusão/exclusão de prestadores hospitalares por operadora.",
        "tabela_raw_destino": "bruto_ans.solicitacao_alteracao_rede_hospitalar",
        "ftp_path": "ALTERACAO_REDE/",
        "layout_id": "layout_solicitacao_alteracao_rede_csv",
        "colunas": [
            ColunaLayout(nome_canonico="competencia", tipo="string"),
            ColunaLayout(nome_canonico="registro_ans", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="nu_solicitacao", tipo="string"),
            ColunaLayout(nome_canonico="tipo_alteracao", tipo="string"),
            ColunaLayout(nome_canonico="cnes", tipo="string"),
            ColunaLayout(nome_canonico="nm_prestador", tipo="string"),
            ColunaLayout(nome_canonico="cd_municipio", tipo="string"),
            ColunaLayout(nome_canonico="sg_uf", tipo="string"),
            ColunaLayout(nome_canonico="data_solicitacao", tipo="date"),
            ColunaLayout(nome_canonico="status_solicitacao", tipo="string"),
        ],
        "aliases": [
            ("COMPETENCIA", "competencia"),
            ("CD_OPERADORA", "registro_ans"),
            ("REGISTRO_ANS", "registro_ans"),
            ("NU_SOLICITACAO", "nu_solicitacao"),
            ("TP_ALTERACAO", "tipo_alteracao"),
            ("CNES", "cnes"),
            ("NM_PRESTADOR", "nm_prestador"),
            ("CD_MUNICIPIO", "cd_municipio"),
            ("SG_UF", "sg_uf"),
            ("DT_SOLICITACAO", "data_solicitacao"),
            ("ST_SOLICITACAO", "status_solicitacao"),
        ],
    },
]


async def bootstrap() -> None:
    client = get_mongo_client()
    try:
        repository = LayoutRepository(get_database())
        service = LayoutService(repository)
        await service.inicializar()

        for ds in _DATASETS:
            dataset = FonteDatasetCreate(
                dataset_codigo=ds["dataset_codigo"],
                nome=ds["nome"],
                descricao=ds["descricao"],
                formato_esperado="csv",
                tabela_raw_destino=ds["tabela_raw_destino"],
            )
            await repository.upsert_dataset(dataset)

            layout = LayoutCreate(
                dataset_codigo=ds["dataset_codigo"],
                nome=ds["nome"],
                descricao=ds["descricao"],
                tabela_raw_destino=ds["tabela_raw_destino"],
                formato_esperado="csv",
            )
            layout_id = ds["layout_id"]
            if not await repository.obter_layout(layout_id):
                await service.criar_layout(layout)

            layout_versao_id = f"{layout_id}:v1"
            if not await repository.obter_versao(layout_versao_id):
                await service.criar_versao_layout(
                    layout_id,
                    LayoutVersaoCreate(versao="v1", colunas=ds["colunas"]),
                )

            for nome_fisico, destino_raw in ds["aliases"]:
                try:
                    await service.criar_alias(
                        layout_id,
                        layout_versao_id,
                        LayoutAliasCreate(nome_fisico=nome_fisico, destino_raw=destino_raw),
                    )
                except Exception:
                    pass

        print("Bootstrap de layouts Rede/Prestadores concluído.")
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(bootstrap())
