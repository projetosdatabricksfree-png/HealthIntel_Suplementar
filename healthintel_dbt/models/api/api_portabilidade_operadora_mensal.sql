{{
    config(
        post_hook=[
            "{{ criar_indice_api(this, 'operadora_id') }}",
            "{{ criar_indice_api(this, 'competencia') }}"
        ],
        tags=['regulatorio_v2']
    )
}}

select
    d.operadora_id,
    s.registro_ans,
    d.nome,
    d.nome_fantasia,
    d.modalidade,
    d.uf_sede,
    s.competencia,
    s.competencia_data,
    s.modalidade_descricao,
    s.tipo_contratacao,
    s.qt_portabilidade_entrada,
    s.qt_portabilidade_saida,
    s.saldo_portabilidade,
    s.fonte_publicacao,
    'regulatorio_v2' as versao_dataset
from {{ ref('stg_portabilidade') }} as s
inner join {{ ref('dim_operadora_atual') }} as d
    on d.registro_ans = s.registro_ans
