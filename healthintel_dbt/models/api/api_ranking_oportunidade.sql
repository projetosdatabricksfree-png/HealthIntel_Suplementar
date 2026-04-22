{{
    config(
        post_hook=[
            "{{ criar_indices(this, ['cd_municipio']) }}",
            "{{ criar_indices(this, ['ranking_posicao']) }}"
        ]
    )
}}

with base as (
    select
        cd_municipio,
        nm_municipio,
        sg_uf,
        competencia,
        oportunidade_score,
        row_number() over (
            order by oportunidade_score desc nulls last, total_beneficiarios desc
        ) as ranking_posicao
    from {{ ref('fat_oportunidade_municipio_mensal') }}
)

select * from base
