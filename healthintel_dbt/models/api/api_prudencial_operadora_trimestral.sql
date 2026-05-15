{{
    config(
        materialized='table',
        tags=['core_ans', 'regulatorios_complementares'],
        post_hook=[
            "{{ criar_indice_api(this, 'registro_ans') }}",
            "{{ criar_indice_api(this, 'trimestre') }}"
        ]
    )
}}

select
    stg.registro_ans,
    stg.trimestre,
    stg.margem_solvencia::numeric(18, 4) as margem_solvencia,
    stg.capital_minimo_requerido::numeric(18, 4) as capital_minimo_requerido,
    stg.capital_disponivel::numeric(18, 4) as capital_disponivel,
    stg.indice_liquidez::numeric(18, 4) as indice_liquidez,
    stg.situacao_prudencial,
    stg.situacao_inadequada,
    stg.fonte_publicacao,
    stg._carregado_em,
    'prudencial_operadora_trimestral_v1' as versao_dataset
from {{ ref('stg_prudencial') }} as stg
