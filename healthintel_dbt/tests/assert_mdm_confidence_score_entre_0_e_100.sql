select
    operadora_master_id,
    confidence_score
from {{ ref('mdm_operadora_master') }}
where confidence_score < 0 or confidence_score > 100
