{{
    config(
        tags=['quality', 'documento', 'prestador', 'rede']
    )
}}

with fonte as (
    select
        competencia,
        registro_ans,
        cd_municipio,
        nm_municipio,
        sg_uf,
        segmento,
        tipo_prestador,
        qt_prestador,
        qt_especialidade_disponivel,
        fonte_publicacao,
        _carregado_em,
        _arquivo_origem,
        _lote_id
    from {{ ref('stg_rede_assistencial') }}
)

select
    'rede_assistencial_agregada' as fonte_documento,
    competencia,
    registro_ans,
    {{ normalizar_registro_ans('registro_ans') }} as registro_ans_normalizado,
    {{ validar_registro_ans_formato('registro_ans') }} as registro_ans_formato_valido,
    cd_municipio,
    nm_municipio,
    sg_uf,
    segmento,
    tipo_prestador,
    qt_prestador,
    qt_especialidade_disponivel,
    cast(null as text) as cnes,
    cast(null as text) as cnes_normalizado,
    false as cnes_formato_valido,
    cast(null as text) as cnpj_original,
    cast(null as text) as cnpj_normalizado,
    false as cnpj_tamanho_valido,
    false as cnpj_digito_valido,
    false as cnpj_is_sequencia_invalida,
    'NULO' as documento_quality_status,
    'Documento individual de prestador ausente no contrato atual de stg_rede_assistencial' as motivo_invalidade_documento,
    fonte_publicacao,
    _carregado_em,
    _arquivo_origem,
    _lote_id
from fonte
