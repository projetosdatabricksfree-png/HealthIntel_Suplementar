select
    contrato_master_id,
    tenant_id,
    operadora_master_id,
    numero_contrato_canonico,
    numero_contrato_normalizado,
    registro_ans_canonico,
    cnpj_operadora_canonico,
    tipo_contrato,
    vigencia_inicio,
    vigencia_fim,
    status_contrato,
    is_operadora_mdm_resolvida,
    is_cnpj_operadora_estrutural_valido,
    has_excecao_bloqueante,
    mdm_confidence_score,
    mdm_status,
    dt_processamento
from {{ ref('mdm_contrato_master') }}
where tenant_id is not null
  and mdm_status in ('GOLDEN', 'CANDIDATE')
  and not has_excecao_bloqueante
