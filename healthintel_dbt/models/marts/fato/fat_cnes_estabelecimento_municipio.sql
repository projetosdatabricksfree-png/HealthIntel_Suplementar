-- depends_on: {{ ref('ref_competencia') }}

{{
    config(
        materialized='incremental',
        unique_key=['competencia', 'cd_municipio', 'tipo_unidade'],
        incremental_strategy='delete+insert',
        on_schema_change='sync_all_columns',
        tags=['cnes']
    )
}}

select
    competencia,
    cd_municipio,
    nm_municipio,
    sg_uf,
    nm_regiao,
    tipo_unidade,
    tipo_unidade_desc,
    pop_estimada_ibge,
    porte_municipio,
    total_estabelecimentos,
    total_estabelecimentos_vinculo_sus,
    total_leitos,
    total_leitos_sus,
    pct_leitos_sus,
    pct_vinculo_sus,
    'cnes_v1' as versao_dataset
from {{ ref('int_cnes_municipio_resumo') }}
{% if is_incremental() %}
where competencia in (
    select competencia
    from {{ ref('ref_competencia') }}
    order by competencia desc
    limit 3
)
{% endif %}
