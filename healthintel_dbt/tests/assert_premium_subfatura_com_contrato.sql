{{ config(tags=['consumo_premium', 'premium', 'mdm_privado']) }}

select *
from {{ ref('consumo_premium_subfatura_validada') }}
where tenant_id is null
   or contrato_master_id is null
   or not is_contrato_resolvido
   or has_excecao_bloqueante
   or mdm_status not in ('GOLDEN', 'CANDIDATE')
