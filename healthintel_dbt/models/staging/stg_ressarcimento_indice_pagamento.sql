{{ config(tags=['delta_ans_100', 'ressarcimento_sus']) }}

with base as (
    select
        cast(
            nullif(regexp_replace(cast(competencia as text), '[^0-9]', '', 'g'), '')
            as integer
        )                                               as competencia,
        lpad(trim(coalesce(registro_ans, '')), 6, '0')  as registro_ans,
        cast(nullif(trim(cast(coalesce(indice_efetivo_pagamento, '0') as text)), '') as numeric(10, 4))
                                                        as indice_efetivo_pagamento,
        cast(nullif(trim(cast(coalesce(valor_total_cobrado, '0') as text)), '') as numeric(18, 2))
                                                        as valor_total_cobrado,
        cast(nullif(trim(cast(coalesce(valor_total_pago, '0') as text)), '') as numeric(18, 2))
                                                        as valor_total_pago,
        _carregado_em,
        _arquivo_origem,
        _lote_id
    from {{ source('bruto_ans', 'ressarcimento_indice_pagamento') }}
    where trim(coalesce(registro_ans, '')) != ''
)

select *
from base
where competencia is not null
