{{
    config(
        post_hook=[
            "{{ criar_indice_api(this, 'fonte_documento') }}",
            "{{ criar_indice_api(this, 'documento_quality_status') }}"
        ]
    )
}}

with documento as (
    select
        fonte_documento,
        documento_quality_status
    from {{ ref('dq_cadop_documento') }}

    union all

    select
        fonte_documento,
        documento_quality_status
    from {{ ref('dq_operadora_documento') }}

    union all

    select
        fonte_documento,
        documento_quality_status
    from {{ ref('dq_cnes_documento') }}

    union all

    select
        fonte_documento,
        documento_quality_status
    from {{ ref('dq_prestador_documento') }}
),

agregado as (
    select
        fonte_documento,
        documento_quality_status,
        count(*) as total_registro
    from documento
    group by 1, 2
),

totais as (
    select
        fonte_documento,
        sum(total_registro) as total_fonte,
        sum(
            case
                when documento_quality_status = 'VALIDO' then total_registro
                else 0
            end
        ) as total_valido
    from agregado
    group by 1
)

select
    agregado.fonte_documento,
    agregado.documento_quality_status,
    agregado.total_registro,
    totais.total_fonte,
    totais.total_valido,
    totais.total_fonte - totais.total_valido as total_invalido,
    round(
        totais.total_valido::numeric / nullif(totais.total_fonte, 0),
        4
    ) as taxa_valido,
    round(
        100 * totais.total_valido::numeric / nullif(totais.total_fonte, 0),
        2
    ) as quality_score_documental
from agregado
inner join totais
    on totais.fonte_documento = agregado.fonte_documento
