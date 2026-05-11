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
        "dataset_codigo": "penalidade_operadora",
        "nome": "Penalidades a Operadoras",
        "descricao": "Penalidades administrativas aplicadas a operadoras pela ANS.",
        "tabela_raw_destino": "bruto_ans.penalidade_operadora",
        "ftp_path": "PENALIDADES/",
        "layout_id": "layout_penalidade_operadora_csv",
        "colunas": [
            ColunaLayout(nome_canonico="competencia", tipo="string"),
            ColunaLayout(nome_canonico="registro_ans", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="nu_processo", tipo="string"),
            ColunaLayout(nome_canonico="tipo_penalidade", tipo="string"),
            ColunaLayout(nome_canonico="descricao_infracao", tipo="string"),
            ColunaLayout(nome_canonico="vl_multa", tipo="decimal"),
            ColunaLayout(nome_canonico="data_penalidade", tipo="date"),
            ColunaLayout(nome_canonico="status_penalidade", tipo="string"),
        ],
        "aliases": [
            ("COMPETENCIA", "competencia"),
            ("CD_OPERADORA", "registro_ans"),
            ("REGISTRO_ANS", "registro_ans"),
            ("NU_PROCESSO", "nu_processo"),
            ("TP_PENALIDADE", "tipo_penalidade"),
            ("DS_INFRACAO", "descricao_infracao"),
            ("VL_MULTA", "vl_multa"),
            ("DT_PENALIDADE", "data_penalidade"),
            ("ST_PENALIDADE", "status_penalidade"),
        ],
    },
    {
        "dataset_codigo": "monitoramento_garantia_atendimento",
        "nome": "Monitoramento de Garantia de Atendimento",
        "descricao": "Indicadores de garantia de atendimento por operadora.",
        "tabela_raw_destino": "bruto_ans.monitoramento_garantia_atendimento",
        "ftp_path": "GARANTIA_ATENDIMENTO/",
        "layout_id": "layout_monitoramento_garantia_atendimento_csv",
        "colunas": [
            ColunaLayout(nome_canonico="competencia", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="registro_ans", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="tipo_garantia", tipo="string"),
            ColunaLayout(nome_canonico="qt_ocorrencias", tipo="integer"),
            ColunaLayout(nome_canonico="qt_resolvidas", tipo="integer"),
            ColunaLayout(nome_canonico="qt_pendentes", tipo="integer"),
            ColunaLayout(nome_canonico="prazo_medio_resolucao", tipo="decimal"),
        ],
        "aliases": [
            ("COMPETENCIA", "competencia"),
            ("CD_OPERADORA", "registro_ans"),
            ("REGISTRO_ANS", "registro_ans"),
            ("TP_GARANTIA", "tipo_garantia"),
            ("QT_OCORRENCIAS", "qt_ocorrencias"),
            ("QT_RESOLVIDAS", "qt_resolvidas"),
            ("QT_PENDENTES", "qt_pendentes"),
            ("PRAZO_MEDIO", "prazo_medio_resolucao"),
        ],
    },
    {
        "dataset_codigo": "peona_sus",
        "nome": "PEONA SUS — Percentual de Eventos Obstétricos Notificados",
        "descricao": "Indicador de utilização do SUS por beneficiários de planos de saúde.",
        "tabela_raw_destino": "bruto_ans.peona_sus",
        "ftp_path": "PEONA_SUS/",
        "layout_id": "layout_peona_sus_csv",
        "colunas": [
            ColunaLayout(nome_canonico="competencia", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="registro_ans", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="vl_peona", tipo="decimal"),
            ColunaLayout(nome_canonico="qt_beneficiarios_sus", tipo="integer"),
            ColunaLayout(nome_canonico="indicador_utilizacao_sus", tipo="decimal"),
            ColunaLayout(nome_canonico="sg_uf", tipo="string"),
        ],
        "aliases": [
            ("COMPETENCIA", "competencia"),
            ("CD_OPERADORA", "registro_ans"),
            ("REGISTRO_ANS", "registro_ans"),
            ("VL_PEONA", "vl_peona"),
            ("QT_BENEFICIARIOS_SUS", "qt_beneficiarios_sus"),
            ("IN_UTILIZACAO_SUS", "indicador_utilizacao_sus"),
            ("SG_UF", "sg_uf"),
        ],
    },
    {
        "dataset_codigo": "promoprev",
        "nome": "PROMOPREV — Programas de Promoção à Saúde e Prevenção de Doenças",
        "descricao": "Investimentos e beneficiários em programas de promoção à saúde.",
        "tabela_raw_destino": "bruto_ans.promoprev",
        "ftp_path": "PROMOPREV/",
        "layout_id": "layout_promoprev_csv",
        "colunas": [
            ColunaLayout(nome_canonico="competencia", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="registro_ans", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="tipo_programa", tipo="string"),
            ColunaLayout(nome_canonico="qt_beneficiarios_programa", tipo="integer"),
            ColunaLayout(nome_canonico="vl_investimento", tipo="decimal"),
            ColunaLayout(nome_canonico="indicador_participacao", tipo="decimal"),
        ],
        "aliases": [
            ("COMPETENCIA", "competencia"),
            ("CD_OPERADORA", "registro_ans"),
            ("REGISTRO_ANS", "registro_ans"),
            ("TP_PROGRAMA", "tipo_programa"),
            ("QT_BENEFICIARIOS_PROGRAMA", "qt_beneficiarios_programa"),
            ("VL_INVESTIMENTO", "vl_investimento"),
            ("IN_PARTICIPACAO", "indicador_participacao"),
        ],
    },
    {
        "dataset_codigo": "rpc",
        "nome": "RPC — Razão de Reclamações por Beneficiário",
        "descricao": "Indicador de reclamações por operadora, município e tipo (retenção 24 meses).",  # noqa: E501
        "tabela_raw_destino": "bruto_ans.rpc",
        "ftp_path": "RPC/",
        "layout_id": "layout_rpc_csv",
        "colunas": [
            ColunaLayout(nome_canonico="competencia", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="registro_ans", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="cd_municipio", tipo="string"),
            ColunaLayout(nome_canonico="sg_uf", tipo="string"),
            ColunaLayout(nome_canonico="tipo_reclamacao", tipo="string"),
            ColunaLayout(nome_canonico="qt_reclamacoes", tipo="integer"),
            ColunaLayout(nome_canonico="qt_resolvidas", tipo="integer"),
            ColunaLayout(nome_canonico="indice_resolucao", tipo="decimal"),
            ColunaLayout(nome_canonico="nota_rpc", tipo="decimal"),
        ],
        "aliases": [
            ("COMPETENCIA", "competencia"),
            ("CD_OPERADORA", "registro_ans"),
            ("REGISTRO_ANS", "registro_ans"),
            ("CD_MUNICIPIO", "cd_municipio"),
            ("SG_UF", "sg_uf"),
            ("TP_RECLAMACAO", "tipo_reclamacao"),
            ("QT_RECLAMACOES", "qt_reclamacoes"),
            ("QT_RESOLVIDAS", "qt_resolvidas"),
            ("IN_RESOLUCAO", "indice_resolucao"),
            ("NOTA_RPC", "nota_rpc"),
        ],
    },
    {
        "dataset_codigo": "iap",
        "nome": "IAP — Índice de Avaliação de Performance",
        "descricao": "Indicadores de performance de operadoras por dimensão e componente.",
        "tabela_raw_destino": "bruto_ans.iap",
        "ftp_path": "IAP/",
        "layout_id": "layout_iap_csv",
        "colunas": [
            ColunaLayout(nome_canonico="competencia", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="registro_ans", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="dimensao", tipo="string"),
            ColunaLayout(nome_canonico="indicador", tipo="string"),
            ColunaLayout(nome_canonico="valor_indicador", tipo="decimal"),
            ColunaLayout(nome_canonico="peso_indicador", tipo="decimal"),
            ColunaLayout(nome_canonico="pontuacao", tipo="decimal"),
        ],
        "aliases": [
            ("COMPETENCIA", "competencia"),
            ("CD_OPERADORA", "registro_ans"),
            ("REGISTRO_ANS", "registro_ans"),
            ("DIMENSAO", "dimensao"),
            ("INDICADOR", "indicador"),
            ("VL_INDICADOR", "valor_indicador"),
            ("PESO_INDICADOR", "peso_indicador"),
            ("PONTUACAO", "pontuacao"),
        ],
    },
    {
        "dataset_codigo": "pfa",
        "nome": "PFA — Programa de Fiscalização Ampliada",
        "descricao": "Indicadores do PFA por operadora: valor, meta e status de cumprimento.",
        "tabela_raw_destino": "bruto_ans.pfa",
        "ftp_path": "PFA/",
        "layout_id": "layout_pfa_csv",
        "colunas": [
            ColunaLayout(nome_canonico="competencia", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="registro_ans", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="indicador", tipo="string"),
            ColunaLayout(nome_canonico="valor_indicador", tipo="decimal"),
            ColunaLayout(nome_canonico="meta", tipo="decimal"),
            ColunaLayout(nome_canonico="status_meta", tipo="string"),
        ],
        "aliases": [
            ("COMPETENCIA", "competencia"),
            ("CD_OPERADORA", "registro_ans"),
            ("REGISTRO_ANS", "registro_ans"),
            ("INDICADOR", "indicador"),
            ("VL_INDICADOR", "valor_indicador"),
            ("META", "meta"),
            ("ST_META", "status_meta"),
        ],
    },
    {
        "dataset_codigo": "programa_qualificacao_institucional",
        "nome": "Programa de Qualificação Institucional",
        "descricao": "Nível e pontuação de qualificação institucional de operadoras.",
        "tabela_raw_destino": "bruto_ans.programa_qualificacao_institucional",
        "ftp_path": "QUALIFICACAO_INSTITUCIONAL/",
        "layout_id": "layout_programa_qualificacao_institucional_csv",
        "colunas": [
            ColunaLayout(nome_canonico="competencia", tipo="string"),
            ColunaLayout(nome_canonico="registro_ans", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="nivel_qualificacao", tipo="string"),
            ColunaLayout(nome_canonico="pontuacao_qualificacao", tipo="decimal"),
            ColunaLayout(nome_canonico="data_avaliacao", tipo="date"),
            ColunaLayout(nome_canonico="status_qualificacao", tipo="string"),
        ],
        "aliases": [
            ("COMPETENCIA", "competencia"),
            ("CD_OPERADORA", "registro_ans"),
            ("REGISTRO_ANS", "registro_ans"),
            ("NIVEL_QUALIFICACAO", "nivel_qualificacao"),
            ("PONTUACAO", "pontuacao_qualificacao"),
            ("DT_AVALIACAO", "data_avaliacao"),
            ("ST_QUALIFICACAO", "status_qualificacao"),
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

        print("Bootstrap de layouts Regulatórios Complementares concluído.")
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(bootstrap())
