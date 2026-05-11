{{
    config(
        tags=['delta_ans_100', 'produto_plano']
    )
}}

with base as (
    select
        lpad(trim(coalesce(registro_ans, '')), 6, '0') as registro_ans,
        trim(coalesce(codigo_plano, ''))                as codigo_plano,
        trim(coalesce(codigo_servico, ''))              as codigo_servico,
        upper(trim(coalesce(descricao_servico, '')))    as descricao_servico,
        upper(trim(coalesce(tipo_servico, '')))         as tipo_servico,
        cast(
            nullif(regexp_replace(cast(competencia as text), '[^0-9]', '', 'g'), '')
            as integer
        )                                               as competencia,
        _carregado_em,
        _arquivo_origem,
        _lote_id,
        row_number() over (
            partition by
                lpad(trim(coalesce(registro_ans, '')), 6, '0'),
                trim(coalesce(codigo_plano, '')),
                trim(coalesce(codigo_servico, ''))
            order by _carregado_em desc, _lote_id desc
        ) as rn
    from {{ source('bruto_ans', 'plano_servico_opcional') }}
    where trim(coalesce(registro_ans, '')) != ''
)

select
    registro_ans,
    codigo_plano,
    codigo_servico,
    descricao_servico,
    tipo_servico,
    competencia,
    _carregado_em,
    _arquivo_origem,
    _lote_id
from base
where rn = 1
