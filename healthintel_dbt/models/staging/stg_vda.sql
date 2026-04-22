{{
    config(tags=['financeiro_v2'])
}}

with base as (
    select
        upper(trim(competencia)) as competencia,
        {{ normalizar_registro_ans('registro_ans') }} as registro_ans,
        cast(valor_devido as numeric(18,4)) as valor_devido,
        cast(valor_pago as numeric(18,4)) as valor_pago,
        cast(saldo_devedor as numeric(18,4)) as saldo_devedor,
        lower(trim(coalesce(situacao_cobranca, 'nao_informada'))) as situacao_cobranca,
        cast(data_vencimento as date) as data_vencimento,
        coalesce(fonte_publicacao, 'vda_ans') as fonte_publicacao,
        _carregado_em,
        _arquivo_origem,
        _lote_id,
        case
            when coalesce(saldo_devedor, 0) > 0 then true
            else false
        end as inadimplente,
        row_number() over (
            partition by upper(trim(competencia)), {{ normalizar_registro_ans('registro_ans') }}
            order by _carregado_em desc, _lote_id desc
        ) as rn
    from {{ source('bruto_ans', 'vda_operadora_mensal') }}
)

select
    competencia,
    registro_ans,
    valor_devido,
    valor_pago,
    saldo_devedor,
    situacao_cobranca,
    data_vencimento,
    inadimplente,
    fonte_publicacao,
    _carregado_em,
    _arquivo_origem,
    _lote_id
from base
where rn = 1
