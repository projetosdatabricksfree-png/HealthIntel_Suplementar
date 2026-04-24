{{
    config(
        materialized='table',
        schema='consumo_ans',
        tags=['consumo'],
        post_hook="{{ grant_select_to_cliente_reader() }}"
    )
}}

select
    trimestre,
    registro_ans,
    nome as razao_social,
    nome_fantasia,
    modalidade,
    uf_sede as uf,
    cnpj,
    ativo_total,
    passivo_total,
    patrimonio_liquido,
    receita_total,
    despesa_total,
    resultado_periodo,
    resultado_operacional,
    provisao_tecnica,
    margem_solvencia_calculada,
    sinistro_total,
    contraprestacao_total,
    sinistralidade_bruta,
    ressarcimento_sus,
    evento_indenizavel,
    sinistralidade_liquida,
    taxa_sinistralidade_calculada,
    indice_sinistralidade,
    margem_liquida_pct,
    cobertura_provisao,
    resultado_operacional_bruto,
    score_financeiro_base,
    rating_financeiro,
    parto_cesareo_pct,
    versao_financeira
from {{ ref('fat_financeiro_operadora_trimestral') }}
