select
    operadora_master_id,
    registro_ans_canonico,
    cnpj_canonico,
    razao_social_canonica,
    nome_fantasia_canonico,
    modalidade_canonica,
    uf_canonica,
    municipio_sede_canonico,
    documento_quality_status,
    status_mdm,
    confidence_score as mdm_confidence_score,
    mdm_created_at,
    mdm_updated_at
from {{ ref('mdm_operadora_master') }}
where status_mdm = 'ATIVO'
