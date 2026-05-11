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

-- Retenção: apenas últimos 24 meses nas tabelas API/consumo
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
    sum(s.qt_eventos)   as qt_eventos,
    sum(s.vl_pago)      as vl_pago,
    sum(s.vl_informado) as vl_informado,
    max(s._carregado_em) as _carregado_em
from {{ ref('stg_tiss_ambulatorial') }} as s
cross join competencia_corte as c
where s.competencia >= c.corte
group by
    s.competencia,
    s.registro_ans,
    s.cd_municipio,
    s.nm_municipio,
    s.sg_uf,
    s.tipo_evento
