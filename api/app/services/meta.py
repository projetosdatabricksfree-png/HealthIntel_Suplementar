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
    "cnes_estabelecimento": {
        "descricao": "Cadastro nacional de estabelecimentos de saude consolidado em bronze.",
        "cadencia": "mensal",
        "status": "ativo",
    },
    "tiss_procedimento": {
        "descricao": "Procedimentos TISS trimestrais consolidado em bronze.",
        "cadencia": "trimestral",
        "status": "ativo",
    },
    "score_v3": {
        "descricao": "Score composto v3 por operadora e competencia.",
        "cadencia": "mensal",
        "status": "ativo",
    },
    "api_premium_operadora_360_validado": {
        "descricao": "Produto API premium de operadora 360 com validação documental.",
        "cadencia": "mensal",
        "status": "ativo",
    },
    "api_premium_cnes_estabelecimento_validado": {
        "descricao": "Produto API premium de estabelecimentos CNES validados.",
        "cadencia": "mensal",
        "status": "ativo",
    },
    "api_premium_quality_dataset": {
        "descricao": "Resumo premium de qualidade documental por fonte e status.",
        "cadencia": "sob demanda",
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
    {
        "metodo": "GET",
        "rota": "/v1/cnes/municipio/{cd_municipio}",
        "descricao": "Estabelecimentos CNES por municipio.",
        "autenticacao": "sim",
        "plano_minimo": "growth",
        "dataset_origem": "api_ans.api_cnes_municipio",
        "versao": "v1",
    },
    {
        "metodo": "GET",
        "rota": "/v1/cnes/uf/{sg_uf}",
        "descricao": "Estabelecimentos CNES por UF.",
        "autenticacao": "sim",
        "plano_minimo": "growth",
        "dataset_origem": "api_ans.api_cnes_municipio",
        "versao": "v1",
    },
    {
        "metodo": "GET",
        "rota": "/v1/tiss/{registro_ans}/procedimentos",
        "descricao": "Procedimentos TISS por operadora.",
        "autenticacao": "sim",
        "plano_minimo": "growth",
        "dataset_origem": "api_ans.api_tiss_operadora_trimestral",
        "versao": "v1",
    },
    {
        "metodo": "GET",
        "rota": "/v1/tiss/{registro_ans}/sinistralidade",
        "descricao": "Sinistralidade por grupo de procedimento.",
        "autenticacao": "sim",
        "plano_minimo": "growth",
        "dataset_origem": "api_ans.api_sinistralidade_procedimento",
        "versao": "v1",
    },
    {
        "metodo": "GET",
        "rota": "/v1/rede/gap/{cd_municipio}",
        "descricao": "Gap entre CNES e rede declarada por municipio.",
        "autenticacao": "sim",
        "plano_minimo": "growth",
        "dataset_origem": "api_ans.api_cnes_rede_gap",
        "versao": "v1",
    },
]

CATALOGO_ENDPOINTS += [
    {
        "metodo": "GET",
        "rota": "/v1/bronze/cadop",
        "descricao": "Bronze técnico de CADOP.",
        "autenticacao": "sim",
        "plano_minimo": "enterprise_tecnico",
        "dataset_origem": "api_ans.api_bronze_cadop",
        "versao": "v1",
    },
    {
        "metodo": "GET",
        "rota": "/v1/bronze/sib/operadora",
        "descricao": "Bronze técnico de SIB por operadora.",
        "autenticacao": "sim",
        "plano_minimo": "enterprise_tecnico",
        "dataset_origem": "api_ans.api_bronze_sib_operadora",
        "versao": "v1",
    },
    {
        "metodo": "GET",
        "rota": "/v1/bronze/sib/municipio",
        "descricao": "Bronze técnico de SIB por municipio.",
        "autenticacao": "sim",
        "plano_minimo": "enterprise_tecnico",
        "dataset_origem": "api_ans.api_bronze_sib_municipio",
        "versao": "v1",
    },
    {
        "metodo": "GET",
        "rota": "/v1/bronze/igr",
        "descricao": "Bronze técnico de IGR.",
        "autenticacao": "sim",
        "plano_minimo": "enterprise_tecnico",
        "dataset_origem": "api_ans.api_bronze_igr",
        "versao": "v1",
    },
    {
        "metodo": "GET",
        "rota": "/v1/bronze/nip",
        "descricao": "Bronze técnico de NIP.",
        "autenticacao": "sim",
        "plano_minimo": "enterprise_tecnico",
        "dataset_origem": "api_ans.api_bronze_nip",
        "versao": "v1",
    },
    {
        "metodo": "GET",
        "rota": "/v1/bronze/idss",
        "descricao": "Bronze técnico de IDSS.",
        "autenticacao": "sim",
        "plano_minimo": "enterprise_tecnico",
        "dataset_origem": "api_ans.api_bronze_idss",
        "versao": "v1",
    },
    {
        "metodo": "GET",
        "rota": "/v1/bronze/diops",
        "descricao": "Bronze técnico de DIOPS.",
        "autenticacao": "sim",
        "plano_minimo": "enterprise_tecnico",
        "dataset_origem": "api_ans.api_bronze_diops",
        "versao": "v1",
    },
    {
        "metodo": "GET",
        "rota": "/v1/bronze/fip",
        "descricao": "Bronze técnico de FIP.",
        "autenticacao": "sim",
        "plano_minimo": "enterprise_tecnico",
        "dataset_origem": "api_ans.api_bronze_fip",
        "versao": "v1",
    },
    {
        "metodo": "GET",
        "rota": "/v1/bronze/vda",
        "descricao": "Bronze técnico de VDA.",
        "autenticacao": "sim",
        "plano_minimo": "enterprise_tecnico",
        "dataset_origem": "api_ans.api_bronze_vda",
        "versao": "v1",
    },
    {
        "metodo": "GET",
        "rota": "/v1/bronze/glosa",
        "descricao": "Bronze técnico de glosa.",
        "autenticacao": "sim",
        "plano_minimo": "enterprise_tecnico",
        "dataset_origem": "api_ans.api_bronze_glosa",
        "versao": "v1",
    },
    {
        "metodo": "GET",
        "rota": "/v1/bronze/rede-assistencial",
        "descricao": "Bronze técnico de rede assistencial.",
        "autenticacao": "sim",
        "plano_minimo": "enterprise_tecnico",
        "dataset_origem": "api_ans.api_bronze_rede_assistencial",
        "versao": "v1",
    },
    {
        "metodo": "GET",
        "rota": "/v1/prata/cadop",
        "descricao": "Prata analítica de CADOP.",
        "autenticacao": "sim",
        "plano_minimo": "analitico",
        "dataset_origem": "api_ans.api_prata_cadop",
        "versao": "v1",
    },
    {
        "metodo": "GET",
        "rota": "/v1/prata/sib/operadora",
        "descricao": "Prata analítica de SIB por operadora.",
        "autenticacao": "sim",
        "plano_minimo": "analitico",
        "dataset_origem": "api_ans.api_prata_sib_operadora",
        "versao": "v1",
    },
    {
        "metodo": "GET",
        "rota": "/v1/prata/sib/municipio",
        "descricao": "Prata analítica de SIB por municipio.",
        "autenticacao": "sim",
        "plano_minimo": "analitico",
        "dataset_origem": "api_ans.api_prata_sib_municipio",
        "versao": "v1",
    },
    {
        "metodo": "GET",
        "rota": "/v1/prata/igr",
        "descricao": "Prata analítica de IGR.",
        "autenticacao": "sim",
        "plano_minimo": "analitico",
        "dataset_origem": "api_ans.api_prata_igr",
        "versao": "v1",
    },
    {
        "metodo": "GET",
        "rota": "/v1/prata/nip",
        "descricao": "Prata analítica de NIP.",
        "autenticacao": "sim",
        "plano_minimo": "analitico",
        "dataset_origem": "api_ans.api_prata_nip",
        "versao": "v1",
    },
    {
        "metodo": "GET",
        "rota": "/v1/prata/idss",
        "descricao": "Prata analítica de IDSS.",
        "autenticacao": "sim",
        "plano_minimo": "analitico",
        "dataset_origem": "api_ans.api_prata_idss",
        "versao": "v1",
    },
    {
        "metodo": "GET",
        "rota": "/v1/prata/diops",
        "descricao": "Prata analítica de DIOPS.",
        "autenticacao": "sim",
        "plano_minimo": "analitico",
        "dataset_origem": "api_ans.api_prata_diops",
        "versao": "v1",
    },
    {
        "metodo": "GET",
        "rota": "/v1/prata/fip",
        "descricao": "Prata analítica de FIP.",
        "autenticacao": "sim",
        "plano_minimo": "analitico",
        "dataset_origem": "api_ans.api_prata_fip",
        "versao": "v1",
    },
    {
        "metodo": "GET",
        "rota": "/v1/prata/vda",
        "descricao": "Prata analítica de VDA.",
        "autenticacao": "sim",
        "plano_minimo": "analitico",
        "dataset_origem": "api_ans.api_prata_vda",
        "versao": "v1",
    },
    {
        "metodo": "GET",
        "rota": "/v1/prata/glosa",
        "descricao": "Prata analítica de glosa.",
        "autenticacao": "sim",
        "plano_minimo": "analitico",
        "dataset_origem": "api_ans.api_prata_glosa",
        "versao": "v1",
    },
    {
        "metodo": "GET",
        "rota": "/v1/prata/rede-assistencial",
        "descricao": "Prata analítica de rede assistencial.",
        "autenticacao": "sim",
        "plano_minimo": "analitico",
        "dataset_origem": "api_ans.api_prata_rede_assistencial",
        "versao": "v1",
    },
    {
        "metodo": "GET",
        "rota": "/v1/prata/operadora/enriquecida",
        "descricao": "Prata enriquecida de operadora.",
        "autenticacao": "sim",
        "plano_minimo": "analitico",
        "dataset_origem": "api_ans.api_prata_operadora_enriquecida",
        "versao": "v1",
    },
    {
        "metodo": "GET",
        "rota": "/v1/prata/municipio/metrica",
        "descricao": "Prata enriquecida de municipio.",
        "autenticacao": "sim",
        "plano_minimo": "analitico",
        "dataset_origem": "api_ans.api_prata_municipio_metrica",
        "versao": "v1",
    },
    {
        "metodo": "GET",
        "rota": "/v1/prata/financeiro/periodo",
        "descricao": "Prata enriquecida financeira por periodo.",
        "autenticacao": "sim",
        "plano_minimo": "analitico",
        "dataset_origem": "api_ans.api_prata_financeiro_periodo",
        "versao": "v1",
    },
    {
        "metodo": "GET",
        "rota": "/v1/prata/quarentena/resumo",
        "descricao": "Resumo da quarentena por dataset e competencia.",
        "autenticacao": "sim",
        "plano_minimo": "analitico",
        "dataset_origem": "plataforma.vw_resumo_quarentena",
        "versao": "v1",
    },
    {
        "metodo": "GET",
        "rota": "/v1/prata/quarentena/{dataset}",
        "descricao": "Detalhe da quarentena por dataset.",
        "autenticacao": "sim",
        "plano_minimo": "enterprise_tecnico",
        "dataset_origem": "plataforma.arquivo_quarentena",
        "versao": "v1",
    },
    {
        "metodo": "GET",
        "rota": "/v1/operadoras/{registro_ans}/score-v3",
        "descricao": "Score v3 por operadora.",
        "autenticacao": "sim",
        "plano_minimo": "essencial",
        "dataset_origem": "api_ans.api_score_v3_operadora_mensal",
        "versao": "v1",
    },
    {
        "metodo": "GET",
        "rota": "/v1/operadoras/{registro_ans}/score-v3/historico",
        "descricao": "Historico do score v3 por operadora.",
        "autenticacao": "sim",
        "plano_minimo": "essencial",
        "dataset_origem": "api_ans.api_score_v3_operadora_mensal",
        "versao": "v1",
    },
    {
        "metodo": "GET",
        "rota": "/v1/rankings/composto",
        "descricao": "Ranking composto v3 por operadora.",
        "autenticacao": "sim",
        "plano_minimo": "essencial",
        "dataset_origem": "api_ans.api_ranking_composto_mensal",
        "versao": "v1",
    },
]

CATALOGO_ENDPOINTS += [
    {
        "metodo": "GET",
        "rota": "/v1/premium/operadoras",
        "descricao": "Operadora 360 premium com validação documental.",
        "autenticacao": "sim",
        "plano_minimo": "premium",
        "dataset_origem": "api_ans.api_premium_operadora_360_validado",
        "versao": "v1",
    },
    {
        "metodo": "GET",
        "rota": "/v1/premium/cnes/estabelecimentos",
        "descricao": "Estabelecimentos CNES premium validados.",
        "autenticacao": "sim",
        "plano_minimo": "premium",
        "dataset_origem": "api_ans.api_premium_cnes_estabelecimento_validado",
        "versao": "v1",
    },
    {
        "metodo": "GET",
        "rota": "/v1/premium/quality/datasets",
        "descricao": "Resumo premium de qualidade documental por dataset.",
        "autenticacao": "sim",
        "plano_minimo": "premium",
        "dataset_origem": "api_ans.api_premium_quality_dataset",
        "versao": "v1",
    },
]


STATUS_DISPONIVEL = "disponivel"
STATUS_EM_VALIDACAO = "em_validacao"
STATUS_FORA_DO_MVP = "fora_do_mvp"
PRODUTO_CORE_ANS = "Core ANS"

DATASETS_CORE_ANS = [
    {
        "nome": "cadop_operadora",
        "descricao": "Cadastro publico de operadoras ANS.",
        "cadencia": "mensal",
        "fonte_serving": "api_ans.api_operadora",
    },
    {
        "nome": "produto_plano",
        "descricao": "Produtos e planos de saude suplementar.",
        "cadencia": "mensal",
        "fonte_serving": "api_ans.api_produto_plano",
    },
    {
        "nome": "historico_plano",
        "descricao": "Historico de situacao dos planos.",
        "cadencia": "mensal",
        "fonte_serving": "api_ans.api_historico_plano",
    },
    {
        "nome": "tuss_procedimento_vigente",
        "descricao": "Tabela TUSS oficial vigente.",
        "cadencia": "sob demanda",
        "fonte_serving": "api_ans.api_tuss_procedimento_vigente",
    },
    {
        "nome": "sib_beneficiario_operadora",
        "descricao": "Beneficiarios SIB por operadora e competencia.",
        "cadencia": "mensal",
        "fonte_serving": "consumo_ans.consumo_beneficiarios_operadora_mes",
    },
    {
        "nome": "sib_beneficiario_municipio",
        "descricao": "Beneficiarios SIB por municipio e competencia.",
        "cadencia": "mensal",
        "fonte_serving": "consumo_ans.consumo_beneficiarios_municipio_mes",
    },
    {
        "nome": "idss",
        "descricao": "IDSS anual por operadora.",
        "cadencia": "anual",
        "fonte_serving": "api_ans.api_prata_idss",
    },
    {
        "nome": "igr",
        "descricao": "IGR trimestral por operadora.",
        "cadencia": "trimestral",
        "fonte_serving": "api_ans.api_prata_igr",
    },
    {
        "nome": "nip",
        "descricao": "NIP por operadora.",
        "cadencia": "trimestral",
        "fonte_serving": "api_ans.api_prata_nip",
    },
    {
        "nome": "diops",
        "descricao": "DIOPS financeiro trimestral.",
        "cadencia": "trimestral",
        "fonte_serving": "api_ans.api_prata_diops",
    },
    {
        "nome": "financeiro_periodo",
        "descricao": "Indicadores economico-financeiros por periodo trimestral.",
        "cadencia": "trimestral",
        "fonte_serving": "api_ans.api_prata_financeiro_periodo",
    },
    {
        "nome": "glosa",
        "descricao": "Glosa mensal por operadora.",
        "cadencia": "mensal",
        "fonte_serving": "api_ans.api_glosa_operadora_mensal",
    },
    {
        "nome": "prudencial",
        "descricao": "Indicadores prudenciais trimestrais.",
        "cadencia": "trimestral",
        "fonte_serving": "api_ans.api_prudencial_operadora_trimestral",
    },
    {
        "nome": "regime_especial",
        "descricao": "Regime especial trimestral por operadora.",
        "cadencia": "trimestral",
        "fonte_serving": "api_ans.api_regime_especial_operadora_trimestral",
    },
    {
        "nome": "taxa_resolutividade",
        "descricao": "Taxa de resolutividade trimestral por operadora.",
        "cadencia": "trimestral",
        "fonte_serving": "api_ans.api_taxa_resolutividade_operadora_trimestral",
    },
]

ENDPOINTS_CORE_ANS = [
    {
        "method": "GET",
        "path": "/saude",
        "grupo": "meta",
        "descricao": "Status basico da API.",
        "fonte_serving": None,
        "requer_api_key": False,
    },
    {
        "method": "GET",
        "path": "/prontidao",
        "grupo": "meta",
        "descricao": "Prontidao operacional. Requer token interno.",
        "fonte_serving": None,
        "requer_api_key": False,
    },
    {
        "method": "GET",
        "path": "/v1/meta/dataset",
        "grupo": "meta",
        "descricao": "Catalogo de datasets do Core ANS.",
        "fonte_serving": "catalogo interno",
        "requer_api_key": True,
    },
    {
        "method": "GET",
        "path": "/v1/meta/versao",
        "grupo": "meta",
        "descricao": "Versoes recentes de datasets.",
        "fonte_serving": "plataforma.versao_dataset",
        "requer_api_key": True,
    },
    {
        "method": "GET",
        "path": "/v1/meta/pipeline",
        "grupo": "meta",
        "descricao": "Estado recente das cargas.",
        "fonte_serving": "plataforma.job",
        "requer_api_key": True,
    },
    {
        "method": "GET",
        "path": "/v1/meta/endpoints",
        "grupo": "meta",
        "descricao": "Catalogo publico Core ANS.",
        "fonte_serving": "catalogo interno",
        "requer_api_key": True,
    },
    {
        "method": "GET",
        "path": "/v1/operadoras",
        "grupo": "operadoras",
        "descricao": "Lista operadoras publicadas.",
        "fonte_serving": "api_ans.api_operadora",
        "requer_api_key": True,
    },
    {
        "method": "GET",
        "path": "/v1/operadoras/{registro_ans}",
        "grupo": "operadoras",
        "descricao": "Detalhe de operadora.",
        "fonte_serving": "api_ans.api_operadora",
        "requer_api_key": True,
    },
    {
        "method": "GET",
        "path": "/v1/operadoras/{registro_ans}/score",
        "grupo": "score",
        "descricao": "Score mensal consolidado.",
        "fonte_serving": "api_ans.api_score_operadora_mensal",
        "requer_api_key": True,
    },
    {
        "method": "GET",
        "path": "/v1/operadoras/{registro_ans}/score-v2",
        "grupo": "score",
        "descricao": "Score composto v2.",
        "fonte_serving": "api_ans.api_score_v2_operadora_mensal",
        "requer_api_key": True,
    },
    {
        "method": "GET",
        "path": "/v1/operadoras/{registro_ans}/score-v3",
        "grupo": "score",
        "descricao": "Score composto v3.",
        "fonte_serving": "api_ans.api_score_v3_operadora_mensal",
        "requer_api_key": True,
    },
    {
        "method": "GET",
        "path": "/v1/operadoras/{registro_ans}/score-v3/historico",
        "grupo": "score",
        "descricao": "Historico do score v3.",
        "fonte_serving": "api_ans.api_score_v3_operadora_mensal",
        "requer_api_key": True,
    },
    {
        "method": "GET",
        "path": "/v1/operadoras/{registro_ans}/score-regulatorio",
        "grupo": "regulatorio",
        "descricao": "Score regulatorio composto.",
        "fonte_serving": "api_ans.api_score_regulatorio_operadora_mensal",
        "requer_api_key": True,
        "status_if_empty": STATUS_EM_VALIDACAO,
    },
    {
        "method": "GET",
        "path": "/v1/operadoras/{registro_ans}/regulatorio",
        "grupo": "regulatorio",
        "descricao": "Consolidado regulatorio IDSS, IGR, NIP e sinais complementares.",
        "fonte_serving": "api_ans.api_regulatorio_operadora_trimestral",
        "requer_api_key": True,
    },
    {
        "method": "GET",
        "path": "/v1/operadoras/{registro_ans}/regime-especial",
        "grupo": "regulatorio",
        "descricao": "Regime especial trimestral.",
        "fonte_serving": "api_ans.api_regime_especial_operadora_trimestral",
        "requer_api_key": True,
    },
    {
        "method": "GET",
        "path": "/v1/regulatorio/rn623",
        "grupo": "regulatorio",
        "descricao": "Listas RN623.",
        "fonte_serving": "api_ans.api_rn623_lista_trimestral",
        "requer_api_key": True,
        "status_if_empty": STATUS_EM_VALIDACAO,
    },
    {
        "method": "GET",
        "path": "/v1/operadoras/{registro_ans}/portabilidade",
        "grupo": "portabilidade",
        "descricao": "Portabilidade por operadora.",
        "fonte_serving": "api_ans.api_portabilidade_operadora_mensal",
        "requer_api_key": True,
        "status_if_empty": STATUS_EM_VALIDACAO,
    },
    {
        "method": "GET",
        "path": "/v1/operadoras/{registro_ans}/financeiro",
        "grupo": "financeiro",
        "descricao": "Indicadores economico-financeiros por operadora e periodo trimestral.",
        "fonte_serving": "consumo_ans.consumo_financeiro_operadora_trimestre",
        "requer_api_key": True,
    },
    {
        "method": "GET",
        "path": "/v1/mercado/municipio",
        "grupo": "mercado",
        "descricao": "Beneficiarios e mercado por municipio.",
        "fonte_serving": "consumo_ans.consumo_beneficiarios_municipio_mes",
        "requer_api_key": True,
    },
    {
        "method": "GET",
        "path": "/v1/rankings/operadora/crescimento",
        "grupo": "rankings",
        "descricao": "Ranking de crescimento por operadora.",
        "fonte_serving": "api_ans.api_ranking_crescimento",
        "requer_api_key": True,
    },
    {
        "method": "GET",
        "path": "/v1/rankings/operadora/score",
        "grupo": "rankings",
        "descricao": "Ranking de score por operadora.",
        "fonte_serving": "api_ans.api_ranking_score",
        "requer_api_key": True,
    },
    {
        "method": "GET",
        "path": "/v1/rankings/municipio/oportunidade",
        "grupo": "rankings",
        "descricao": "Ranking de oportunidade por municipio.",
        "fonte_serving": "api_ans.api_ranking_oportunidade",
        "requer_api_key": True,
    },
    {
        "method": "GET",
        "path": "/v1/rankings/municipio/oportunidade-v2",
        "grupo": "rankings",
        "descricao": "Ranking de oportunidade v2 por municipio.",
        "fonte_serving": "api_ans.api_oportunidade_v2_municipio_mensal",
        "requer_api_key": True,
    },
    {
        "method": "GET",
        "path": "/v1/rankings/composto",
        "grupo": "rankings",
        "descricao": "Ranking composto v3 por operadora.",
        "fonte_serving": "api_ans.api_ranking_composto_mensal",
        "requer_api_key": True,
    },
    {
        "method": "GET",
        "path": "/v1/mercado/vazio-assistencial",
        "grupo": "rede",
        "descricao": "Vazio assistencial.",
        "fonte_serving": "api_ans.api_vazio_assistencial",
        "requer_api_key": True,
        "status_if_empty": STATUS_EM_VALIDACAO,
    },
    {
        "method": "GET",
        "path": "/v1/rede/municipio/{cd_municipio}",
        "grupo": "rede",
        "descricao": "Rede assistencial por municipio.",
        "fonte_serving": "api_ans.api_rede_assistencial",
        "requer_api_key": True,
        "status_if_empty": STATUS_EM_VALIDACAO,
    },
    {
        "method": "GET",
        "path": "/v1/cnes/municipio/{cd_municipio}",
        "grupo": "cnes",
        "descricao": "CNES por municipio.",
        "fonte_serving": "api_ans.api_cnes_municipio",
        "requer_api_key": True,
        "status_if_empty": STATUS_EM_VALIDACAO,
    },
    {
        "method": "GET",
        "path": "/v1/cnes/uf/{sg_uf}",
        "grupo": "cnes",
        "descricao": "CNES por UF.",
        "fonte_serving": "api_ans.api_cnes_municipio",
        "requer_api_key": True,
        "status_if_empty": STATUS_EM_VALIDACAO,
    },
    {
        "method": "GET",
        "path": "/v1/produtos/planos",
        "grupo": "produto_plano",
        "descricao": "Lista produtos e planos.",
        "fonte_serving": "api_ans.api_produto_plano",
        "requer_api_key": True,
    },
    {
        "method": "GET",
        "path": "/v1/produtos/planos/{codigo_plano}",
        "grupo": "produto_plano",
        "descricao": "Detalhe de produto/plano.",
        "fonte_serving": "api_ans.api_produto_plano",
        "requer_api_key": True,
    },
    {
        "method": "GET",
        "path": "/v1/produtos/historico",
        "grupo": "produto_plano",
        "descricao": "Historico de planos.",
        "fonte_serving": "api_ans.api_historico_plano",
        "requer_api_key": True,
    },
    {
        "method": "GET",
        "path": "/v1/tuss/procedimentos",
        "grupo": "tuss",
        "descricao": "Procedimentos TUSS oficiais vigentes.",
        "fonte_serving": "api_ans.api_tuss_procedimento_vigente",
        "requer_api_key": True,
    },
    {
        "method": "GET",
        "path": "/v1/tuss/procedimentos/{codigo_tuss}",
        "grupo": "tuss",
        "descricao": "Detalhe de procedimento TUSS.",
        "fonte_serving": "api_ans.api_tuss_procedimento_vigente",
        "requer_api_key": True,
    },
    {
        "method": "GET",
        "path": "/v1/tiss/{registro_ans}/procedimentos",
        "grupo": "tiss",
        "descricao": "TISS em validacao para o Core ANS.",
        "fonte_serving": "api_ans.api_tiss_operadora_trimestral",
        "requer_api_key": True,
        "status_if_empty": STATUS_EM_VALIDACAO,
    },
]


def _relacao_segura(relacao: str | None) -> str | None:
    if not relacao or relacao == "catalogo interno":
        return None
    partes = relacao.split(".")
    if len(partes) != 2 or not all(parte.replace("_", "").isalnum() for parte in partes):
        return None
    return f"{partes[0]}.{partes[1]}"


async def _contar_relacoes(relacoes: set[str]) -> dict[str, int | None]:
    counts: dict[str, int | None] = {}
    async with SessionLocal() as session:
        for relacao in sorted(relacoes):
            segura = _relacao_segura(relacao)
            if not segura:
                counts[relacao] = None
                continue
            existe = await session.execute(text("select to_regclass(:relacao)"), {"relacao": segura})
            if existe.scalar_one() is None:
                counts[relacao] = None
                continue
            total = await session.execute(text(f"select count(*) from {segura}"))
            counts[relacao] = int(total.scalar_one())
    return counts


def _status_por_row_count(row_count: int | None, status_if_empty: str = STATUS_EM_VALIDACAO) -> str:
    if row_count is None:
        return status_if_empty
    if row_count > 0:
        return STATUS_DISPONIVEL
    return status_if_empty


def _meta_padrao(total: int) -> dict:
    return MetaEnvelope(
        competencia_referencia="atual",
        versao_dataset="meta_v1",
        total=total,
        pagina=1,
        por_pagina=total,
    ).model_dump()


async def listar_datasets() -> dict:
    relacoes = {dataset["fonte_serving"] for dataset in DATASETS_CORE_ANS}
    counts = await _contar_relacoes(relacoes)
    datasets = []
    for dataset in DATASETS_CORE_ANS:
        row_count = counts.get(dataset["fonte_serving"])
        datasets.append(
            DatasetMetaResponse(
                nome=dataset["nome"],
                descricao=dataset["descricao"],
                cadencia=dataset["cadencia"],
                status="publicado" if row_count and row_count > 0 else "em_validacao",
                produto=PRODUTO_CORE_ANS,
                fonte_serving=dataset["fonte_serving"],
                row_count=row_count,
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
    relacoes = {
        endpoint["fonte_serving"]
        for endpoint in ENDPOINTS_CORE_ANS
        if endpoint.get("fonte_serving")
        and endpoint.get("fonte_serving") != "catalogo interno"
    }
    counts = await _contar_relacoes(relacoes)
    dados = []
    for endpoint in ENDPOINTS_CORE_ANS:
        fonte = endpoint.get("fonte_serving")
        row_count = counts.get(fonte) if fonte else None
        status = STATUS_DISPONIVEL
        if fonte and fonte != "catalogo interno":
            status = _status_por_row_count(
                row_count,
                endpoint.get("status_if_empty", STATUS_EM_VALIDACAO),
            )
        aparece = status == STATUS_DISPONIVEL
        payload = {
            "method": endpoint["method"],
            "path": endpoint["path"],
            "grupo": endpoint["grupo"],
            "status": status,
            "produto": PRODUTO_CORE_ANS,
            "fonte_serving": fonte,
            "requer_api_key": endpoint["requer_api_key"],
            "row_count": row_count,
            "aparece_catalogo_publico": aparece,
            "metodo": endpoint["method"],
            "rota": endpoint["path"],
            "descricao": endpoint["descricao"],
            "autenticacao": "sim" if endpoint["requer_api_key"] else "nao",
            "plano_minimo": "core",
            "camada": "ouro" if endpoint["path"].startswith("/v1") else "publico",
            "dataset_origem": fonte,
            "versao": "v1",
        }
        dados.append(EndpointMetaResponse(**payload).model_dump())
    return {"dados": dados, "meta": _meta_padrao(len(dados))}


async def listar_atualizacao() -> dict:
    async with SessionLocal() as session:
        result = await session.execute(
            text(
                """
                select
                    coalesce(fonte_ans, nome_job) as dataset,
                    max(finalizado_em) as ultima_atualizacao,
                    count(*) filter (where status = 'sucesso') as cargas_sucesso,
                    max(status) as ultimo_status
                from plataforma.job
                where status in ('sucesso', 'falha')
                group by coalesce(fonte_ans, nome_job)
                order by ultima_atualizacao desc nulls last
                limit 30
                """
            )
        )
        dados = [
            {
                "dataset": row["dataset"],
                "ultima_atualizacao": row["ultima_atualizacao"].isoformat()
                if row["ultima_atualizacao"]
                else None,
                "cargas_sucesso": row["cargas_sucesso"],
                "ultimo_status": row["ultimo_status"],
            }
            for row in result.mappings()
        ]
    return {"dados": dados, "meta": _meta_padrao(len(dados))}


async def listar_qualidade() -> dict:
    async with SessionLocal() as session:
        result = await session.execute(
            text(
                """
                select
                    dataset,
                    max(carregado_em) as carregado_em,
                    count(*) as versoes_ativas
                from plataforma.versao_dataset
                where status = 'ativo'
                group by dataset
                order by carregado_em desc nulls last
                limit 30
                """
            )
        )
        dados = [
            {
                "dataset": row["dataset"],
                "carregado_em": row["carregado_em"].isoformat() if row["carregado_em"] else None,
                "versoes_ativas": row["versoes_ativas"],
                "status": "ok",
            }
            for row in result.mappings()
        ]
    return {"dados": dados, "meta": _meta_padrao(len(dados))}
