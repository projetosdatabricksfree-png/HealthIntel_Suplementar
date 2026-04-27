{{
    config(
        post_hook=[
            "{{ criar_indice_api(this, 'competencia') }}",
            "{{ criar_indice_api(this, 'cnes_normalizado') }}",
            "{{ criar_indice_api(this, 'cd_municipio') }}",
            "{{ criar_indice_api(this, 'sg_uf') }}"
        ]
    )
}}

select
    estabelecimento_master_id,
    competencia,
    cnes,
    cnes_normalizado,
    cnpj_normalizado,
    razao_social,
    nome_fantasia,
    sg_uf,
    cd_municipio,
    nm_municipio,
    tipo_unidade,
    tipo_unidade_desc,
    cnes_formato_valido,
    cnpj_digito_valido,
    documento_quality_status,
    motivo_invalidade_documento,
    status_mdm,
    mdm_confidence_score,
    quality_score_cnes
from {{ ref('consumo_premium_cnes_estabelecimento_validado') }}
