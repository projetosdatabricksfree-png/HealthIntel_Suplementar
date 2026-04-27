{{ config(tags=['mdm_privado', 'mdm_privado_warning'], severity='warn') }}

-- Diagnóstico: contratos GOLDEN devem ter operadora_master_id resolvida.
-- QUARENTENA pode não ter, por design — não bloqueia o gate.

select contrato_master_id, tenant_id
from {{ ref('mdm_contrato_master') }}
where mdm_status = 'GOLDEN'
  and operadora_master_id is null
