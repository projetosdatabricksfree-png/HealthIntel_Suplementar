{{ config(tags=['mdm_privado'], severity='error') }}

select
'contrato' as tabela,
contrato_master_id::text as id,
mdm_confidence_score
from {{ ref('mdm_contrato_master') }}
where mdm_confidence_score < 0 or mdm_confidence_score > 100

union all

select
'subfatura' as tabela,
subfatura_master_id::text,
mdm_confidence_score
from {{ ref('mdm_subfatura_master') }}
where mdm_confidence_score < 0 or mdm_confidence_score > 100
