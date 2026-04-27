{{
    config(
        tags=['mdm', 'operadora', 'exception']
    )
}}

select
    operadora_master_id,
    registro_ans_canonico,
    cnpj_canonico,
    'DOCUMENTO_INVALIDO' as tipo_excecao,
    documento_quality_status as detalhe_excecao,
    current_timestamp as mdm_created_at
from {{ ref('mdm_operadora_master') }}
where confidence_score < 50
