from sqlalchemy import text

from api.app.core.database import SessionLocal
from api.app.schemas.meta import (
    DatasetMetaResponse,
    EndpointMetaResponse,
    MetaEnvelope,
    PipelineMetaResponse,
    VersaoDatasetResponse,
)

CATALOGO_DATASETS = {
    "cadop": {
        "descricao": "Cadastro mestre de operadoras.",
        "cadencia": "continua",
        "status": "ativo",
    },
    "sib_operadora": {
        "descricao": "Beneficiarios SIB consolidados por operadora e competencia.",
        "cadencia": "mensal",
        "status": "ativo",
    },
    "sib_municipio": {
        "descricao": "Beneficiarios SIB consolidados por municipio, operadora e competencia.",
        "cadencia": "mensal",
        "status": "ativo",
    },
    "igr": {
        "descricao": "IGR trimestral por operadora com metadados regulatorios.",
        "cadencia": "trimestral",
        "status": "ativo",
    },
    "nip": {
        "descricao": "Demandas NIP e TIR/TR trimestrais por operadora.",
        "cadencia": "trimestral",
        "status": "ativo",
    },
    "rn623_lista": {
        "descricao": "Listas trimestrais de excelencia e reducao da RN 623/2024.",
        "cadencia": "trimestral",
        "status": "ativo",
    },
    "idss": {
        "descricao": "IDSS anual padronizado por operadora.",
        "cadencia": "anual",
        "status": "ativo",
    },
    "regime_especial": {
        "descricao": "Historico regulatorio de regime especial por operadora.",
        "cadencia": "trimestral",
        "status": "ativo",
    },
    "prudencial": {
        "descricao": "Indicadores prudenciais trimestrais por operadora.",
        "cadencia": "trimestral",
        "status": "ativo",
    },
    "portabilidade": {
        "descricao": "Movimentacao mensal de portabilidade por operadora.",
        "cadencia": "mensal",
        "status": "ativo",
    },
    "taxa_resolutividade": {
        "descricao": "Taxa de resolutividade trimestral por operadora.",
        "cadencia": "trimestral",
        "status": "ativo",
    },
    "diops": {
        "descricao": "DIOPS financeiro trimestral por operadora.",
        "cadencia": "trimestral",
        "status": "ativo",
    },
    "fip": {
        "descricao": "FIP historico financeiro harmonizado por operadora.",
        "cadencia": "trimestral",
        "status": "ativo",
    },
    "vda": {
        "descricao": "VDA mensal por operadora.",
        "cadencia": "mensal",
        "status": "ativo",
    },
    "glosa": {
        "descricao": "Glosa mensal por operadora e tipo de glosa.",
        "cadencia": "mensal",
        "status": "ativo",
    },
    "financeiro": {
        "descricao": "Fato financeiro harmonizado por operadora e trimestre.",
        "cadencia": "trimestral",
        "status": "ativo",
    },
    "financeiro_v2": {
        "descricao": "Serie financeira v2 com VDA e glosa mensal.",
        "cadencia": "mensal",
        "status": "ativo",
    },
    "score_regulatorio": {
        "descricao": "Score regulatorio composto por operadora e competencia.",
        "cadencia": "mensal",
        "status": "ativo",
    },
    "score_v2": {
        "descricao": "Score composto v2 mensal por operadora.",
        "cadencia": "mensal",
        "status": "ativo",
    },
    "beneficiario_operadora": {
        "descricao": "Fato mensal de beneficiarios por operadora.",
        "cadencia": "mensal",
        "status": "ativo",
    },
    "beneficiario_localidade": {
        "descricao": "Fato mensal de beneficiarios por localidade.",
        "cadencia": "mensal",
        "status": "ativo",
    },
    "market_share_mensal": {
        "descricao": "Market share mensal por operadora e municipio.",
        "cadencia": "mensal",
        "status": "ativo",
    },
    "oportunidade_municipio": {
        "descricao": "Score mensal de oportunidade por municipio.",
        "cadencia": "mensal",
        "status": "ativo",
    },
    "oportunidade_v2": {
        "descricao": "Score mensal de oportunidade v2 por municipio.",
        "cadencia": "mensal",
        "status": "ativo",
    },
    "rede_assistencial": {
        "descricao": "Cobertura de rede assistencial por operadora, municipio e segmento.",
        "cadencia": "mensal",
        "status": "ativo",
    },
    "vazio_assistencial": {
        "descricao": "Vazios assistenciais por municipio, segmento e competencia.",
        "cadencia": "mensal",
        "status": "ativo",
    },
}

CATALOGO_ENDPOINTS = [
    {
        "metodo": "GET",
        "rota": "/saude",
        "descricao": "Status basico da API.",
        "autenticacao": "nao",
        "plano_minimo": "publico",
        "dataset_origem": None,
        "versao": "v1",
    },
    {
        "metodo": "GET",
        "rota": "/prontidao",
        "descricao": "Prontidao operacional das dependencias.",
        "autenticacao": "nao",
        "plano_minimo": "publico",
        "dataset_origem": None,
        "versao": "v1",
    },
    {
        "metodo": "GET",
        "rota": "/v1/meta/dataset",
        "descricao": "Catalogo de datasets ativos.",
        "autenticacao": "nao",
        "plano_minimo": "publico",
        "dataset_origem": "plataforma.versao_dataset",
        "versao": "v1",
    },
    {
        "metodo": "GET",
        "rota": "/v1/meta/versao",
        "descricao": "Versoes recentes de datasets.",
        "autenticacao": "nao",
        "plano_minimo": "publico",
        "dataset_origem": "plataforma.versao_dataset",
        "versao": "v1",
    },
    {
        "metodo": "GET",
        "rota": "/v1/meta/pipeline",
        "descricao": "Estado recente das DAGs.",
        "autenticacao": "nao",
        "plano_minimo": "publico",
        "dataset_origem": "plataforma.job",
        "versao": "v1",
    },
    {
        "metodo": "GET",
        "rota": "/v1/meta/endpoints",
        "descricao": "Catalogo publico de endpoints e contratos.",
        "autenticacao": "nao",
        "plano_minimo": "publico",
        "dataset_origem": "catalogo interno",
        "versao": "v1",
    },
    {
        "metodo": "GET",
        "rota": "/v1/operadoras",
        "descricao": "Lista operadoras publicadas na camada de leitura.",
        "autenticacao": "sim",
        "plano_minimo": "starter",
        "dataset_origem": "api_ans.api_operadora",
        "versao": "v1",
    },
    {
        "metodo": "GET",
        "rota": "/v1/operadoras/{registro_ans}",
        "descricao": "Detalhe de operadora.",
        "autenticacao": "sim",
        "plano_minimo": "starter",
        "dataset_origem": "api_ans.api_operadora",
        "versao": "v1",
    },
    {
        "metodo": "GET",
        "rota": "/v1/operadoras/{registro_ans}/score",
        "descricao": "Score mensal consolidado.",
        "autenticacao": "sim",
        "plano_minimo": "starter",
        "dataset_origem": "api_ans.api_score_operadora_mensal",
        "versao": "v1",
    },
    {
        "metodo": "GET",
        "rota": "/v1/operadoras/{registro_ans}/score-regulatorio",
        "descricao": "Score regulatorio composto.",
        "autenticacao": "sim",
        "plano_minimo": "growth",
        "dataset_origem": "api_ans.api_score_regulatorio_operadora_mensal",
        "versao": "v2",
    },
    {
        "metodo": "GET",
        "rota": "/v1/operadoras/{registro_ans}/regime-especial",
        "descricao": "Historico de regime especial.",
        "autenticacao": "sim",
        "plano_minimo": "growth",
        "dataset_origem": "api_ans.api_regime_especial_operadora",
        "versao": "v1",
    },
    {
        "metodo": "GET",
        "rota": "/v1/operadoras/{registro_ans}/portabilidade",
        "descricao": "Serie mensal de portabilidade.",
        "autenticacao": "sim",
        "plano_minimo": "growth",
        "dataset_origem": "api_ans.api_portabilidade_operadora_mensal",
        "versao": "v1",
    },
    {
        "metodo": "GET",
        "rota": "/v1/operadoras/{registro_ans}/financeiro",
        "descricao": "Serie financeira consolidada.",
        "autenticacao": "sim",
        "plano_minimo": "pro",
        "dataset_origem": "api_ans.api_financeiro_operadora_mensal",
        "versao": "v2",
    },
    {
        "metodo": "GET",
        "rota": "/v1/operadoras/{registro_ans}/score-v2",
        "descricao": "Score composto v2.",
        "autenticacao": "sim",
        "plano_minimo": "pro",
        "dataset_origem": "api_ans.api_score_v2_operadora_mensal",
        "versao": "v2",
    },
    {
        "metodo": "GET",
        "rota": "/v1/operadoras/{registro_ans}/rede",
        "descricao": "Rede assistencial por operadora.",
        "autenticacao": "sim",
        "plano_minimo": "growth",
        "dataset_origem": "api_ans.api_rede_assistencial",
        "versao": "v1",
    },
    {
        "metodo": "GET",
        "rota": "/v1/mercado/municipio",
        "descricao": "Market share por municipio.",
        "autenticacao": "sim",
        "plano_minimo": "starter",
        "dataset_origem": "api_ans.api_market_share_mensal",
        "versao": "v1",
    },
    {
        "metodo": "GET",
        "rota": "/v1/mercado/vazio-assistencial",
        "descricao": "Vazios assistenciais por municipio e segmento.",
        "autenticacao": "sim",
        "plano_minimo": "growth",
        "dataset_origem": "api_ans.api_vazio_assistencial",
        "versao": "v1",
    },
    {
        "metodo": "GET",
        "rota": "/v1/rede/municipio/{cd_municipio}",
        "descricao": "Rede assistencial por municipio.",
        "autenticacao": "sim",
        "plano_minimo": "growth",
        "dataset_origem": "api_ans.api_rede_assistencial",
        "versao": "v1",
    },
    {
        "metodo": "GET",
        "rota": "/v1/rankings/operadora/score",
        "descricao": "Ranking de score por operadora.",
        "autenticacao": "sim",
        "plano_minimo": "starter",
        "dataset_origem": "api_ans.api_ranking_score",
        "versao": "v1",
    },
    {
        "metodo": "GET",
        "rota": "/v1/rankings/operadora/crescimento",
        "descricao": "Ranking de crescimento por operadora.",
        "autenticacao": "sim",
        "plano_minimo": "starter",
        "dataset_origem": "api_ans.api_ranking_crescimento",
        "versao": "v1",
    },
    {
        "metodo": "GET",
        "rota": "/v1/rankings/municipio/oportunidade",
        "descricao": "Ranking de oportunidade v1 por municipio.",
        "autenticacao": "sim",
        "plano_minimo": "starter",
        "dataset_origem": "api_ans.api_ranking_oportunidade",
        "versao": "v1",
    },
    {
        "metodo": "GET",
        "rota": "/v1/rankings/municipio/oportunidade-v2",
        "descricao": "Ranking de oportunidade v2 por municipio.",
        "autenticacao": "sim",
        "plano_minimo": "growth",
        "dataset_origem": "api_ans.api_oportunidade_v2_municipio_mensal",
        "versao": "v2",
    },
]


def _meta_padrao(total: int) -> dict:
    return MetaEnvelope(
        competencia_referencia="atual",
        versao_dataset="meta_v1",
        total=total,
        pagina=1,
        por_pagina=total,
    ).model_dump()


async def listar_datasets() -> dict:
    async with SessionLocal() as session:
        result = await session.execute(
            text(
                """
                select dataset, max(carregado_em) as carregado_em
                from plataforma.versao_dataset
                group by dataset
                order by dataset
                """
            )
        )
        datasets = []
        for row in result.mappings():
            definicao = CATALOGO_DATASETS.get(
                row["dataset"],
                {
                    "descricao": "Dataset catalogado na plataforma.",
                    "cadencia": "sob demanda",
                    "status": "ativo",
                },
            )
            datasets.append(
                DatasetMetaResponse(
                    nome=row["dataset"],
                    descricao=definicao["descricao"],
                    cadencia=definicao["cadencia"],
                    status=definicao["status"],
                ).model_dump()
            )
    return {"dados": datasets, "meta": _meta_padrao(len(datasets))}


async def listar_versoes() -> dict:
    async with SessionLocal() as session:
        result = await session.execute(
            text(
                """
                select
                    dataset,
                    versao,
                    carregado_em,
                    competencia,
                    status
                from plataforma.versao_dataset
                order by carregado_em desc
                limit 20
                """
            )
        )
        dados = [
            VersaoDatasetResponse(
                dataset=row["dataset"],
                versao=row["versao"],
                carregado_em=row["carregado_em"].isoformat(),
                competencia=row["competencia"],
                status=row["status"],
            ).model_dump()
            for row in result.mappings()
        ]
    return {"dados": dados, "meta": _meta_padrao(len(dados))}


async def listar_pipeline() -> dict:
    async with SessionLocal() as session:
        result = await session.execute(
            text(
                """
                select
                    dag_id,
                    coalesce(fonte_ans, nome_job) as dataset,
                    status,
                    iniciado_em,
                    finalizado_em
                from plataforma.job
                order by iniciado_em desc
                limit 20
                """
            )
        )
        dados = [
            PipelineMetaResponse(
                dag_id=row["dag_id"],
                dataset=row["dataset"],
                status=row["status"],
                iniciado_em=row["iniciado_em"].isoformat(),
                finalizado_em=row["finalizado_em"].isoformat() if row["finalizado_em"] else None,
            ).model_dump()
            for row in result.mappings()
        ]
    return {"dados": dados, "meta": _meta_padrao(len(dados))}


async def listar_endpoints() -> dict:
    dados = [
        EndpointMetaResponse(**endpoint).model_dump() for endpoint in CATALOGO_ENDPOINTS
    ]
    return {"dados": dados, "meta": _meta_padrao(len(dados))}
