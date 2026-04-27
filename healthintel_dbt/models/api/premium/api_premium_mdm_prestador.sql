select
    prestador_master_id,
    estabelecimento_master_id,
    operadora_master_id,
    cnes_canonico,
    cnpj_canonico,
    nome_prestador_canonico,
    tipo_prestador_canonico,
    cd_municipio_canonico,
    uf_canonica,
    documento_quality_status,
    status_mdm,
    mdm_confidence_score,
    mdm_created_at,
    mdm_updated_at
from {{ ref('consumo_premium_mdm_prestador') }}
