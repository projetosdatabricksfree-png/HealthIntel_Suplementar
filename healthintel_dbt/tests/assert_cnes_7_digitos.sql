{{ config(tags=['quality', 'documento', 'cnes']) }}

select
    competencia,
    cnes,
    cnes_normalizado,
    documento_quality_status,
    motivo_invalidade_documento
from {{ ref('dq_cnes_documento') }}
where not cnes_formato_valido
