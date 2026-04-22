{{
    config(
        post_hook=[
            "{{ criar_indices(this, ['cd_municipio', 'competencia']) }}",
            "{{ criar_indices(this, ['registro_ans']) }}"
        ]
    )
}}

select
    cd_municipio,
    nm_municipio,
    sg_uf,
    nm_regiao,
    modalidade as segmento,
    competencia,
    operadora_id,
    registro_ans,
    nome,
    nome_fantasia,
    modalidade,
    uf_sede,
    municipio,
    uf,
    beneficiario_total,
    total_beneficiarios_municipio,
    market_share_pct,
    hhi_municipio,
    concentracao_mercado,
    'market_share_v1' as versao_dataset
from {{ ref('fat_market_share_mensal') }}
