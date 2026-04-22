with base as (
    select
        cast(ano_base as integer) as ano_base,
        {{ normalizar_registro_ans('registro_ans') }} as registro_ans,
        cast(idss_total as numeric(6,4)) as idss_total,
        cast(idqs as numeric(6,4)) as idqs,
        cast(idga as numeric(6,4)) as idga,
        cast(idsm as numeric(6,4)) as idsm,
        cast(idgr as numeric(6,4)) as idgr,
        upper(trim(coalesce(faixa_idss, 'NAO_INFORMADO'))) as faixa_idss,
        {{ versao_metodologia_idss('ano_base') }} as versao_metodologia,
        fonte_publicacao,
        _carregado_em,
        _arquivo_origem,
        _lote_id,
        row_number() over (
            partition by cast(ano_base as integer), {{ normalizar_registro_ans('registro_ans') }}
            order by _carregado_em desc, _lote_id desc
        ) as rn
    from {{ source('bruto_ans', 'idss') }}
)

select
    ano_base,
    registro_ans,
    idss_total,
    idqs,
    idga,
    idsm,
    idgr,
    faixa_idss,
    versao_metodologia,
    fonte_publicacao,
    _carregado_em,
    _arquivo_origem,
    _lote_id
from base
where rn = 1
