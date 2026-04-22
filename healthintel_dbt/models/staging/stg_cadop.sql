with base as (
    select
        lpad(trim(registro_ans), 6, '0') as registro_ans,
        upper(trim(razao_social)) as nome,
        upper(trim(nome_fantasia)) as nome_fantasia,
        upper(trim(modalidade)) as modalidade,
        upper(trim(uf)) as uf_sede,
        upper(trim(cidade)) as municipio_sede,
        regexp_replace(cnpj, '[^0-9]', '', 'g') as cnpj,
        _carregado_em,
        _arquivo_origem,
        _lote_id,
        row_number() over (
            partition by lpad(trim(registro_ans), 6, '0')
            order by _carregado_em desc, competencia desc, _lote_id desc
        ) as rn
    from {{ source('bruto_ans', 'cadop') }}
)

select
    registro_ans,
    nome,
    nome_fantasia,
    modalidade,
    uf_sede,
    municipio_sede,
    cnpj,
    _carregado_em,
    _arquivo_origem,
    _lote_id
from base
where rn = 1
