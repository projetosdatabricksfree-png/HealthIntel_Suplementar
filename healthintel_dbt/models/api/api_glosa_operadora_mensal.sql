{{
    config(
        materialized='table',
        tags=['core_ans', 'regulatorios_complementares'],
        post_hook=[
            "{{ criar_indice_api(this, 'registro_ans') }}",
            "{{ criar_indice_api(this, 'competencia') }}"
        ]
    )
}}

select
    stg.registro_ans,
    stg.competencia::integer as competencia,
    stg.tipo_glosa,
    stg.qt_glosa::bigint as qt_glosa,
    stg.valor_glosa::numeric(18, 4) as valor_glosa,
    stg.valor_faturado::numeric(18, 4) as valor_faturado,
    stg.taxa_glosa_calculada::numeric(18, 6) as taxa_glosa_calculada,
    stg.fonte_publicacao,
    stg._carregado_em,
    'glosa_operadora_mensal_v1' as versao_dataset
from {{ ref('stg_glosa') }} as stg
