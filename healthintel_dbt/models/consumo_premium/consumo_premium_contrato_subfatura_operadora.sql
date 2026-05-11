{{
    config(
        materialized='table',
        schema='consumo_premium_ans',
        tags=['consumo_premium', 'mdm_privado'],
        post_hook=[
            "{{ criar_indice_api(this, 'tenant_id') }}",
            "{{ criar_indice_api(this, 'operadora_master_id') }}"
        ]
    )
}}

-- Visão integrada contrato-subfatura-operadora para consumo premium.
-- Preserva tenant_id; não mistura tenants; não publica linhas com exceção bloqueante.

with contrato as (
    select
        tenant_id,
        contrato_master_id,
        operadora_master_id,
        numero_contrato_canonico,
        numero_contrato_normalizado,
        registro_ans_canonico,
        cnpj_operadora_canonico,
        tipo_contrato,
        vigencia_inicio,
        vigencia_fim,
        status_contrato,
        is_operadora_mdm_resolvida,
        is_cnpj_operadora_estrutural_valido,
        mdm_confidence_score,
        mdm_status,
        dt_processamento
    from {{ ref('consumo_premium_contrato_validado') }}
),

subfatura as (
    select
        tenant_id,
        subfatura_master_id,
        contrato_master_id,
        codigo_subfatura_canonico,
        codigo_subfatura_normalizado,
        numero_contrato_normalizado as sub_contrato_normalizado,
        competencia,
        centro_custo,
        unidade_negocio,
        vigencia_inicio as sub_vigencia_inicio,
        vigencia_fim as sub_vigencia_fim,
        status_subfatura,
        mdm_confidence_score,
        mdm_status,
        dt_processamento
    from {{ ref('consumo_premium_subfatura_validada') }}
),

operadora as (
    select
        operadora_master_id,
        registro_ans_canonico,
        razao_social_canonica,
        nome_fantasia_canonico,
        modalidade_canonica,
        uf_canonica,
        municipio_sede_canonico
    from {{ ref('mdm_operadora_master') }}
)

select
    c.tenant_id,
    c.contrato_master_id,
    s.subfatura_master_id,
    c.operadora_master_id,
    c.numero_contrato_canonico,
    c.numero_contrato_normalizado,
    c.registro_ans_canonico,
    c.cnpj_operadora_canonico,
    c.tipo_contrato,
    c.vigencia_inicio,
    c.vigencia_fim,
    c.status_contrato,
    s.codigo_subfatura_canonico,
    s.codigo_subfatura_normalizado,
    s.competencia,
    s.centro_custo,
    s.unidade_negocio,
    s.sub_vigencia_inicio,
    s.sub_vigencia_fim,
    s.status_subfatura,
    o.razao_social_canonica as operadora_razao_social,
    o.nome_fantasia_canonico as operadora_nome_fantasia,
    o.modalidade_canonica as operadora_modalidade,
    o.uf_canonica as operadora_uf,
    o.municipio_sede_canonico as operadora_municipio_sede,
    -- mdm_status e confidence: consolidado
    c.mdm_status,
    c.is_operadora_mdm_resolvida,
    c.is_cnpj_operadora_estrutural_valido,
    least(100, greatest(0, c.mdm_confidence_score))::numeric(5, 2) as quality_score_contrato,
    least(100, greatest(0, s.mdm_confidence_score))::numeric(5, 2) as quality_score_subfatura,
    least(100, greatest(0,
        (coalesce(c.mdm_confidence_score, 0) + coalesce(s.mdm_confidence_score, 0)) / 2.0
    ))::numeric(5, 2) as quality_score_publicacao,
    current_timestamp as dt_processamento
from contrato as c
left join subfatura as s
    on c.tenant_id = s.tenant_id
   and c.contrato_master_id = s.contrato_master_id
left join operadora as o
    on c.operadora_master_id = o.operadora_master_id
