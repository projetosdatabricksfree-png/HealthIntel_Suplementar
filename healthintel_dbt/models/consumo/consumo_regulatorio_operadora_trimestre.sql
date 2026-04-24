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
    razao_social,
    modalidade,
    qtd_reclamacoes,
    indice_reclamacao,
    demandas_nip,
    taxa_resolutividade,
    nivel_alerta,
    tendencia_regulatoria
from {{ ref('mart_regulatorio_operadora') }}
