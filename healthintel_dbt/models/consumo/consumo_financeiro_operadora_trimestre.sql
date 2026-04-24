{{ config(materialized='table', schema='consumo_ans', tags=['consumo']) }}

select
    registro_ans,
    nome as razao_social,
    trimestre,
    receita_total,
    taxa_sinistralidade_calculada as sinistralidade_pct,
    despesa_total as despesas_administrativas,
    resultado_operacional,
    margem_liquida_pct as margem_operacional_pct
from {{ ref('fat_financeiro_operadora_trimestral') }}
