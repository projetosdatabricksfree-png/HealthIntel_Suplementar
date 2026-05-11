{{
    config(
        tags=['delta_ans_100', 'tuss_oficial']
    )
}}

with base as (
    select
        trim(codigo_tuss)                           as codigo_tuss,
        upper(trim(descricao))                      as descricao,
        trim(coalesce(versao_tuss, ''))             as versao_tuss,
        case
            when trim(coalesce(cast(vigencia_inicio as text), '')) = '' then null
            else vigencia_inicio
        end                                         as vigencia_inicio,
        case
            when trim(coalesce(cast(vigencia_fim as text), '')) = '' then null
            else vigencia_fim
        end                                         as vigencia_fim,
        coalesce(cast(is_tuss_vigente as boolean), true) as is_tuss_vigente,
        upper(trim(coalesce(grupo, '')))            as grupo,
        upper(trim(coalesce(subgrupo, '')))         as subgrupo,
        _carregado_em,
        _arquivo_origem,
        _lote_id,
        row_number() over (
            partition by trim(codigo_tuss), trim(coalesce(versao_tuss, ''))
            order by _carregado_em desc, _lote_id desc
        ) as rn
    from {{ source('bruto_ans', 'tuss_terminologia_oficial') }}
    where trim(coalesce(codigo_tuss, '')) != ''
      and trim(coalesce(descricao, '')) != ''
)

select
    codigo_tuss,
    descricao,
    versao_tuss,
    vigencia_inicio,
    vigencia_fim,
    is_tuss_vigente,
    grupo,
    subgrupo,
    _carregado_em,
    _arquivo_origem,
    _lote_id
from base
where rn = 1
