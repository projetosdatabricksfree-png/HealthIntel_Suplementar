{{
    config(
        post_hook=[
            "{{ criar_indice_api(this, 'registro_ans') }}",
            "{{ criar_indice_api(this, 'registro_ans, competencia') }}",
            "{{ criar_indice_api(this, 'score_v2') }}"
        ],
        tags=['score_v2', 'financeiro_v2']
    )
}}

select
    f.operadora_id,
    f.registro_ans,
    f.nome,
    f.nome_fantasia,
    f.modalidade,
    f.uf_sede,
    f.competencia,
    f.trimestre_financeiro,
    f.score_core,
    f.score_regulatorio,
    f.score_financeiro_trimestral,
    f.inadimplente,
    f.saldo_devedor,
    f.valor_devido,
    f.valor_pago,
    f.situacao_cobranca,
    f.taxa_glosa_calculada,
    f.valor_glosa_total,
    f.valor_faturado_total,
    f.penalizacao_vda,
    f.penalizacao_glosa,
    greatest(0, 100 - (f.penalizacao_vda + f.penalizacao_glosa)) as score_penalizacoes,
    f.score_v2_base,
    f.score_v2,
    f.rating,
    jsonb_build_object(
        'score_core', f.score_core,
        'score_regulatorio', f.score_regulatorio,
        'score_financeiro_trimestral', f.score_financeiro_trimestral,
        'penalizacao_vda', f.penalizacao_vda,
        'penalizacao_glosa', f.penalizacao_glosa,
        'score_penalizacoes', greatest(0, 100 - (f.penalizacao_vda + f.penalizacao_glosa))
    ) as componentes,
    f.versao_metodologia
from {{ ref('fat_score_v2_operadora_mensal') }} as f
