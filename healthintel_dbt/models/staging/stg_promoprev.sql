{{ config(tags=['delta_ans_100', 'regulatorios_complementares']) }}

with base as (
    select
        cast(
            nullif(regexp_replace(cast(competencia as text), '[^0-9]', '', 'g'), '')
            as integer
        )                                               as competencia,
        lpad(trim(coalesce(registro_ans, '')), 6, '0')  as registro_ans,
        upper(trim(coalesce(tipo_programa, '')))         as tipo_programa,
        coalesce(cast(nullif(trim(cast(qt_beneficiarios_programa as text)), '') as integer), 0)
                                                         as qt_beneficiarios_programa,
        cast(nullif(trim(cast(coalesce(vl_investimento, '0') as text)), '') as numeric(18, 2))
                                                         as vl_investimento,
        cast(nullif(trim(cast(coalesce(indicador_participacao, '0') as text)), '') as numeric(10, 4))
                                                         as indicador_participacao,
        _carregado_em,
        _arquivo_origem,
        _lote_id
    from {{ source('bruto_ans', 'promoprev') }}
    where trim(coalesce(registro_ans, '')) != ''
)

select *
from base
where competencia is not null
