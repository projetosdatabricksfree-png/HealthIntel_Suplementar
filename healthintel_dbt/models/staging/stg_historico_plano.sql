{{
    config(
        tags=['delta_ans_100', 'produto_plano']
    )
}}

with base as (
    select
        lpad(trim(coalesce(registro_ans, '')), 6, '0') as registro_ans,
        trim(coalesce(codigo_plano, ''))                as codigo_plano,
        upper(trim(coalesce(nome_plano, '')))           as nome_plano,
        upper(trim(coalesce(situacao, '')))             as situacao,
        case
            when trim(coalesce(cast(data_situacao as text), '')) = '' then null
            else data_situacao
        end                                             as data_situacao,
        upper(trim(coalesce(segmentacao, '')))          as segmentacao,
        upper(trim(coalesce(tipo_contratacao, '')))     as tipo_contratacao,
        upper(trim(coalesce(abrangencia_geografica, ''))) as abrangencia_geografica,
        upper(trim(coalesce(uf, '')))                   as uf,
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
                trim(coalesce(codigo_plano, ''))
            order by _carregado_em desc, _lote_id desc
        ) as rn
    from {{ source('bruto_ans', 'historico_plano') }}
    where trim(coalesce(registro_ans, '')) != ''
      and trim(coalesce(codigo_plano, '')) != ''
)

select
    registro_ans,
    codigo_plano,
    nome_plano,
    situacao,
    data_situacao,
    segmentacao,
    tipo_contratacao,
    abrangencia_geografica,
    uf,
    competencia,
    _carregado_em,
    _arquivo_origem,
    _lote_id
from base
where rn = 1
