{{ config(tags=['mdm_privado'], severity='error') }}

select 'mdm_contrato_master' as tabela, contrato_master_id::text as id
from {{ ref('mdm_contrato_master') }}
where tenant_id is null

union all

select 'mdm_subfatura_master', subfatura_master_id::text
from {{ ref('mdm_subfatura_master') }}
where tenant_id is null

union all

select 'xref_contrato_origem', xref_contrato_id::text
from {{ ref('xref_contrato_origem') }}
where tenant_id is null

union all

select 'xref_subfatura_origem', xref_subfatura_id::text
from {{ ref('xref_subfatura_origem') }}
where tenant_id is null

union all

select 'mdm_contrato_exception', contrato_master_id::text
from {{ ref('mdm_contrato_exception') }}
where tenant_id is null

union all

select 'mdm_subfatura_exception', subfatura_master_id::text
from {{ ref('mdm_subfatura_exception') }}
where tenant_id is null
