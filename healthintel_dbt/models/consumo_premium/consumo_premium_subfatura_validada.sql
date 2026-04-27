select
    subfatura_master_id,
    contrato_master_id,
    tenant_id,
    codigo_subfatura_canonico,
    codigo_subfatura_normalizado,
    numero_contrato_normalizado,
    competencia,
    centro_custo,
    unidade_negocio,
    vigencia_inicio,
    vigencia_fim,
    status_subfatura,
    is_contrato_resolvido,
    has_excecao_bloqueante,
    mdm_confidence_score,
    mdm_status,
    dt_processamento
from {{ ref('mdm_subfatura_master') }}
where tenant_id is not null
  and contrato_master_id is not null
  and mdm_status in ('GOLDEN', 'CANDIDATE')
  and not has_excecao_bloqueante
