{{ config(tags=['delta_ans_100', 'rede_prestadores']) }}

with base as (
    select
        lpad(trim(coalesce(registro_ans, '')), 6, '0')  as registro_ans,
        upper(trim(coalesce(razao_social, '')))         as razao_social,
        upper(trim(coalesce(acreditadora, '')))         as acreditadora,
        upper(trim(coalesce(nivel_acreditacao, '')))    as nivel_acreditacao,
        cast(nullif(trim(cast(data_acreditacao as text)), '') as date)
                                                        as data_acreditacao,
        cast(nullif(trim(cast(data_validade as text)), '') as date)
                                                        as data_validade,
        row_number() over (
            partition by lpad(trim(coalesce(registro_ans, '')), 6, '0')
            order by _carregado_em desc
        )                                               as rn,
        _carregado_em,
        _arquivo_origem,
        _lote_id
    from {{ source('bruto_ans', 'operadora_acreditada') }}
    where trim(coalesce(registro_ans, '')) != ''
)

select *
from base
where rn = 1
