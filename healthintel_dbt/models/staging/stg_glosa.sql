{{
    config(tags=['financeiro_v2'])
}}

with base as (
    select
        upper(trim(competencia)) as competencia,
        {{ normalizar_registro_ans('registro_ans') }} as registro_ans,
        lower(trim(coalesce(tipo_glosa, 'nao_informada'))) as tipo_glosa,
        cast(qt_glosa as integer) as qt_glosa,
        cast(valor_glosa as numeric(18,4)) as valor_glosa,
        cast(valor_faturado as numeric(18,4)) as valor_faturado,
        coalesce(fonte_publicacao, 'glosa_ans') as fonte_publicacao,
        _carregado_em,
        _arquivo_origem,
        _lote_id,
        case
            when coalesce(valor_faturado, 0) = 0 then 0
            else cast(valor_glosa as numeric(18,4)) / nullif(cast(valor_faturado as numeric(18,4)), 0)
        end as taxa_glosa_calculada,
        row_number() over (
            partition by upper(trim(competencia)), {{ normalizar_registro_ans('registro_ans') }}, lower(trim(coalesce(tipo_glosa, 'nao_informada')))
            order by _carregado_em desc, _lote_id desc
        ) as rn
    from {{ source('bruto_ans', 'glosa_operadora_mensal') }}
)

select
    competencia,
    registro_ans,
    tipo_glosa,
    qt_glosa,
    valor_glosa,
    valor_faturado,
    taxa_glosa_calculada,
    fonte_publicacao,
    _carregado_em,
    _arquivo_origem,
    _lote_id
from base
where rn = 1
