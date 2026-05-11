-- depends_on: {{ ref('ref_competencia') }}

{{
    config(
        materialized='incremental',
        unique_key=['cd_municipio', 'competencia', 'segmento'],
        incremental_strategy='delete+insert',
        on_schema_change='sync_all_columns',
        tags=['vazio']
    )
}}

with base as (
    select
        cd_municipio,
        nm_municipio,
        sg_uf,
        nm_regiao,
        competencia,
        segmento,
        count(distinct case when tem_cobertura then operadora_id end) as qt_operadora_presente,
        count(distinct case when not tem_cobertura then operadora_id end) as qt_operadora_sem_cobertura,
        count(distinct operadora_id) as qt_operadora_total
    from {{ ref('fat_cobertura_rede_municipio') }}
    group by cd_municipio, nm_municipio, sg_uf, nm_regiao, competencia, segmento
)

select
    cd_municipio,
    nm_municipio,
    sg_uf,
    nm_regiao,
    competencia,
    segmento,
    qt_operadora_presente,
    qt_operadora_sem_cobertura,
    qt_operadora_total,
    round(
        coalesce((qt_operadora_presente::numeric / nullif(qt_operadora_total, 0)) * 100, 0),
        2
    ) as pct_operadoras_com_cobertura,
    round(
        coalesce((qt_operadora_sem_cobertura::numeric / nullif(qt_operadora_total, 0)) * 100, 0),
        2
    ) as pct_operadoras_sem_cobertura,
    coalesce(qt_operadora_presente = 0, false) as vazio_total,
    coalesce(qt_operadora_sem_cobertura > 0 and qt_operadora_presente > 0, false) as vazio_parcial,
    'vazio_v1' as versao_dataset
from base
{% if is_incremental() %}
where competencia in (
    select competencia
    from {{ ref('ref_competencia') }}
    order by competencia desc
    limit 3
)
{% endif %}
