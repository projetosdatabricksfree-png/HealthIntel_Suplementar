{{ config(tags=['mdm_privado'], severity='error') }}

-- Crosswalk privado nunca pode ligar registros de tenants diferentes.

select 'contrato' as tabela, x.xref_contrato_id::text as id
from {{ ref('xref_contrato_origem') }} x
inner join {{ ref('mdm_contrato_master') }} m on m.contrato_master_id = x.contrato_master_id
where x.tenant_id <> m.tenant_id

union all

select 'subfatura', x.xref_subfatura_id::text
from {{ ref('xref_subfatura_origem') }} x
inner join {{ ref('mdm_subfatura_master') }} m on m.subfatura_master_id = x.subfatura_master_id
where x.tenant_id <> m.tenant_id
