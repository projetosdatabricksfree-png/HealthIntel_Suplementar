{{ config(tags=['mdm_privado'], severity='error') }}

select 'contrato' as tabela, contrato_master_id::text as id, mdm_status
from {{ ref('mdm_contrato_master') }}
where mdm_status not in ('GOLDEN', 'CANDIDATE', 'QUARENTENA', 'DEPRECATED')

union all

select 'subfatura', subfatura_master_id::text, mdm_status
from {{ ref('mdm_subfatura_master') }}
where mdm_status not in ('GOLDEN', 'CANDIDATE', 'QUARENTENA', 'DEPRECATED')
