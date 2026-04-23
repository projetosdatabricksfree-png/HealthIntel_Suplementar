{{
    config(
        tags=['rede']
    )
}}

with base as (
    select
        lpad(regexp_replace(cast(competencia as text), '[^0-9]', '', 'g'), 6, '0') as competencia,
        {{ normalizar_registro_ans('registro_ans') }} as registro_ans,
        lpad(regexp_replace(cast(cd_municipio as text), '[^0-9]', '', 'g'), 7, '0') as cd_municipio,
        upper(trim(coalesce(nm_municipio, 'NAO INFORMADO'))) as nm_municipio,
        upper(trim(coalesce(sg_uf, 'NA'))) as sg_uf,
        upper(trim(segmento)) as segmento,
        upper(trim(coalesce(tipo_prestador, 'NAO INFORMADO'))) as tipo_prestador,
        coalesce(qt_prestador, 0) as qt_prestador,
        coalesce(qt_especialidade_disponivel, 0) as qt_especialidade_disponivel,
        fonte_publicacao,
        _carregado_em,
        _arquivo_origem,
        _lote_id,
        row_number() over (
            partition by
                competencia,
                {{ normalizar_registro_ans('registro_ans') }},
                lpad(regexp_replace(cast(cd_municipio as text), '[^0-9]', '', 'g'), 7, '0'),
                upper(trim(segmento)),
                upper(trim(coalesce(tipo_prestador, 'NAO INFORMADO')))
            order by _carregado_em desc, _lote_id desc
        ) as rn
    from {{ source('bruto_ans', 'rede_prestador_municipio') }}
)

select
    base.competencia,
    base.registro_ans,
    base.cd_municipio,
    base.nm_municipio,
    base.sg_uf,
    base.segmento,
    base.tipo_prestador,
    base.qt_prestador,
    base.qt_especialidade_disponivel,
    base.fonte_publicacao,
    base._carregado_em,
    base._arquivo_origem,
    base._lote_id,
    case when municipio.codigo_ibge is null then false else true end as municipio_valido
from base
left join {{ ref('ref_municipio_ibge') }} as municipio
    on cast(municipio.codigo_ibge as text) = base.cd_municipio
where base.rn = 1
