{{
    config(
        materialized='view',
        schema='stg_ans',
        tags=['staging', 'tuss']
    )
}}

select
    codigo_tuss,
    descricao,
    grupo,
    subgrupo,
    capitulo,
    cast(vigencia_inicio as date) as vigencia_inicio,
    cast(nullif(trim(vigencia_fim), '') as date) as vigencia_fim,
    coalesce(nullif(trim(vigencia_fim), ''), '9999-12-31') as vigencia_fim_default
from {{ ref('ref_tuss') }}