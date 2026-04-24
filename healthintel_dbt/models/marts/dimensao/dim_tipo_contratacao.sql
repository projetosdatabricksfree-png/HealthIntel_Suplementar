{{
    config(materialized='table', tags=['dimensao', 'mart'])
}}

select
    row_number() over (order by tipo_contratacao) as tipo_contratacao_id,
    tipo_contratacao as codigo_tipo_contratacao,
    tipo_contratacao as descricao_tipo_contratacao,
    true as ativa
from (
    select distinct upper(coalesce(tipo_contratacao, 'NAO_INFORMADO')) as tipo_contratacao
    from {{ ref('stg_fip') }}
    union
    select distinct upper(coalesce(tipo_contratacao, 'NAO_INFORMADO')) as tipo_contratacao
    from {{ ref('stg_tiss_procedimento') }}
) as base
