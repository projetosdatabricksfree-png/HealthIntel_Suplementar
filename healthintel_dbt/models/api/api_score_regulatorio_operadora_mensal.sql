{{
    config(
        post_hook=[
            "{{ criar_indice_api(this, 'operadora_id') }}",
            "{{ criar_indice_api(this, 'competencia') }}",
            "{{ criar_indice_api(this, 'score_regulatorio') }}"
        ],
        tags=['regulatorio_v2']
    )
}}

select
    operadora_id,
    registro_ans,
    nome,
    nome_fantasia,
    modalidade,
    uf_sede,
    competencia,
    score_igr,
    score_nip,
    score_rn623,
    score_prudencial,
    score_taxa_resolutividade,
    regime_especial_ativo,
    tipo_regime,
    situacao_inadequada,
    qt_portabilidade_entrada,
    qt_portabilidade_saida,
    saldo_portabilidade,
    score_regulatorio_base,
    score_regulatorio,
    rating,
    versao_regulatoria
from {{ ref('fat_score_regulatorio_operadora_mensal') }}
