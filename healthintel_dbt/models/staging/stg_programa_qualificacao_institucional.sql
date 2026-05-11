{{ config(tags=['delta_ans_100', 'regulatorios_complementares']) }}

with base as (
    select
        cast(
            nullif(regexp_replace(cast(competencia as text), '[^0-9]', '', 'g'), '')
            as integer
        )                                               as competencia,
        lpad(trim(coalesce(registro_ans, '')), 6, '0')  as registro_ans,
        upper(trim(coalesce(nivel_qualificacao, '')))   as nivel_qualificacao,
        cast(nullif(trim(cast(coalesce(pontuacao_qualificacao, '0') as text)), '') as numeric(5, 2))
                                                        as pontuacao_qualificacao,
        cast(nullif(trim(cast(data_avaliacao as text)), '') as date)
                                                        as data_avaliacao,
        upper(trim(coalesce(status_qualificacao, '')))  as status_qualificacao,
        _carregado_em,
        _arquivo_origem,
        _lote_id
    from {{ source('bruto_ans', 'programa_qualificacao_institucional') }}
    where trim(coalesce(registro_ans, '')) != ''
)

select *
from base
where competencia is not null
