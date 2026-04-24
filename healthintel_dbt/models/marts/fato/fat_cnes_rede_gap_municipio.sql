{{
    config(
        materialized='incremental',
        unique_key=['competencia', 'cd_municipio', 'tipo_unidade'],
        incremental_strategy='delete+insert',
        on_schema_change='sync_all_columns',
        tags=['cnes', 'rede']
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
    total_estabelecimentos as estabelecimentos_cnes,
    qt_prestador_rede as prestadores_credenciados,
    gap_estabelecimentos_vs_rede as gap_absoluto,
    gap_pct,
    case
        when gap_estabelecimentos_vs_rede <= 0 then 'nenhum'
        when gap_pct >= 25 or gap_estabelecimentos_vs_rede >= 10 then 'critico'
        else 'leve'
    end as severidade_gap,
    flag_gap_critico,
    'cnes_rede_gap_v1' as versao_dataset
from {{ ref('int_cnes_x_rede_municipio') }}
{% if is_incremental() %}
where competencia in (
    select competencia
    from {{ ref('stg_cnes_estabelecimento') }}
    order by competencia desc
    limit 3
)
{% endif %}
