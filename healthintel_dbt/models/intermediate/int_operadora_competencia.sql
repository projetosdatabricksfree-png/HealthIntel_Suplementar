with sib as (
    select distinct
        registro_ans,
        competencia
    from {{ ref('stg_sib_operadora') }}
)

select
    sib.registro_ans,
    sib.competencia,
    cadop.nome,
    cadop.nome_fantasia,
    cadop.modalidade,
    cadop.uf_sede,
    cadop.municipio_sede,
    cadop.cnpj
from sib
inner join {{ ref('int_operadora_canonica') }} as cadop
    on sib.registro_ans = cadop.registro_ans
