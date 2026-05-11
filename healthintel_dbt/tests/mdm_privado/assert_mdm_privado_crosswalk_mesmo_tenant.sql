{{ config(tags=['mdm_privado'], severity='error') }}

-- Crosswalk privado nunca pode ligar registros de tenants diferentes.

select
'contrato' as tabela,
x.xref_contrato_id::text as id
from {{ ref('xref_contrato_origem') }} as x
inner join {{ ref('mdm_contrato_master') }} as m on x.contrato_master_id = m.contrato_master_id
where x.tenant_id <> m.tenant_id

union all

select
'subfatura' as tabela,
x.xref_subfatura_id::text
from {{ ref('xref_subfatura_origem') }} as x
inner join {{ ref('mdm_subfatura_master') }} as m on x.subfatura_master_id = m.subfatura_master_id
where x.tenant_id <> m.tenant_id
