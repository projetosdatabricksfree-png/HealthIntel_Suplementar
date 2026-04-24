{{ config(materialized='table', schema='consumo_ans', tags=['consumo']) }}

select
    registro_ans,
    razao_social,
    cd_municipio,
    nome_municipio,
    uf,
    competencia,
    qt_prestadores,
    densidade_por_10k,
    gap_leitos_cnes,
    classificacao_vazio
from {{ ref('mart_rede_assistencial') }}
