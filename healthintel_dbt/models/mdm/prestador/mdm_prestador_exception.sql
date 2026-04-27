{{
    config(
        tags=['mdm', 'prestador', 'exception']
    )
}}

select
    prestador_master_id,
    cnes_canonico,
    cnpj_canonico,
    'DOCUMENTO_INVALIDO' as tipo_excecao,
    documento_quality_status as detalhe_excecao,
    current_timestamp as mdm_created_at
from {{ ref('mdm_prestador_master') }}
where confidence_score < 50
