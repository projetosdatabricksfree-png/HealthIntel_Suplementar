{{
    config(
        materialized='table',
        post_hook=[
            "{{ criar_indices(this, ['cd_municipio', 'competencia']) }}"
        ]
    )
}}

with base as (
    select
        cd_municipio,
        nm_municipio,
        sg_uf,
        nm_regiao,
        competencia,
        sum(beneficiario_total) as total_beneficiarios,
        max(hhi_municipio) as hhi_municipio,
        avg(market_share_pct) as cobertura_media_pct,
        count(distinct operadora_id) as qtd_operadoras
    from {{ ref('int_metrica_municipio') }}
    group by 1, 2, 3, 4, 5
)

select
    cd_municipio,
    nm_municipio,
    sg_uf,
    nm_regiao,
    competencia,
    total_beneficiarios,
    hhi_municipio,
    cobertura_media_pct,
    qtd_operadoras as cobertura_rede,
    round(
        greatest(
            0,
            100
            - least(100, coalesce(hhi_municipio, 0) / 100)
            + least(20, ln(greatest(total_beneficiarios, 1)) * 5)
            + least(10, qtd_operadoras * 1.5)
        )::numeric,
        2
    ) as oportunidade_score
from base
