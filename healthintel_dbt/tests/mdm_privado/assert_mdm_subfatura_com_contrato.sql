{{ config(tags=['mdm_privado', 'mdm_privado_warning'], severity='warn') }}

-- Diagnóstico: subfaturas GOLDEN exigem contrato resolvido.

select subfatura_master_id, tenant_id
from {{ ref('mdm_subfatura_master') }}
where mdm_status = 'GOLDEN'
  and contrato_master_id is null
