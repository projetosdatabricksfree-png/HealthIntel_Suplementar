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
        registro_ans,
        cnpj_operadora,
        numero_contrato,
        tipo_contrato,
        vigencia_inicio,
        vigencia_fim,
        status_contrato,
        dt_carga
    from {{ source('bruto_cliente', 'contrato') }}
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
    nullif(trim(registro_ans), '') as registro_ans_origem,
    {{ normalizar_registro_ans('registro_ans') }} as registro_ans_canonico,
    cnpj_operadora as cnpj_operadora_origem,
    {{ normalizar_cnpj('cnpj_operadora') }} as cnpj_operadora_canonico,
    {{ validar_cnpj_completo('cnpj_operadora') }} as cnpj_operadora_quality_status,
    nullif(trim(numero_contrato), '') as numero_contrato_origem,
    nullif(upper(regexp_replace(coalesce(numero_contrato, ''), '[^A-Za-z0-9]', '', 'g')), '') as numero_contrato_normalizado,
    nullif(upper(trim(tipo_contrato)), '') as tipo_contrato,
    vigencia_inicio,
    vigencia_fim,
    nullif(upper(trim(status_contrato)), '') as status_contrato,
    dt_carga
from origem
