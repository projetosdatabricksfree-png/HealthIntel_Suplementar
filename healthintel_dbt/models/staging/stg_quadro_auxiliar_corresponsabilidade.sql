{{
    config(
        tags=['delta_ans_100', 'produto_plano']
    )
}}

with base as (
    select
        lpad(trim(coalesce(registro_ans, '')), 6, '0')  as registro_ans,
        trim(coalesce(codigo_plano, ''))                as codigo_plano,
        upper(trim(coalesce(tipo_corresponsabilidade, ''))) as tipo_corresponsabilidade,
        cast(
            nullif(trim(cast(percentual_corresponsabilidade as text)), '')
            as numeric(7, 4)
        )                                               as percentual_corresponsabilidade,
        cast(
            nullif(trim(cast(valor_corresponsabilidade as text)), '')
            as numeric(18, 2)
        )                                               as valor_corresponsabilidade,
        trim(coalesce(descricao, ''))                   as descricao,
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
                upper(trim(coalesce(tipo_corresponsabilidade, '')))
            order by _carregado_em desc, _lote_id desc
        ) as rn
    from {{ source('bruto_ans', 'quadro_auxiliar_corresponsabilidade') }}
    where trim(coalesce(registro_ans, '')) != ''
)

select
    registro_ans,
    codigo_plano,
    tipo_corresponsabilidade,
    percentual_corresponsabilidade,
    valor_corresponsabilidade,
    descricao,
    competencia,
    _carregado_em,
    _arquivo_origem,
    _lote_id
from base
where rn = 1
