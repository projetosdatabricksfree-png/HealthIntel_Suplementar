{{
    config(
        tags=['delta_ans_100', 'produto_plano']
    )
}}

with base as (
    select
        lpad(trim(coalesce(registro_ans, '')), 6, '0') as registro_ans,
        trim(codigo_produto)                            as codigo_produto,
        upper(trim(nome_produto))                       as nome_produto,
        upper(trim(coalesce(segmentacao, '')))          as segmentacao,
        upper(trim(coalesce(tipo_contratacao, '')))     as tipo_contratacao,
        upper(trim(coalesce(abrangencia_geografica, ''))) as abrangencia_geografica,
        upper(trim(coalesce(cobertura_area, '')))       as cobertura_area,
        upper(trim(coalesce(modalidade, '')))           as modalidade,
        upper(trim(coalesce(uf_comercializacao, '')))   as uf_comercializacao,
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
                trim(codigo_produto)
            order by _carregado_em desc, _lote_id desc
        ) as rn
    from {{ source('bruto_ans', 'produto_caracteristica') }}
    where trim(coalesce(registro_ans, '')) != ''
      and trim(coalesce(codigo_produto, '')) != ''
)

select
    registro_ans,
    codigo_produto,
    nome_produto,
    segmentacao,
    tipo_contratacao,
    abrangencia_geografica,
    cobertura_area,
    modalidade,
    uf_comercializacao,
    competencia,
    _carregado_em,
    _arquivo_origem,
    _lote_id
from base
where rn = 1
