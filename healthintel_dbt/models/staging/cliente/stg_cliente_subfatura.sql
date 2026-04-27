{{
    config(
        tags=['staging', 'cliente', 'privado']
    )
}}

with origem as (
    select
        tenant_id,
        id_carga,
        source_system,
        fonte_arquivo,
        hash_arquivo,
        competencia,
        numero_contrato,
        codigo_subfatura,
        centro_custo,
        unidade_negocio,
        vigencia_inicio,
        vigencia_fim,
        status_subfatura,
        dt_carga
    from {{ source('bruto_cliente', 'subfatura') }}
    where tenant_id is not null
      and trim(tenant_id) <> ''
)

select
    nullif(trim(tenant_id), '') as tenant_id,
    id_carga,
    nullif(trim(source_system), '') as source_system,
    nullif(trim(fonte_arquivo), '') as fonte_arquivo,
    hash_arquivo,
    competencia,
    nullif(trim(numero_contrato), '') as numero_contrato_origem,
    nullif(upper(regexp_replace(coalesce(numero_contrato, ''), '[^A-Za-z0-9]', '', 'g')), '') as numero_contrato_normalizado,
    nullif(trim(codigo_subfatura), '') as codigo_subfatura_origem,
    nullif(upper(regexp_replace(coalesce(codigo_subfatura, ''), '[^A-Za-z0-9]', '', 'g')), '') as codigo_subfatura_normalizado,
    nullif(upper(trim(centro_custo)), '') as centro_custo,
    nullif(upper(trim(unidade_negocio)), '') as unidade_negocio,
    vigencia_inicio,
    vigencia_fim,
    nullif(upper(trim(status_subfatura)), '') as status_subfatura,
    dt_carga
from origem
