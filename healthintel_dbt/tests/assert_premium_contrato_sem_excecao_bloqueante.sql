{{ config(tags=['consumo_premium', 'premium', 'mdm_privado']) }}

select *
from {{ ref('consumo_premium_contrato_validado') }}
where tenant_id is null
   or has_excecao_bloqueante
   or mdm_status not in ('GOLDEN', 'CANDIDATE')
   or mdm_confidence_score < 0
   or mdm_confidence_score > 100
