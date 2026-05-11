{{ config(tags=['delta_ans_100', 'rede_prestadores']) }}

with base as (
    select
        lpad(trim(coalesce(registro_ans, '')), 6, '0')  as registro_ans,
        upper(trim(coalesce(razao_social, '')))         as razao_social,
        regexp_replace(coalesce(cnpj, ''), '[^0-9]', '', 'g') as cnpj,
        upper(trim(coalesce(modalidade, '')))           as modalidade,
        cast(nullif(trim(cast(data_cancelamento as text)), '') as date)
                                                        as data_cancelamento,
        upper(trim(coalesce(motivo_cancelamento, '')))  as motivo_cancelamento,
        upper(trim(coalesce(sg_uf, '')))                as sg_uf,
        row_number() over (
            partition by lpad(trim(coalesce(registro_ans, '')), 6, '0')
            order by _carregado_em desc
        )                                               as rn,
        _carregado_em,
        _arquivo_origem,
        _lote_id
    from {{ source('bruto_ans', 'operadora_cancelada') }}
    where trim(coalesce(registro_ans, '')) != ''
)

select *
from base
where rn = 1
