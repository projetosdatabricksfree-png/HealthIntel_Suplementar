-- depends_on: {{ ref('ref_competencia') }}

{{
    config(
        materialized='incremental',
        unique_key=['operadora_id', 'cd_municipio', 'competencia', 'segmento'],
        incremental_strategy='delete+insert',
        on_schema_change='sync_all_columns',
        tags=['rede']
    )
}}

select
    competencia,
    competencia as competencia_id,
    operadora_id,
    registro_ans,
    nm_municipio,
    sg_uf,
    nm_regiao,
    cd_municipio,
    segmento,
    pop_estimada_ibge,
    porte_municipio,
    qt_prestador,
    qt_especialidade_disponivel,
    beneficiario_total,
    qt_prestador_por_10k_beneficiarios,
    limiar_prestador_por_10k,
    limiar_especialidade_por_10k,
    tem_cobertura,
    cobertura_minima_atendida,
    'rede_v1' as versao_dataset
from {{ ref('int_rede_assistencial_municipio') }}
{% if is_incremental() %}
where competencia in (
    select competencia
    from {{ ref('ref_competencia') }}
    order by competencia desc
    limit 3
)
{% endif %}
