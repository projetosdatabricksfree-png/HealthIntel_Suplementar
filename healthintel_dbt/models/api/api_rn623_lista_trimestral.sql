{{
    config(
        post_hook=[
            "{{ criar_indice_api(this, 'trimestre') }}",
            "{{ criar_indice_api(this, 'tipo_lista') }}"
        ]
    )
}}

select
    lista.trimestre,
    lista.tipo_lista,
    lista.registro_ans,
    dim.nome,
    dim.nome_fantasia,
    dim.modalidade,
    dim.uf_sede,
    lista.total_nip,
    lista.beneficiarios,
    lista.igr,
    lista.meta_igr,
    lista.elegivel,
    lista.observacao
from {{ ref('stg_rn623_lista') }} as lista
left join {{ ref('dim_operadora_atual') }} as dim
    on lista.registro_ans = dim.registro_ans
