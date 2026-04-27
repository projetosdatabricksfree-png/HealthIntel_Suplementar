{{
    config(
        tags=['mdm', 'estabelecimento', 'xref']
    )
}}

select
    estabelecimento_master_id,
    'CNES' as sistema_origem,
    cnes_canonico as chave_origem_id,
    current_timestamp as mdm_created_at
from {{ ref('mdm_estabelecimento_master') }}
