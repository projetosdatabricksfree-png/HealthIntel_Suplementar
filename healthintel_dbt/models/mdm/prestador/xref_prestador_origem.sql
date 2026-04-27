{{
    config(
        tags=['mdm', 'prestador', 'xref']
    )
}}

select
    prestador_master_id,
    'MDM_ESTABELECIMENTO' as sistema_origem,
    estabelecimento_master_id as chave_origem_id,
    current_timestamp as mdm_created_at
from {{ ref('mdm_prestador_master') }}
