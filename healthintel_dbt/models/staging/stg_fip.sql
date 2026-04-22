{{
    config(tags=['financeiro'])
}}

with base as (
    select
        upper(trim(trimestre)) as trimestre,
        {{ normalizar_registro_ans('registro_ans') }} as registro_ans,
        lower(trim(coalesce(modalidade, 'nao_informada'))) as modalidade,
        lower(trim(coalesce(tipo_contratacao, 'nao_informada'))) as tipo_contratacao,
        cast(sinistro_total as numeric(18,4)) as sinistro_total,
        cast(contraprestacao_total as numeric(18,4)) as contraprestacao_total,
        cast(sinistralidade_bruta as numeric(12,4)) as sinistralidade_bruta,
        cast(ressarcimento_sus as numeric(18,4)) as ressarcimento_sus,
        cast(evento_indenizavel as numeric(18,4)) as evento_indenizavel,
        coalesce(fonte_publicacao, 'fip_ans') as fonte_publicacao,
        _carregado_em,
        _arquivo_origem,
        _lote_id,
        case
            when coalesce(contraprestacao_total, 0) = 0 then 0
            else sinistro_total - coalesce(ressarcimento_sus, 0)
        end as sinistralidade_liquida,
        row_number() over (
            partition by upper(trim(trimestre)), {{ normalizar_registro_ans('registro_ans') }}
            order by _carregado_em desc, _lote_id desc
        ) as rn
    from {{ source('bruto_ans', 'fip_operadora_trimestral') }}
)

select
    trimestre,
    registro_ans,
    modalidade,
    tipo_contratacao,
    sinistro_total,
    contraprestacao_total,
    sinistralidade_bruta,
    ressarcimento_sus,
    evento_indenizavel,
    sinistralidade_liquida,
    case
        when contraprestacao_total = 0 then 0
        else (sinistro_total / nullif(contraprestacao_total, 0)) * 100
    end as taxa_sinistralidade_calculada,
    fonte_publicacao,
    _carregado_em,
    _arquivo_origem,
    _lote_id
from base
where rn = 1
