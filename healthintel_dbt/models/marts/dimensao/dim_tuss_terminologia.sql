{{
    config(
        materialized='table',
        schema='nucleo_ans',
        tags=['dimensao', 'tuss']
    )
}}

select
    codigo_tuss,
    descricao,
    grupo,
    subgrupo,
    capitulo,
    vigencia_inicio,
    coalesce(vigencia_fim, cast('9999-12-31' as date)) as vigencia_fim,
    vigencia_inicio as versao_tuss,
    case
        when coalesce(vigencia_fim, cast('9999-12-31' as date)) >= current_date then true
        else false
    end as is_tuss_vigente,
    current_timestamp as dt_processamento
from {{ ref('stg_tuss_terminologia') }}