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
    demandas_nip,
    demandas_resolvidas,
    beneficiarios,
    taxa_intermediacao_resolvida,
    taxa_resolutividade,
    _carregado_em
from {{ ref('api_prata_nip') }}
