{{
    config(
        materialized='table',
        schema='nucleo_ans',
        tags=['dimensao', 'tuss']
    )
}}

with tuss as (
    select
        codigo_tuss,
        descricao,
        grupo,
        subgrupo,
        capitulo,
        vigencia_inicio,
        vigencia_fim,
        versao_tuss,
        is_tuss_vigente
    from {{ ref('dim_tuss_terminologia') }}
),

rol as (
    select
        codigo_tuss,
        descricao as descricao_rol,
        segmento,
        obrigatorio_medico,
        obrigatorio_odonto,
        carencia_dias,
        cast(vigencia_inicio as date) as rol_vigencia_inicio,
        cast(nullif(vigencia_fim, '') as date) as rol_vigencia_fim
    from {{ ref('ref_rol_procedimento') }}
)

select
    tuss.codigo_tuss,
    tuss.descricao as descricao_tuss,
    tuss.grupo,
    tuss.subgrupo,
    tuss.capitulo,
    tuss.vigencia_inicio,
    tuss.vigencia_fim,
    tuss.versao_tuss,
    tuss.is_tuss_vigente,
    rol.segmento as rol_segmento,
    rol.obrigatorio_medico as rol_obrigatorio_medico,
    rol.obrigatorio_odonto as rol_obrigatorio_odonto,
    rol.carencia_dias as rol_carencia_dias,
    rol.rol_vigencia_inicio,
    rol.rol_vigencia_fim,
    -- quality_score_tuss: 100 se procedimento TUSS tem código e está vigente; 50 se existe mas não vigente
    least(100, greatest(0,
        case
            when tuss.codigo_tuss is not null and tuss.is_tuss_vigente then 100
            when tuss.codigo_tuss is not null then 50
            else 0
        end
    ))::numeric(5, 2) as quality_score_tuss,
    current_timestamp as dt_processamento
from tuss
left join rol
    on tuss.codigo_tuss = rol.codigo_tuss