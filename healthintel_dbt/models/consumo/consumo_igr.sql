{{
    config(
        materialized='table',
        schema='consumo_ans',
        tags=['consumo'],
        post_hook="{{ grant_select_to_cliente_reader() }}"
    )
}}

select
    trimestre,
    registro_ans,
    modalidade,
    porte,
    total_reclamacoes,
    beneficiarios,
    igr,
    meta_igr,
    atingiu_meta,
    _carregado_em
from {{ ref('api_prata_igr') }}
