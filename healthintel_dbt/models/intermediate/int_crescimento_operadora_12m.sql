select
    operadora_id,
    registro_ans,
    competencia,
    beneficiario_total,
    beneficiario_total_12m_anterior,
    taxa_crescimento_12m,
    beneficiario_media_12m
from {{ ref('int_beneficiario_operadora_enriquecido') }}
