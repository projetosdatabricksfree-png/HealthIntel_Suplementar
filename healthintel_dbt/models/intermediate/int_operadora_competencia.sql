with sib as (
    select distinct
        registro_ans,
        competencia
    from {{ ref('stg_sib_operadora') }}
)

select
    operadora.operadora_id,
    sib.registro_ans,
    sib.competencia,
    operadora.nome,
    operadora.nome_fantasia,
    operadora.modalidade,
    operadora.uf_sede,
    operadora.municipio_sede,
    operadora.cnpj
from sib
inner join {{ ref('dim_operadora_atual') }} as operadora
    on sib.registro_ans = operadora.registro_ans
