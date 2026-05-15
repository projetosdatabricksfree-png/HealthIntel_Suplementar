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
    api.nome,
    api.nome_fantasia,
    api.modalidade,
    api.uf_sede,
    api.trimestre,
    api.tipo_regime,
    api.ativo,
    api.data_inicio,
    api.data_fim,
    api.descricao,
    api.fonte_publicacao,
    api.versao_dataset
from {{ ref('api_regime_especial_operadora_trimestral') }} as api
