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
        "dataset_codigo": "ressarcimento_beneficiario_abi",
        "nome": "Ressarcimento SUS — Beneficiário ABI",
        "descricao": "Ressarcimento ao SUS: autorizações de internação por beneficiário.",
        "tabela_raw_destino": "bruto_ans.ressarcimento_beneficiario_abi",
        "ftp_path": "RESSARCIMENTO_AO_SUS/",
        "layout_id": "layout_ressarcimento_beneficiario_abi_csv",
        "colunas": [
            ColunaLayout(nome_canonico="competencia", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="registro_ans", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="nu_abi", tipo="string"),
            ColunaLayout(nome_canonico="cd_municipio", tipo="string"),
            ColunaLayout(nome_canonico="nm_municipio", tipo="string"),
            ColunaLayout(nome_canonico="sg_uf", tipo="string"),
            ColunaLayout(nome_canonico="qt_beneficiarios", tipo="integer"),
            ColunaLayout(nome_canonico="vl_ressarcimento", tipo="decimal"),
            ColunaLayout(nome_canonico="status_ressarcimento", tipo="string"),
        ],
        "aliases": [
            ("COMPETENCIA", "competencia"),
            ("CD_OPERADORA", "registro_ans"),
            ("REGISTRO_ANS", "registro_ans"),
            ("NU_ABI", "nu_abi"),
            ("CD_MUNICIPIO", "cd_municipio"),
            ("NM_MUNICIPIO", "nm_municipio"),
            ("SG_UF", "sg_uf"),
            ("QT_BENEFICIARIOS", "qt_beneficiarios"),
            ("VL_RESSARCIMENTO", "vl_ressarcimento"),
            ("ST_RESSARCIMENTO", "status_ressarcimento"),
        ],
    },
    {
        "dataset_codigo": "ressarcimento_sus_operadora_plano",
        "nome": "Ressarcimento SUS — Operadora/Plano",
        "descricao": "Ressarcimento ao SUS: totais por operadora e plano.",
        "tabela_raw_destino": "bruto_ans.ressarcimento_sus_operadora_plano",
        "ftp_path": "RESSARCIMENTO_AO_SUS/operadora_plano/",
        "layout_id": "layout_ressarcimento_sus_operadora_plano_csv",
        "colunas": [
            ColunaLayout(nome_canonico="competencia", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="registro_ans", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="codigo_plano", tipo="string"),
            ColunaLayout(nome_canonico="qt_autorizacoes", tipo="integer"),
            ColunaLayout(nome_canonico="vl_cobrado", tipo="decimal"),
            ColunaLayout(nome_canonico="vl_pago", tipo="decimal"),
            ColunaLayout(nome_canonico="vl_pendente", tipo="decimal"),
            ColunaLayout(nome_canonico="status_cobranca", tipo="string"),
        ],
        "aliases": [
            ("COMPETENCIA", "competencia"),
            ("CD_OPERADORA", "registro_ans"),
            ("REGISTRO_ANS", "registro_ans"),
            ("CD_PLANO", "codigo_plano"),
            ("QT_AUTORIZACOES", "qt_autorizacoes"),
            ("VL_COBRADO", "vl_cobrado"),
            ("VL_PAGO", "vl_pago"),
            ("VL_PENDENTE", "vl_pendente"),
            ("ST_COBRANCA", "status_cobranca"),
        ],
    },
    {
        "dataset_codigo": "ressarcimento_hc",
        "nome": "Ressarcimento SUS — Habilitação de Crédito (HC)",
        "descricao": "Ressarcimento ao SUS: habilitações de crédito por operadora.",
        "tabela_raw_destino": "bruto_ans.ressarcimento_hc",
        "ftp_path": "RESSARCIMENTO_AO_SUS/hc/",
        "layout_id": "layout_ressarcimento_hc_csv",
        "colunas": [
            ColunaLayout(nome_canonico="competencia", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="registro_ans", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="nu_hc", tipo="string"),
            ColunaLayout(nome_canonico="vl_hc", tipo="decimal"),
            ColunaLayout(nome_canonico="status_hc", tipo="string"),
            ColunaLayout(nome_canonico="fase_cobranca", tipo="string"),
        ],
        "aliases": [
            ("COMPETENCIA", "competencia"),
            ("CD_OPERADORA", "registro_ans"),
            ("REGISTRO_ANS", "registro_ans"),
            ("NU_HC", "nu_hc"),
            ("VL_HC", "vl_hc"),
            ("ST_HC", "status_hc"),
            ("FASE_COBRANCA", "fase_cobranca"),
        ],
    },
    {
        "dataset_codigo": "ressarcimento_cobranca_arrecadacao",
        "nome": "Ressarcimento SUS — Cobrança e Arrecadação",
        "descricao": "Totais de cobrança e arrecadação do ressarcimento ao SUS por operadora.",
        "tabela_raw_destino": "bruto_ans.ressarcimento_cobranca_arrecadacao",
        "ftp_path": "RESSARCIMENTO_AO_SUS/cobranca/",
        "layout_id": "layout_ressarcimento_cobranca_arrecadacao_csv",
        "colunas": [
            ColunaLayout(nome_canonico="competencia", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="registro_ans", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="vl_cobrado", tipo="decimal"),
            ColunaLayout(nome_canonico="vl_arrecadado", tipo="decimal"),
            ColunaLayout(nome_canonico="vl_inadimplente", tipo="decimal"),
            ColunaLayout(nome_canonico="qt_guias", tipo="integer"),
        ],
        "aliases": [
            ("COMPETENCIA", "competencia"),
            ("CD_OPERADORA", "registro_ans"),
            ("REGISTRO_ANS", "registro_ans"),
            ("VL_COBRADO", "vl_cobrado"),
            ("VL_ARRECADADO", "vl_arrecadado"),
            ("VL_INADIMPLENTE", "vl_inadimplente"),
            ("QT_GUIAS", "qt_guias"),
        ],
    },
    {
        "dataset_codigo": "ressarcimento_indice_pagamento",
        "nome": "Ressarcimento SUS — Índice de Efetivo Pagamento",
        "descricao": "Índice de efetivo pagamento do ressarcimento ao SUS por operadora.",
        "tabela_raw_destino": "bruto_ans.ressarcimento_indice_pagamento",
        "ftp_path": "RESSARCIMENTO_AO_SUS/indice/",
        "layout_id": "layout_ressarcimento_indice_pagamento_csv",
        "colunas": [
            ColunaLayout(nome_canonico="competencia", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="registro_ans", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="indice_efetivo_pagamento", tipo="decimal"),
            ColunaLayout(nome_canonico="valor_total_cobrado", tipo="decimal"),
            ColunaLayout(nome_canonico="valor_total_pago", tipo="decimal"),
        ],
        "aliases": [
            ("COMPETENCIA", "competencia"),
            ("CD_OPERADORA", "registro_ans"),
            ("REGISTRO_ANS", "registro_ans"),
            ("IN_EFETIVO_PAGAMENTO", "indice_efetivo_pagamento"),
            ("VL_TOTAL_COBRADO", "valor_total_cobrado"),
            ("VL_TOTAL_PAGO", "valor_total_pago"),
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

        print("Bootstrap de layouts Ressarcimento SUS concluído.")
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(bootstrap())
