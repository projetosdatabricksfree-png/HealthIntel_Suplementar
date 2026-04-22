select
    operadora_id,
    registro_ans,
    competencia,
    beneficiario_total,
    volatilidade_24m
from {{ ref('int_beneficiario_operadora_enriquecido') }}
