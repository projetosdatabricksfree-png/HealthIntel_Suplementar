{{
    config(
        materialized='incremental',
        unique_key=['operadora_id', 'trimestre_inicio'],
        incremental_strategy='delete+insert',
        on_schema_change='sync_all_columns',
        tags=['regulatorio_v2']
    )
}}

select
    d.operadora_id,
    s.registro_ans,
    d.nome,
    d.nome_fantasia,
    d.modalidade,
    d.uf_sede,
    s.trimestre as trimestre_inicio,
    case
        when s.data_fim is null then null
        else to_char(s.data_fim, 'YYYY') || 'T' || extract(quarter from s.data_fim)::int
    end as trimestre_fim,
    s.tipo_regime,
    s.ativo,
    case
        when s.data_fim is null then null
        else greatest(1, ((date_part('year', age(s.data_fim, s.data_inicio)) * 12
            + date_part('month', age(s.data_fim, s.data_inicio))) / 3)::int)
    end as duracao_trimestres,
    s.data_inicio,
    s.data_fim,
    s.fonte_publicacao,
    'regulatorio_v2' as versao_dataset
from {{ ref('stg_regime_especial') }} as s
inner join {{ ref('dim_operadora_atual') }} as d
    on s.registro_ans = d.registro_ans
