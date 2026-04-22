with base as (
    select
        cast(regexp_replace(cast(competencia as text), '[^0-9]', '', 'g') as integer) as competencia,
        {{ normalizar_registro_ans('registro_ans') }} as registro_ans,
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
            partition by competencia, {{ normalizar_registro_ans('registro_ans') }}
            order by _carregado_em desc, _lote_id desc
        ) as rn
    from {{ source('bruto_ans', 'sib_beneficiario_operadora') }}
)

select
    competencia,
    registro_ans,
    beneficiario_medico,
    beneficiario_odonto,
    beneficiario_total,
    _carregado_em,
    _arquivo_origem,
    _lote_id
from base
where rn = 1
