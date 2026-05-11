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
        "dataset_codigo": "beneficiario_regiao_geografica",
        "nome": "Beneficiários por Região Geográfica",
        "descricao": "Distribuição de beneficiários de planos de saúde por região e UF.",
        "tabela_raw_destino": "bruto_ans.beneficiario_regiao_geografica",
        "ftp_path": "BENEFICIARIOS/beneficiario_regiao_geografica/",
        "layout_id": "layout_beneficiario_regiao_geografica_csv",
        "colunas": [
            ColunaLayout(nome_canonico="competencia", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="cd_regiao", tipo="string"),
            ColunaLayout(nome_canonico="nm_regiao", tipo="string"),
            ColunaLayout(nome_canonico="sg_uf", tipo="string"),
            ColunaLayout(nome_canonico="tipo_plano", tipo="string"),
            ColunaLayout(nome_canonico="segmentacao", tipo="string"),
            ColunaLayout(nome_canonico="qt_beneficiarios", tipo="integer"),
        ],
        "aliases": [
            ("COMPETENCIA", "competencia"),
            ("CD_REGIAO", "cd_regiao"),
            ("NM_REGIAO", "nm_regiao"),
            ("SG_UF", "sg_uf"),
            ("TP_PLANO", "tipo_plano"),
            ("SEGMENTACAO", "segmentacao"),
            ("QT_BENEFICIARIOS", "qt_beneficiarios"),
        ],
    },
    {
        "dataset_codigo": "beneficiario_informacao_consolidada",
        "nome": "Beneficiários — Informação Consolidada",
        "descricao": "Beneficiários por município, segmentação, faixa etária e sexo.",
        "tabela_raw_destino": "bruto_ans.beneficiario_informacao_consolidada",
        "ftp_path": "BENEFICIARIOS/beneficiario_informacao_consolidada/",
        "layout_id": "layout_beneficiario_informacao_consolidada_csv",
        "colunas": [
            ColunaLayout(nome_canonico="competencia", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="sg_uf", tipo="string"),
            ColunaLayout(nome_canonico="cd_municipio", tipo="string"),
            ColunaLayout(nome_canonico="nm_municipio", tipo="string"),
            ColunaLayout(nome_canonico="segmentacao", tipo="string"),
            ColunaLayout(nome_canonico="tipo_contratacao", tipo="string"),
            ColunaLayout(nome_canonico="faixa_etaria", tipo="string"),
            ColunaLayout(nome_canonico="sexo", tipo="string"),
            ColunaLayout(nome_canonico="qt_beneficiarios", tipo="integer"),
        ],
        "aliases": [
            ("COMPETENCIA", "competencia"),
            ("SG_UF", "sg_uf"),
            ("CD_MUNICIPIO", "cd_municipio"),
            ("NM_MUNICIPIO", "nm_municipio"),
            ("SEGMENTACAO", "segmentacao"),
            ("TIPO_CONTRATACAO", "tipo_contratacao"),
            ("FAIXA_ETARIA", "faixa_etaria"),
            ("SEXO", "sexo"),
            ("QT_BENEFICIARIOS", "qt_beneficiarios"),
        ],
    },
    {
        "dataset_codigo": "taxa_cobertura_plano",
        "nome": "Taxa de Cobertura de Planos de Saúde",
        "descricao": "Proporção da população coberta por planos de saúde por município.",
        "tabela_raw_destino": "bruto_ans.taxa_cobertura_plano",
        "ftp_path": "BENEFICIARIOS/taxa_cobertura_plano/",
        "layout_id": "layout_taxa_cobertura_plano_csv",
        "colunas": [
            ColunaLayout(nome_canonico="competencia", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="sg_uf", tipo="string"),
            ColunaLayout(nome_canonico="cd_municipio", tipo="string"),
            ColunaLayout(nome_canonico="nm_municipio", tipo="string"),
            ColunaLayout(nome_canonico="populacao_total", tipo="integer"),
            ColunaLayout(nome_canonico="qt_beneficiarios", tipo="integer"),
            ColunaLayout(nome_canonico="taxa_cobertura", tipo="decimal"),
        ],
        "aliases": [
            ("COMPETENCIA", "competencia"),
            ("SG_UF", "sg_uf"),
            ("CD_MUNICIPIO", "cd_municipio"),
            ("NM_MUNICIPIO", "nm_municipio"),
            ("POPULACAO_TOTAL", "populacao_total"),
            ("QT_BENEFICIARIOS", "qt_beneficiarios"),
            ("TAXA_COBERTURA", "taxa_cobertura"),
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

        print("Bootstrap de layouts Beneficiários/Cobertura concluído.")
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(bootstrap())
