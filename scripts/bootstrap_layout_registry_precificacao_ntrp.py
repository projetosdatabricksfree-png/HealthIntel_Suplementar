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
        "dataset_codigo": "ntrp_area_comercializacao",
        "nome": "NTRP — Área de Comercialização",
        "descricao": "Normas de regulação de preços: área de comercialização por produto.",
        "tabela_raw_destino": "bruto_ans.ntrp_area_comercializacao",
        "ftp_path": "NTRP/area_comercializacao/",
        "layout_id": "layout_ntrp_area_comercializacao_csv",
        "colunas": [
            ColunaLayout(nome_canonico="competencia", tipo="string"),
            ColunaLayout(nome_canonico="registro_ans", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="codigo_plano", tipo="string"),
            ColunaLayout(nome_canonico="cd_municipio", tipo="string"),
            ColunaLayout(nome_canonico="nm_municipio", tipo="string"),
            ColunaLayout(nome_canonico="sg_uf", tipo="string"),
            ColunaLayout(nome_canonico="area_comercializacao", tipo="string"),
        ],
        "aliases": [
            ("COMPETENCIA", "competencia"),
            ("CD_OPERADORA", "registro_ans"),
            ("REGISTRO_ANS", "registro_ans"),
            ("CD_PLANO", "codigo_plano"),
            ("CD_MUNICIPIO", "cd_municipio"),
            ("NM_MUNICIPIO", "nm_municipio"),
            ("SG_UF", "sg_uf"),
            ("AREA_COMERCIALIZACAO", "area_comercializacao"),
        ],
    },
    {
        "dataset_codigo": "painel_precificacao",
        "nome": "Painel de Precificação de Planos",
        "descricao": "Mensalidades médias, mínimas e máximas por plano, segmentação e faixa etária.",  # noqa: E501
        "tabela_raw_destino": "bruto_ans.painel_precificacao",
        "ftp_path": "PAINEL_PRECIFICACAO/",
        "layout_id": "layout_painel_precificacao_csv",
        "colunas": [
            ColunaLayout(nome_canonico="competencia", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="registro_ans", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="codigo_plano", tipo="string"),
            ColunaLayout(nome_canonico="segmentacao", tipo="string"),
            ColunaLayout(nome_canonico="faixa_etaria", tipo="string"),
            ColunaLayout(nome_canonico="sg_uf", tipo="string"),
            ColunaLayout(nome_canonico="tipo_contratacao", tipo="string"),
            ColunaLayout(nome_canonico="vl_mensalidade_media", tipo="decimal"),
            ColunaLayout(nome_canonico="vl_mensalidade_min", tipo="decimal"),
            ColunaLayout(nome_canonico="vl_mensalidade_max", tipo="decimal"),
            ColunaLayout(nome_canonico="qt_beneficiarios", tipo="integer"),
        ],
        "aliases": [
            ("COMPETENCIA", "competencia"),
            ("CD_OPERADORA", "registro_ans"),
            ("REGISTRO_ANS", "registro_ans"),
            ("CD_PLANO", "codigo_plano"),
            ("SEGMENTACAO", "segmentacao"),
            ("FAIXA_ETARIA", "faixa_etaria"),
            ("SG_UF", "sg_uf"),
            ("TIPO_CONTRATACAO", "tipo_contratacao"),
            ("VL_MENSALIDADE_MEDIA", "vl_mensalidade_media"),
            ("VL_MENSALIDADE_MIN", "vl_mensalidade_min"),
            ("VL_MENSALIDADE_MAX", "vl_mensalidade_max"),
            ("QT_BENEFICIARIOS", "qt_beneficiarios"),
        ],
    },
    {
        "dataset_codigo": "percentual_reajuste_agrupamento",
        "nome": "Percentual de Reajuste por Agrupamento",
        "descricao": "Percentuais de reajuste anuais aprovados por operadora e agrupamento.",
        "tabela_raw_destino": "bruto_ans.percentual_reajuste_agrupamento",
        "ftp_path": "PERCENTUAL_REAJUSTE/",
        "layout_id": "layout_percentual_reajuste_agrupamento_csv",
        "colunas": [
            ColunaLayout(nome_canonico="competencia", tipo="string"),
            ColunaLayout(nome_canonico="registro_ans", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="tipo_contratacao", tipo="string"),
            ColunaLayout(nome_canonico="agrupamento", tipo="string"),
            ColunaLayout(nome_canonico="percentual_reajuste", tipo="decimal"),
            ColunaLayout(nome_canonico="data_aplicacao", tipo="date"),
        ],
        "aliases": [
            ("COMPETENCIA", "competencia"),
            ("CD_OPERADORA", "registro_ans"),
            ("REGISTRO_ANS", "registro_ans"),
            ("TIPO_CONTRATACAO", "tipo_contratacao"),
            ("AGRUPAMENTO", "agrupamento"),
            ("PCT_REAJUSTE", "percentual_reajuste"),
            ("DT_APLICACAO", "data_aplicacao"),
        ],
    },
    {
        "dataset_codigo": "ntrp_vcm_faixa_etaria",
        "nome": "NTRP — VCM por Faixa Etária",
        "descricao": "Valor Comercial Médio por plano e faixa etária.",
        "tabela_raw_destino": "bruto_ans.ntrp_vcm_faixa_etaria",
        "ftp_path": "NTRP/vcm_faixa_etaria/",
        "layout_id": "layout_ntrp_vcm_faixa_etaria_csv",
        "colunas": [
            ColunaLayout(nome_canonico="competencia", tipo="string"),
            ColunaLayout(nome_canonico="registro_ans", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="codigo_plano", tipo="string"),
            ColunaLayout(nome_canonico="faixa_etaria", tipo="string"),
            ColunaLayout(nome_canonico="sg_uf", tipo="string"),
            ColunaLayout(nome_canonico="vcm", tipo="decimal"),
            ColunaLayout(nome_canonico="vl_minimo", tipo="decimal"),
            ColunaLayout(nome_canonico="vl_maximo", tipo="decimal"),
        ],
        "aliases": [
            ("COMPETENCIA", "competencia"),
            ("CD_OPERADORA", "registro_ans"),
            ("REGISTRO_ANS", "registro_ans"),
            ("CD_PLANO", "codigo_plano"),
            ("FAIXA_ETARIA", "faixa_etaria"),
            ("SG_UF", "sg_uf"),
            ("VCM", "vcm"),
            ("VL_MINIMO", "vl_minimo"),
            ("VL_MAXIMO", "vl_maximo"),
        ],
    },
    {
        "dataset_codigo": "valor_comercial_medio_municipio",
        "nome": "Valor Comercial Médio por Município",
        "descricao": "VCM médio de planos por município, segmentação e faixa etária.",
        "tabela_raw_destino": "bruto_ans.valor_comercial_medio_municipio",
        "ftp_path": "VCM_MUNICIPIO/",
        "layout_id": "layout_vcm_municipio_csv",
        "colunas": [
            ColunaLayout(nome_canonico="competencia", tipo="string"),
            ColunaLayout(nome_canonico="cd_municipio", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="nm_municipio", tipo="string"),
            ColunaLayout(nome_canonico="sg_uf", tipo="string"),
            ColunaLayout(nome_canonico="segmentacao", tipo="string"),
            ColunaLayout(nome_canonico="faixa_etaria", tipo="string"),
            ColunaLayout(nome_canonico="vcm_municipio", tipo="decimal"),
            ColunaLayout(nome_canonico="qt_planos", tipo="integer"),
        ],
        "aliases": [
            ("COMPETENCIA", "competencia"),
            ("CD_MUNICIPIO", "cd_municipio"),
            ("NM_MUNICIPIO", "nm_municipio"),
            ("SG_UF", "sg_uf"),
            ("SEGMENTACAO", "segmentacao"),
            ("FAIXA_ETARIA", "faixa_etaria"),
            ("VCM_MUNICIPIO", "vcm_municipio"),
            ("QT_PLANOS", "qt_planos"),
        ],
    },
    {
        "dataset_codigo": "faixa_preco",
        "nome": "Faixa de Preço por Plano e Faixa Etária",
        "descricao": "Faixas de preço mínimo e máximo por plano e faixa etária.",
        "tabela_raw_destino": "bruto_ans.faixa_preco",
        "ftp_path": "FAIXA_PRECO/",
        "layout_id": "layout_faixa_preco_csv",
        "colunas": [
            ColunaLayout(nome_canonico="competencia", tipo="string"),
            ColunaLayout(nome_canonico="registro_ans", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="codigo_plano", tipo="string"),
            ColunaLayout(nome_canonico="faixa_etaria", tipo="string"),
            ColunaLayout(nome_canonico="sg_uf", tipo="string"),
            ColunaLayout(nome_canonico="vl_faixa_min", tipo="decimal"),
            ColunaLayout(nome_canonico="vl_faixa_max", tipo="decimal"),
        ],
        "aliases": [
            ("COMPETENCIA", "competencia"),
            ("CD_OPERADORA", "registro_ans"),
            ("REGISTRO_ANS", "registro_ans"),
            ("CD_PLANO", "codigo_plano"),
            ("FAIXA_ETARIA", "faixa_etaria"),
            ("SG_UF", "sg_uf"),
            ("VL_FAIXA_MIN", "vl_faixa_min"),
            ("VL_FAIXA_MAX", "vl_faixa_max"),
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

        print("Bootstrap de layouts Precificação/NTRP concluído.")
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(bootstrap())
