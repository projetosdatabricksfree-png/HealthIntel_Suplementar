{{
    config(
        unique_key=['operadora_id', 'competencia'],
        incremental_strategy='delete+insert',
        on_schema_change='sync_all_columns',
        tags=['financeiro_v2']
    )
}}

with base as (
    select
        {{ normalizar_registro_ans('registro_ans') }} as registro_ans,
        competencia,
        valor_devido,
        valor_pago,
        saldo_devedor,
        situacao_cobranca,
        data_vencimento,
        inadimplente,
        fonte_publicacao,
        _carregado_em,
        _arquivo_origem,
        _lote_id,
        row_number() over (
            partition by {{ normalizar_registro_ans('registro_ans') }}, competencia
            order by _carregado_em desc, _lote_id desc
        ) as rn
    from {{ ref('stg_vda') }}
),
streaks as (
    select
        *,
        sum(case when inadimplente then 0 else 1 end) over (
            partition by registro_ans
            order by competencia
            rows between unbounded preceding and current row
        ) as grupo_inadimplencia
    from base
    where rn = 1
),
calculado as (
    select
        *,
        case
            when inadimplente then row_number() over (
                partition by registro_ans, grupo_inadimplencia
                order by competencia
            )
            else 0
        end as meses_inadimplente_consecutivos
    from streaks
)

select
    d.operadora_id,
    calculado.registro_ans,
    d.nome,
    d.nome_fantasia,
    d.modalidade,
    d.uf_sede,
    calculado.competencia,
    calculado.valor_devido,
    calculado.valor_pago,
    calculado.saldo_devedor,
    calculado.situacao_cobranca,
    calculado.data_vencimento,
    calculado.inadimplente,
    calculado.meses_inadimplente_consecutivos,
    calculado.fonte_publicacao,
    calculado._carregado_em,
    calculado._arquivo_origem,
    calculado._lote_id,
    'vda_v1' as versao_dataset
from calculado
inner join {{ ref('dim_operadora_atual') }} as d
    on d.registro_ans = calculado.registro_ans
