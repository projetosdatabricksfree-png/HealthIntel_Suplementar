select
    registro_ans,
    nome,
    nome_fantasia,
    modalidade,
    uf_sede,
    municipio_sede,
    cnpj
from {{ ref('stg_cadop') }}
