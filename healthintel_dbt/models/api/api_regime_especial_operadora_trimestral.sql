{{
    config(
        materialized='table',
        tags=['core_ans', 'regulatorios_complementares'],
        post_hook=[
            "{{ criar_indice_api(this, 'registro_ans') }}",
            "{{ criar_indice_api(this, 'trimestre') }}",
            "{{ criar_indice_api(this, 'ativo') }}"
        ]
    )
}}

select
    row_number() over (order by stg.registro_ans, stg.trimestre, stg.data_inicio) as operadora_id,
    stg.registro_ans,
    dim.nome,
    dim.nome_fantasia,
    dim.modalidade,
    dim.uf_sede,
    stg.trimestre,
    stg.trimestre as trimestre_fim,
    stg.tipo_regime,
    stg.ativo,
    null::integer as duracao_trimestres,
    stg.data_inicio,
    stg.data_fim,
    stg.descricao,
    stg.fonte_publicacao,
    stg._carregado_em,
    'regime_especial_operadora_trimestral_v1' as versao_dataset
from {{ ref('stg_regime_especial') }} as stg
left join {{ ref('dim_operadora_atual') }} as dim
    on stg.registro_ans = dim.registro_ans
