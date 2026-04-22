{{
    config(
        post_hook=[
            "{{ criar_indices(this, ['operadora_id']) }}",
            "{{ criar_indices(this, ['ranking_posicao']) }}"
        ]
    )
}}

with base as (
    select
        operadora_id,
        registro_ans,
        competencia,
        taxa_crescimento_12m,
        qt_beneficiario_ativo as beneficiario_atual,
        beneficiario_total_12m_anterior as beneficiario_12m_anterior,
        row_number() over (
            order by taxa_crescimento_12m desc nulls last, qt_beneficiario_ativo desc
        ) as ranking_posicao
    from {{ ref('fat_beneficiario_operadora') }}
    where taxa_crescimento_12m is not null
)

select
    base.operadora_id,
    base.registro_ans,
    dim.nome,
    base.competencia,
    base.taxa_crescimento_12m,
    base.beneficiario_atual,
    base.beneficiario_12m_anterior,
    base.ranking_posicao
from base
left join {{ ref('dim_operadora_atual') }} as dim
    on base.registro_ans = dim.registro_ans
