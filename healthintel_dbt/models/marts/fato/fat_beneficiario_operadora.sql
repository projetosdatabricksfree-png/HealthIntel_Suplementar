-- depends_on: {{ ref('ref_competencia') }}
-- depends_on: {{ ref('stg_sib_operadora') }}
{{
    config(
        unique_key=['operadora_id', 'competencia'],
        incremental_strategy='delete+insert',
        on_schema_change='sync_all_columns'
    )
}}
select
    operadora_id,
    registro_ans,
    competencia,
    competencia as competencia_id,
    beneficiario_total as qt_beneficiario_ativo,
    beneficiario_medico as qt_beneficiario_medico,
    beneficiario_odonto as qt_beneficiario_odonto,
    beneficiario_total_12m_anterior,
    beneficiario_media_12m,
    taxa_crescimento_12m,
    volatilidade_24m
from {{ ref('int_beneficiario_operadora_enriquecido') }}
{% if is_incremental() %}
where competencia in (
    select distinct competencia
    from {{ ref('stg_sib_operadora') }}
    order by competencia desc
    limit 3
)
{% endif %}
