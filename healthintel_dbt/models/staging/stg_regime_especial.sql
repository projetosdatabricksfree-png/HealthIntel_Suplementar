{{
    config(tags=['regulatorio_v2'])
}}

with base as (
    select
        upper(trim(trimestre)) as trimestre,
        {{ normalizar_registro_ans('registro_ans') }} as registro_ans,
        lower(trim(tipo_regime)) as tipo_regime,
        cast(data_inicio as date) as data_inicio,
        cast(data_fim as date) as data_fim,
        coalesce(descricao, '') as descricao,
        coalesce(fonte_publicacao, 'regime_especial_ans') as fonte_publicacao,
        _carregado_em,
        _arquivo_origem,
        _lote_id,
        case
            when data_fim is null then true
            when cast(data_fim as date) > current_date then true
            else false
        end as ativo,
        row_number() over (
            partition by upper(trim(trimestre)), {{ normalizar_registro_ans('registro_ans') }}
            order by _carregado_em desc, _lote_id desc
        ) as rn
    from {{ source('bruto_ans', 'regime_especial_operadora_trimestral') }}
)

select
    trimestre,
    registro_ans,
    tipo_regime,
    data_inicio,
    data_fim,
    descricao,
    ativo,
    fonte_publicacao,
    _carregado_em,
    _arquivo_origem,
    _lote_id
from base
where rn = 1
