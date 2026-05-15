{{
    config(
        materialized='table',
        schema='consumo_ans',
        tags=['core_ans', 'regulatorios_complementares', 'consumo'],
        post_hook="{{ grant_select_to_cliente_reader() }}"
    )
}}

select
    api.registro_ans,
    api.trimestre,
    api.modalidade,
    api.modalidade_descricao,
    api.taxa_resolutividade,
    api.n_reclamacao_resolvida,
    api.n_reclamacao_total,
    api.fonte_publicacao,
    api.versao_dataset
from {{ ref('api_taxa_resolutividade_operadora_trimestral') }} as api
