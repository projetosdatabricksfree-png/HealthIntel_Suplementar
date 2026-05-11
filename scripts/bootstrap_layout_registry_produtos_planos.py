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
        "dataset_codigo": "produto_caracteristica",
        "nome": "Características de Produtos de Saúde Suplementar",
        "descricao": "Características de produtos por operadora (segmentação, cobertura, modalidade).",  # noqa: E501
        "tabela_raw_destino": "bruto_ans.produto_caracteristica",
        "ftp_path": "caracteristicas_produtos_saude_suplementar-008/",
        "layout_id": "layout_produto_caracteristica_csv",
        "colunas": [
            ColunaLayout(nome_canonico="registro_ans", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="codigo_produto", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="nome_produto", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="segmentacao", tipo="string"),
            ColunaLayout(nome_canonico="tipo_contratacao", tipo="string"),
            ColunaLayout(nome_canonico="abrangencia_geografica", tipo="string"),
            ColunaLayout(nome_canonico="cobertura_area", tipo="string"),
            ColunaLayout(nome_canonico="modalidade", tipo="string"),
            ColunaLayout(nome_canonico="uf_comercializacao", tipo="string"),
            ColunaLayout(nome_canonico="competencia", tipo="string"),
        ],
        "aliases": [
            ("CD_OPERADORA", "registro_ans"),
            ("REGISTRO_ANS", "registro_ans"),
            ("CD_PRODUTO", "codigo_produto"),
            ("NM_PRODUTO", "nome_produto"),
            ("SEGMENTACAO_ASSISTENCIAL", "segmentacao"),
            ("TIPO_CONTRATACAO", "tipo_contratacao"),
            ("ABRANGENCIA_COBERTURA", "abrangencia_geografica"),
            ("MUNICIPIOS_COBERTURA", "cobertura_area"),
            ("MODALIDADE", "modalidade"),
            ("UF_COMERCIALIZACAO", "uf_comercializacao"),
            ("COMPETENCIA", "competencia"),
        ],
    },
    {
        "dataset_codigo": "historico_plano",
        "nome": "Histórico de Planos de Saúde",
        "descricao": "Histórico de planos por operadora, situação e período.",
        "tabela_raw_destino": "bruto_ans.historico_plano",
        "ftp_path": "historico_planos_saude/",
        "layout_id": "layout_historico_plano_csv",
        "colunas": [
            ColunaLayout(nome_canonico="registro_ans", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="codigo_plano", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="nome_plano", tipo="string"),
            ColunaLayout(nome_canonico="situacao", tipo="string"),
            ColunaLayout(nome_canonico="data_situacao", tipo="date"),
            ColunaLayout(nome_canonico="segmentacao", tipo="string"),
            ColunaLayout(nome_canonico="tipo_contratacao", tipo="string"),
            ColunaLayout(nome_canonico="abrangencia_geografica", tipo="string"),
            ColunaLayout(nome_canonico="uf", tipo="string"),
            ColunaLayout(nome_canonico="competencia", tipo="string"),
        ],
        "aliases": [
            ("CD_OPERADORA", "registro_ans"),
            ("REGISTRO_ANS", "registro_ans"),
            ("CD_PLANO", "codigo_plano"),
            ("NM_PLANO", "nome_plano"),
            ("SITUACAO", "situacao"),
            ("DT_SITUACAO", "data_situacao"),
            ("SEGMENTACAO", "segmentacao"),
            ("TIPO_CONTRATACAO", "tipo_contratacao"),
            ("ABRANGENCIA", "abrangencia_geografica"),
            ("UF", "uf"),
            ("COMPETENCIA", "competencia"),
        ],
    },
    {
        "dataset_codigo": "plano_servico_opcional",
        "nome": "Serviços Opcionais de Planos de Saúde",
        "descricao": "Serviços opcionais disponíveis por plano e operadora.",
        "tabela_raw_destino": "bruto_ans.plano_servico_opcional",
        "ftp_path": "servicos_opcionais_planos_saude/",
        "layout_id": "layout_plano_servico_opcional_csv",
        "colunas": [
            ColunaLayout(nome_canonico="registro_ans", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="codigo_plano", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="codigo_servico", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="descricao_servico", tipo="string"),
            ColunaLayout(nome_canonico="tipo_servico", tipo="string"),
            ColunaLayout(nome_canonico="competencia", tipo="string"),
        ],
        "aliases": [
            ("CD_OPERADORA", "registro_ans"),
            ("REGISTRO_ANS", "registro_ans"),
            ("CD_PLANO", "codigo_plano"),
            ("CD_SERVICO", "codigo_servico"),
            ("DS_SERVICO", "descricao_servico"),
            ("TP_SERVICO", "tipo_servico"),
            ("COMPETENCIA", "competencia"),
        ],
    },
    {
        "dataset_codigo": "quadro_auxiliar_corresponsabilidade",
        "nome": "Quadros Auxiliares de Corresponsabilidade",
        "descricao": "Quadros de corresponsabilidade financeira por plano e operadora.",
        "tabela_raw_destino": "bruto_ans.quadro_auxiliar_corresponsabilidade",
        "ftp_path": "quadros_auxiliares_de_corresponsabilidade/",
        "layout_id": "layout_quadro_auxiliar_corresponsabilidade_csv",
        "colunas": [
            ColunaLayout(nome_canonico="registro_ans", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="codigo_plano", tipo="string"),
            ColunaLayout(nome_canonico="tipo_corresponsabilidade", tipo="string"),
            ColunaLayout(nome_canonico="percentual_corresponsabilidade", tipo="decimal"),
            ColunaLayout(nome_canonico="valor_corresponsabilidade", tipo="decimal"),
            ColunaLayout(nome_canonico="descricao", tipo="string"),
            ColunaLayout(nome_canonico="competencia", tipo="string"),
        ],
        "aliases": [
            ("CD_OPERADORA", "registro_ans"),
            ("REGISTRO_ANS", "registro_ans"),
            ("CD_PLANO", "codigo_plano"),
            ("TP_CORRESPONSABILIDADE", "tipo_corresponsabilidade"),
            ("PCT_CORRESPONSABILIDADE", "percentual_corresponsabilidade"),
            ("VL_CORRESPONSABILIDADE", "valor_corresponsabilidade"),
            ("DS_CORRESPONSABILIDADE", "descricao"),
            ("COMPETENCIA", "competencia"),
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

        print("Bootstrap de layouts Produtos/Planos concluído.")
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(bootstrap())
