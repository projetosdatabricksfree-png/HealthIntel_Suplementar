with base as (
    select
        lpad(regexp_replace(cast(competencia as text), '[^0-9]', '', 'g'), 6, '0') as competencia,
        {{ normalizar_registro_ans('registro_ans') }} as registro_ans,
        lpad(regexp_replace(cast(codigo_ibge as text), '[^0-9]', '', 'g'), 7, '0') as codigo_ibge,
        upper(trim(municipio)) as municipio,
        upper(trim(uf)) as uf,
        coalesce(beneficiario_medico, 0) as beneficiario_medico,
        coalesce(beneficiario_odonto, 0) as beneficiario_odonto,
        coalesce(
            beneficiario_total,
            coalesce(beneficiario_medico, 0) + coalesce(beneficiario_odonto, 0)
        ) as beneficiario_total,
        _carregado_em,
        _arquivo_origem,
        _lote_id,
        row_number() over (
            partition by
                competencia,
                {{ normalizar_registro_ans('registro_ans') }},
                lpad(regexp_replace(cast(codigo_ibge as text), '[^0-9]', '', 'g'), 7, '0')
            order by _carregado_em desc, _lote_id desc
        ) as rn
    from {{ source('bruto_ans', 'sib_beneficiario_municipio') }}
)

select
    competencia,
    registro_ans,
    codigo_ibge,
    municipio,
    uf,
    beneficiario_medico,
    beneficiario_odonto,
    beneficiario_total,
    _carregado_em,
    _arquivo_origem,
    _lote_id
from base
where rn = 1
