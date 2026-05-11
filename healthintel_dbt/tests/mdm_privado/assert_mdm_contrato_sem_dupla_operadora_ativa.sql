{{ config(tags=['mdm_privado'], severity='error') }}

-- Mesmo (tenant_id, numero_contrato_normalizado) não pode resolver
-- mais de um operadora_master_id ATIVO simultaneamente.

select
tenant_id,
numero_contrato_normalizado,
count(distinct operadora_master_id) as qtd
from {{ ref('mdm_contrato_master') }}
where operadora_master_id is not null
  and mdm_status in ('GOLDEN', 'CANDIDATE')
group by tenant_id, numero_contrato_normalizado
having count(distinct operadora_master_id) > 1
