{{
    config(materialized='table', tags=['dimensao', 'mart'])
}}

select
    row_number() over (order by modalidade) as modalidade_id,
    modalidade as codigo_modalidade,
    modalidade as descricao_modalidade,
    true as ativa
from (
    select distinct upper(coalesce(modalidade, 'NAO_INFORMADA')) as modalidade
    from {{ ref('stg_cadop') }}
) as base
