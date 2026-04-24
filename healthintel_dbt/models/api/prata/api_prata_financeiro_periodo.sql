{{
    config(
        materialized='table',
        tags=['prata', 'financeiro']
    )
}}

select
    financeiro.*,
    {{ taxa_aprovacao_dataset('diops', ref('int_financeiro_operadora_periodo')) }} as taxa_aprovacao_lote
from {{ ref('int_financeiro_operadora_periodo') }} as financeiro
