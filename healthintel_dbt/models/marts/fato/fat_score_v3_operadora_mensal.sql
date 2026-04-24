{{
    config(
        materialized='incremental',
        unique_key=['operadora_id', 'competencia_id'],
        incremental_strategy='delete+insert',
        on_schema_change='sync_all_columns',
        tags=['fato_v3', 'score_v3']
    )
}}

select
    operadora_id,
    competencia_id,
    registro_ans,
    nome,
    nome_fantasia,
    modalidade,
    uf_sede,
    trimestre_financeiro,
    score_core,
    score_regulatorio,
    score_financeiro,
    score_rede,
    score_estrutural,
    score_completo,
    score_v3_final,
    versao_metodologia
from {{ ref('int_score_v3_componentes') }}
{% if is_incremental() %}
where competencia_id in (
    select competencia
    from {{ ref('ref_competencia') }}
    order by competencia desc
    limit 4
)
{% endif %}
