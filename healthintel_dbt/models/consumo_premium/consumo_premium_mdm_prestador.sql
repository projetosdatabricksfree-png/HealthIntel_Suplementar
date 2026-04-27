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
    confidence_score as mdm_confidence_score,
    mdm_created_at,
    mdm_updated_at
from {{ ref('mdm_prestador_master') }}
where status_mdm = 'ATIVO'
