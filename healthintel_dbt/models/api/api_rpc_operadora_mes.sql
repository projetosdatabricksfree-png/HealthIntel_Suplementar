{{
    config(
        materialized='table',
        tags=['delta_ans_100', 'regulatorios_complementares'],
        post_hook=[
            "{{ criar_indice_api(this, 'registro_ans') }}",
            "{{ criar_indice_api(this, 'competencia') }}",
            "{{ criar_indice_api(this, 'sg_uf') }}"
        ]
    )
}}

-- Retenção: apenas últimos 24 meses
with competencia_corte as (
    select (
        extract(year from current_date)::int * 100
        + extract(month from current_date)::int
    ) - 24 as corte
)

select
    s.competencia,
    s.registro_ans,
    s.cd_municipio,
    s.sg_uf,
    s.tipo_reclamacao,
    s.qt_reclamacoes,
    s.qt_resolvidas,
    s.indice_resolucao,
    s.nota_rpc,
    s._carregado_em
from {{ ref('stg_rpc') }} as s
cross join competencia_corte as c
where s.competencia >= c.corte
