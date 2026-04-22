select
    row_number() over (order by registro_ans) as operadora_id,
    registro_ans,
    nome,
    nome_fantasia,
    modalidade,
    uf_sede,
    municipio_sede,
    cnpj
from {{ ref('int_operadora_canonica') }}
