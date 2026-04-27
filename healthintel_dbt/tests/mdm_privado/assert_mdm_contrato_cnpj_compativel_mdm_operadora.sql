{{ config(tags=['mdm_privado'], severity='error') }}

-- Contrato GOLDEN não pode ter CNPJ divergente do MDM público.
-- QUARENTENA é o destino legítimo da divergência.

with contrato as (
    select
        c.contrato_master_id,
        c.tenant_id,
        c.cnpj_operadora_canonico,
        c.mdm_status,
        op.cnpj_canonico as cnpj_publico
    from {{ ref('mdm_contrato_master') }} c
    left join {{ ref('mdm_operadora_master') }} op
        on op.operadora_master_id = c.operadora_master_id
)

select contrato_master_id, tenant_id
from contrato
where mdm_status = 'GOLDEN'
  and cnpj_operadora_canonico is not null
  and cnpj_publico is not null
  and cnpj_operadora_canonico <> cnpj_publico
