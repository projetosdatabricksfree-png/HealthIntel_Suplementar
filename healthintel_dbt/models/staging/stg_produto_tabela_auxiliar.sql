{{
    config(
        tags=['delta_ans_100', 'produto_plano']
    )
}}

with base as (
    select
        lpad(trim(coalesce(registro_ans, '')), 6, '0') as registro_ans,
        trim(coalesce(codigo_produto, ''))              as codigo_produto,
        upper(trim(coalesce(tipo_tabela, '')))          as tipo_tabela,
        upper(trim(coalesce(descricao_tabela, '')))     as descricao_tabela,
        trim(coalesce(codigo_item, ''))                 as codigo_item,
        upper(trim(coalesce(descricao_item, '')))       as descricao_item,
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
                trim(coalesce(codigo_produto, '')),
                trim(coalesce(codigo_item, ''))
            order by _carregado_em desc, _lote_id desc
        ) as rn
    from {{ source('bruto_ans', 'produto_tabela_auxiliar') }}
    where trim(coalesce(registro_ans, '')) != ''
)

select
    registro_ans,
    codigo_produto,
    tipo_tabela,
    descricao_tabela,
    codigo_item,
    descricao_item,
    competencia,
    _carregado_em,
    _arquivo_origem,
    _lote_id
from base
where rn = 1
