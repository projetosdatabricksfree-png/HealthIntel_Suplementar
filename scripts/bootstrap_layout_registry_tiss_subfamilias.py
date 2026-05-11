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

_ANS_BASE = "https://dadosabertos.ans.gov.br/FTP/PDA/"

_DATASETS = [
    {
        "dataset_codigo": "tiss_ambulatorial",
        "nome": "TISS Ambulatorial por Operadora",
        "descricao": "Utilização ambulatorial TISS por operadora e competência (retenção 24 meses).",  # noqa: E501
        "tabela_raw_destino": "bruto_ans.tiss_ambulatorial",
        "ftp_path": "TISS/TISS_AMBULATORIAL/",
        "layout_id": "layout_tiss_ambulatorial_csv",
        "colunas": [
            ColunaLayout(nome_canonico="competencia", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="registro_ans", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="codigo_plano", tipo="string"),
            ColunaLayout(nome_canonico="tipo_atendimento", tipo="string"),
            ColunaLayout(nome_canonico="qt_guias", tipo="integer"),
            ColunaLayout(nome_canonico="qt_procedimentos", tipo="integer"),
            ColunaLayout(nome_canonico="vl_apresentado", tipo="decimal"),
            ColunaLayout(nome_canonico="vl_aprovado", tipo="decimal"),
            ColunaLayout(nome_canonico="vl_glosado", tipo="decimal"),
        ],
        "aliases": [
            ("COMPETENCIA", "competencia"),
            ("CD_OPERADORA", "registro_ans"),
            ("REGISTRO_ANS", "registro_ans"),
            ("CD_PLANO", "codigo_plano"),
            ("TP_ATENDIMENTO", "tipo_atendimento"),
            ("QT_GUIAS", "qt_guias"),
            ("QT_PROCEDIMENTOS", "qt_procedimentos"),
            ("VL_APRESENTADO", "vl_apresentado"),
            ("VL_APROVADO", "vl_aprovado"),
            ("VL_GLOSADO", "vl_glosado"),
        ],
    },
    {
        "dataset_codigo": "tiss_hospitalar",
        "nome": "TISS Hospitalar por Operadora",
        "descricao": "Utilização hospitalar TISS por operadora e competência (retenção 24 meses).",
        "tabela_raw_destino": "bruto_ans.tiss_hospitalar",
        "ftp_path": "TISS/TISS_HOSPITALAR/",
        "layout_id": "layout_tiss_hospitalar_csv",
        "colunas": [
            ColunaLayout(nome_canonico="competencia", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="registro_ans", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="codigo_plano", tipo="string"),
            ColunaLayout(nome_canonico="tipo_internacao", tipo="string"),
            ColunaLayout(nome_canonico="qt_internacoes", tipo="integer"),
            ColunaLayout(nome_canonico="qt_diarias", tipo="integer"),
            ColunaLayout(nome_canonico="vl_apresentado", tipo="decimal"),
            ColunaLayout(nome_canonico="vl_aprovado", tipo="decimal"),
        ],
        "aliases": [
            ("COMPETENCIA", "competencia"),
            ("CD_OPERADORA", "registro_ans"),
            ("REGISTRO_ANS", "registro_ans"),
            ("CD_PLANO", "codigo_plano"),
            ("TP_INTERNACAO", "tipo_internacao"),
            ("QT_INTERNACOES", "qt_internacoes"),
            ("QT_DIARIAS", "qt_diarias"),
            ("VL_APRESENTADO", "vl_apresentado"),
            ("VL_APROVADO", "vl_aprovado"),
        ],
    },
    {
        "dataset_codigo": "tiss_dados_plano",
        "nome": "TISS Dados de Planos",
        "descricao": "Dados agregados de planos na TISS por operadora e competência.",
        "tabela_raw_destino": "bruto_ans.tiss_dados_plano",
        "ftp_path": "TISS/TISS_DADOS_DE_PLANOS/",
        "layout_id": "layout_tiss_dados_plano_csv",
        "colunas": [
            ColunaLayout(nome_canonico="competencia", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="registro_ans", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="codigo_plano", tipo="string"),
            ColunaLayout(nome_canonico="qt_beneficiarios_ativos", tipo="integer"),
            ColunaLayout(nome_canonico="qt_eventos_medicos", tipo="integer"),
            ColunaLayout(nome_canonico="vl_total_pago", tipo="decimal"),
        ],
        "aliases": [
            ("COMPETENCIA", "competencia"),
            ("CD_OPERADORA", "registro_ans"),
            ("REGISTRO_ANS", "registro_ans"),
            ("CD_PLANO", "codigo_plano"),
            ("QT_BENEFICIARIOS_ATIVOS", "qt_beneficiarios_ativos"),
            ("QT_EVENTOS_MEDICOS", "qt_eventos_medicos"),
            ("VL_TOTAL_PAGO", "vl_total_pago"),
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

        print("Bootstrap de layouts TISS Subfamílias concluído.")
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(bootstrap())
