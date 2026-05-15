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
    stg.modalidade,
    stg.modalidade_descricao,
    stg.taxa_resolutividade::numeric(12, 4) as taxa_resolutividade,
    stg.n_reclamacao_resolvida::bigint as n_reclamacao_resolvida,
    stg.n_reclamacao_total::bigint as n_reclamacao_total,
    stg.fonte_publicacao,
    stg._carregado_em,
    'taxa_resolutividade_operadora_trimestral_v1' as versao_dataset
from {{ ref('stg_taxa_resolutividade') }} as stg
