{{ config(materialized='table', schema='consumo_ans', tags=['consumo']) }}

select
    registro_ans,
    razao_social,
    trimestre,
    nivel_alerta,
    tendencia_regulatoria,
    demandas_nip as qtd_processos_ativos,
    cast(null as numeric) as multas_total,
    cast(null as numeric) as idss_score,
    indice_reclamacao
from {{ ref('mart_regulatorio_operadora') }}
