{{
    config(
        unique_key=['operadora_id', 'ano_base'],
        incremental_strategy='delete+insert',
        on_schema_change='sync_all_columns'
    )
}}

select
    operadora_id,
    registro_ans,
    ano_base,
    idss_total,
    idqs,
    idga,
    idsm,
    idgr,
    faixa_idss,
    versao_metodologia,
    idss_total_normalizado,
    idqs_normalizado,
    idga_normalizado,
    idsm_normalizado,
    idgr_normalizado
from {{ ref('int_idss_normalizado') }}
{% if is_incremental() %}
where ano_base >= (
    select coalesce(max(ano_base), 0) - 1
    from {{ this }}
)
{% endif %}
