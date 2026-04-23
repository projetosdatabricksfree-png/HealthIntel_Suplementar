-- depends_on: {{ ref('ref_competencia') }}

{{
    config(
        unique_key=['cd_municipio', 'operadora_id', 'competencia'],
        incremental_strategy='delete+insert',
        on_schema_change='sync_all_columns'
    )
}}

select
    cd_municipio,
    nm_municipio,
    sg_uf,
    nm_regiao,
    operadora_id,
    registro_ans,
    competencia,
    competencia as competencia_id,
    beneficiario_total as qt_beneficiario_ativo,
    total_beneficiarios_municipio,
    market_share_pct
from {{ ref('int_beneficiario_localidade_enriquecido') }}
{% if is_incremental() %}
where competencia in (
    select competencia
    from {{ ref('ref_competencia') }}
    order by competencia desc
    limit 3
)
{% endif %}
