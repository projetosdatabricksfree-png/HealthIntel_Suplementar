{{
    config(
        tags=['mdm', 'operadora', 'xref']
    )
}}

select
    operadora_master_id,
    'CADOP' as sistema_origem,
    registro_ans_canonico as chave_origem_id,
    current_timestamp as mdm_created_at
from {{ ref('mdm_operadora_master') }}
