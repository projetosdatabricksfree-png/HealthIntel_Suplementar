{{
    config(
        materialized='table',
        tags=['delta_ans_100', 'tiss_subfamilias'],
        post_hook=[
            "{{ criar_indice_api(this, 'registro_ans') }}",
            "{{ criar_indice_api(this, 'competencia') }}",
            "{{ criar_indice_api(this, 'sg_uf') }}"
        ]
    )
}}

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
    s.nm_municipio,
    s.sg_uf,
    s.tipo_evento,
    sum(s.qt_internacoes) as qt_internacoes,
    sum(s.qt_diarias)     as qt_diarias,
    sum(s.vl_pago)        as vl_pago,
    sum(s.vl_informado)   as vl_informado,
    max(s._carregado_em)  as _carregado_em
from {{ ref('stg_tiss_hospitalar') }} as s
cross join competencia_corte as c
where s.competencia >= c.corte
group by
    s.competencia,
    s.registro_ans,
    s.cd_municipio,
    s.nm_municipio,
    s.sg_uf,
    s.tipo_evento
