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
    mdm_confidence_score,
    mdm_created_at,
    mdm_updated_at
from {{ ref('consumo_premium_mdm_operadora') }}
