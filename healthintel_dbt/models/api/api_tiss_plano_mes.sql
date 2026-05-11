{{
    config(
        materialized='table',
        tags=['delta_ans_100', 'tiss_subfamilias'],
        post_hook=[
            "{{ criar_indice_api(this, 'registro_ans') }}",
            "{{ criar_indice_api(this, 'competencia') }}",
            "{{ criar_indice_api(this, 'codigo_plano') }}"
        ]
    )
}}

with competencia_corte as (
    select (
        extract(year from current_date)::int * 100 +
        extract(month from current_date)::int
    ) - 24 as corte
)

select
    s.competencia,
    s.registro_ans,
    s.codigo_plano,
    s.segmentacao,
    s.tipo_contratacao,
    sum(s.qt_beneficiarios) as qt_beneficiarios,
    sum(s.qt_eventos)       as qt_eventos,
    sum(s.vl_pago)          as vl_pago,
    max(s._carregado_em)    as _carregado_em
from {{ ref('stg_tiss_dados_plano') }} as s
cross join competencia_corte as c
where s.competencia >= c.corte
group by
    s.competencia,
    s.registro_ans,
    s.codigo_plano,
    s.segmentacao,
    s.tipo_contratacao
