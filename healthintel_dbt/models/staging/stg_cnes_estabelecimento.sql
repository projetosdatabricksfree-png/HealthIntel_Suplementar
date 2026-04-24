{{
    config(
        tags=['cnes']
    )
}}

with base as (
    select
        lpad(regexp_replace(cast(competencia as text), '[^0-9]', '', 'g'), 6, '0') as competencia,
        lpad(regexp_replace(cast(cnes as text), '[^0-9]', '', 'g'), 7, '0') as cnes,
        nullif(regexp_replace(cnpj, '[^0-9]', '', 'g'), '') as cnpj,
        upper(trim(coalesce(razao_social, 'nao informado'))) as razao_social,
        upper(trim(coalesce(nome_fantasia, 'nao informado'))) as nome_fantasia,
        upper(trim(coalesce(sg_uf, 'na'))) as sg_uf,
        lpad(regexp_replace(cast(cd_municipio as text), '[^0-9]', '', 'g'), 6, '0') as cd_municipio,
        upper(trim(coalesce(nm_municipio, 'nao informado'))) as nm_municipio,
        upper(trim(coalesce(tipo_unidade, 'nao informado'))) as tipo_unidade,
        upper(trim(coalesce(tipo_unidade_desc, 'nao informado'))) as tipo_unidade_desc,
        upper(trim(coalesce(esfera_administrativa, 'nao informado'))) as esfera_administrativa,
        coalesce(vinculo_sus, false) as vinculo_sus,
        coalesce(leitos_existentes, 0) as leitos_existentes,
        coalesce(leitos_sus, 0) as leitos_sus,
        cast(latitude as numeric(10, 6)) as latitude,
        cast(longitude as numeric(10, 6)) as longitude,
        upper(trim(coalesce(situacao, 'nao informado'))) as situacao,
        coalesce(fonte_publicacao, 'cnes_ans') as fonte_publicacao,
        _carregado_em,
        _arquivo_origem,
        _lote_id,
        _layout_id,
        _layout_versao_id,
        _hash_arquivo,
        _hash_estrutura,
        _status_parse,
        row_number() over (
            partition by
                lpad(regexp_replace(cast(competencia as text), '[^0-9]', '', 'g'), 6, '0'),
                lpad(regexp_replace(cast(cnes as text), '[^0-9]', '', 'g'), 7, '0')
            order by _carregado_em desc, _lote_id desc
        ) as rn
    from {{ source('bruto_ans', 'cnes_estabelecimento') }}
)

select
    base.competencia,
    base.cnes,
    base.cnpj,
    base.razao_social,
    base.nome_fantasia,
    base.sg_uf,
    base.cd_municipio,
    base.nm_municipio,
    base.tipo_unidade,
    base.tipo_unidade_desc,
    base.esfera_administrativa,
    base.vinculo_sus,
    base.leitos_existentes,
    base.leitos_sus,
    base.latitude,
    base.longitude,
    base.situacao,
    base.fonte_publicacao,
    base._carregado_em,
    base._arquivo_origem,
    base._lote_id,
    base._layout_id,
    base._layout_versao_id,
    base._hash_arquivo,
    base._hash_estrutura,
    base._status_parse,
    case when municipio.codigo_ibge is null then false else true end as municipio_valido
from base
left join {{ ref('ref_municipio_ibge') }} as municipio
    on lpad(regexp_replace(cast(municipio.codigo_ibge as text), '[^0-9]', '', 'g'), 6, '0') = base.cd_municipio
where base.rn = 1
