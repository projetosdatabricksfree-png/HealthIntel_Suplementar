{{
    config(
        tags=['quality', 'documento', 'cadop']
    )
}}

with fonte as (
    select
        registro_ans,
        nome,
        nome_fantasia,
        cnpj,
        _carregado_em,
        _arquivo_origem,
        _lote_id
    from {{ ref('stg_cadop') }}
),

documento as (
    select
        'cadop' as fonte_documento,
        registro_ans,
        {{ normalizar_registro_ans('registro_ans') }} as registro_ans_normalizado,
        {{ validar_registro_ans_formato('registro_ans') }} as registro_ans_formato_valido,
        nome,
        nome_fantasia,
        cnpj as cnpj_original,
        {{ normalizar_cnpj('cnpj') }} as cnpj_normalizado,
        _carregado_em,
        _arquivo_origem,
        _lote_id
    from fonte
),

qualificado as (
    select
        *,
        cnpj_normalizado is not null and length(cnpj_normalizado) = 14 as cnpj_tamanho_valido,
        case
            when cnpj_normalizado is null then false
            when cnpj_normalizado in (
                '00000000000000', '11111111111111', '22222222222222', '33333333333333',
                '44444444444444', '55555555555555', '66666666666666', '77777777777777',
                '88888888888888', '99999999999999'
            ) then true
            else false
        end as cnpj_is_sequencia_invalida,
        {{ validar_cnpj_digito('cnpj_normalizado') }} as cnpj_digito_valido
    from documento
)

select
    fonte_documento,
    registro_ans,
    registro_ans_normalizado,
    registro_ans_formato_valido,
    nome,
    nome_fantasia,
    cnpj_original,
    cnpj_normalizado,
    cnpj_tamanho_valido,
    cnpj_digito_valido,
    cnpj_is_sequencia_invalida,
    case
        when cnpj_normalizado is null then 'NULO'
        when cnpj_is_sequencia_invalida then 'SEQUENCIA_INVALIDA'
        when not cnpj_tamanho_valido then 'INVALIDO_FORMATO'
        when not cnpj_digito_valido then 'INVALIDO_DIGITO'
        else 'VALIDO'
    end as documento_quality_status,
    case
        when cnpj_normalizado is null then 'CNPJ ausente na fonte CADOP aprovada'
        when cnpj_is_sequencia_invalida then 'CNPJ composto por sequencia repetida'
        when not cnpj_tamanho_valido then 'CNPJ normalizado diferente de 14 digitos'
        when not cnpj_digito_valido then 'CNPJ com digito verificador invalido'
        else null
    end as motivo_invalidade_documento,
    _carregado_em,
    _arquivo_origem,
    _lote_id
from qualificado

