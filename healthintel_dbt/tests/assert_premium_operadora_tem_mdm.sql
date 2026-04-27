{{ config(tags=['consumo_premium', 'premium', 'mdm']) }}

select *
from {{ ref('consumo_premium_operadora_360_validado') }}
where operadora_master_id is null
   or status_mdm <> 'ATIVO'
   or mdm_confidence_score < 0
   or mdm_confidence_score > 100
