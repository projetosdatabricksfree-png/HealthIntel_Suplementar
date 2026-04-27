{{
    config(
        tags=['quality', 'documento', 'cnes']
    )
}}

with fonte as (
    select
        competencia,
        cnes,
        cnpj,
        razao_social,
        nome_fantasia,
        sg_uf,
        cd_municipio,
        nm_municipio,
        tipo_unidade,
        tipo_unidade_desc,
        _carregado_em,
        _arquivo_origem,
        _lote_id,
        _layout_id,
        _layout_versao_id,
        _hash_arquivo,
        _hash_estrutura,
        _status_parse
    from {{ ref('stg_cnes_estabelecimento') }}
),

documento as (
    select
        'cnes_estabelecimento' as fonte_documento,
        competencia,
        cnes,
        {{ normalizar_cnes('cnes') }} as cnes_normalizado,
        {{ validar_cnes_formato('cnes') }} as cnes_formato_valido,
        cnpj as cnpj_original,
        {{ normalizar_cnpj('cnpj') }} as cnpj_normalizado,
        razao_social,
        nome_fantasia,
        sg_uf,
        cd_municipio,
        nm_municipio,
        tipo_unidade,
        tipo_unidade_desc,
        _carregado_em,
        _arquivo_origem,
        _lote_id,
        _layout_id,
        _layout_versao_id,
        _hash_arquivo,
        _hash_estrutura,
        _status_parse
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
),

classificado as (
    select
        *,
        case
            when not cnes_formato_valido then 'INVALIDO_FORMATO'
            else {{ validar_cnpj_completo('cnpj_normalizado') }}
        end as documento_quality_status
    from qualificado
)

select
    fonte_documento,
    competencia,
    cnes,
    cnes_normalizado,
    cnes_formato_valido,
    cnpj_original,
    cnpj_normalizado,
    cnpj_tamanho_valido,
    cnpj_digito_valido,
    cnpj_is_sequencia_invalida,
    documento_quality_status,
    case
        when not cnes_formato_valido then 'CNES normalizado diferente de 7 digitos'
        when documento_quality_status = 'VALIDO' then null
        when documento_quality_status = 'NULO' then 'CNPJ ausente na fonte CNES aprovada'
        when documento_quality_status = 'INVALIDO_FORMATO' then 'CNPJ normalizado diferente de 14 digitos'
        when documento_quality_status = 'SEQUENCIA_INVALIDA' then 'CNPJ composto por sequencia repetida'
        when documento_quality_status = 'INVALIDO_DIGITO' then 'CNPJ com digito verificador invalido'
        else null
    end as motivo_invalidade_documento,
    razao_social,
    nome_fantasia,
    sg_uf,
    cd_municipio,
    nm_municipio,
    tipo_unidade,
    tipo_unidade_desc,
    _carregado_em,
    _arquivo_origem,
    _lote_id,
    _layout_id,
    _layout_versao_id,
    _hash_arquivo,
    _hash_estrutura,
    _status_parse
from classificado

