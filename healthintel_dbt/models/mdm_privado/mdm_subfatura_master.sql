{{
    config(
        tags=['mdm_privado', 'subfatura', 'master']
    )
}}

-- Subfatura master por tenant. Resolve contrato pelo par
-- (tenant_id, numero_contrato_normalizado). Sem mistura entre tenants.

with stg as (
    select
        tenant_id,
        numero_contrato_origem,
        numero_contrato_normalizado,
        codigo_subfatura_origem,
        codigo_subfatura_normalizado,
        centro_custo,
        unidade_negocio,
        vigencia_inicio,
        vigencia_fim,
        status_subfatura,
        competencia
    from {{ ref('stg_cliente_subfatura') }}
    where tenant_id is not null
      and numero_contrato_normalizado is not null
      and codigo_subfatura_normalizado is not null
),

contrato as (
    select
        contrato_master_id,
        tenant_id,
        numero_contrato_normalizado
    from {{ ref('mdm_contrato_master') }}
),

resolvido as (
    select
        s.tenant_id,
        s.numero_contrato_normalizado,
        s.codigo_subfatura_normalizado,
        s.competencia,
        s.codigo_subfatura_origem as codigo_subfatura_canonico,
        s.centro_custo,
        s.unidade_negocio,
        s.vigencia_inicio,
        s.vigencia_fim,
        s.status_subfatura,
        c.contrato_master_id
    from stg as s
    left join contrato as c
        on s.tenant_id = c.tenant_id
       and s.numero_contrato_normalizado = c.numero_contrato_normalizado
),

agregado as (
    select
        tenant_id,
        numero_contrato_normalizado,
        codigo_subfatura_normalizado,
        competencia,
        max(codigo_subfatura_canonico) as codigo_subfatura_canonico,
        max(centro_custo)              as centro_custo,
        max(unidade_negocio)           as unidade_negocio,
        min(vigencia_inicio)           as vigencia_inicio,
        max(vigencia_fim)              as vigencia_fim,
        max(status_subfatura)          as status_subfatura,
        max(contrato_master_id)        as contrato_master_id,
        count(*)                       as ocorrencias_origem
    from resolvido
    group by tenant_id, numero_contrato_normalizado, codigo_subfatura_normalizado, competencia
),

duplicidade as (
    select
        tenant_id,
        numero_contrato_normalizado,
        codigo_subfatura_normalizado,
        competencia,
        ocorrencias_origem > 1 as duplicada_competencia
    from agregado
),

scored as (
    select
        a.*,
        a.contrato_master_id is not null as is_contrato_resolvido,
        d.duplicada_competencia,
        coalesce(a.contrato_master_id is null, false) as has_excecao_bloqueante,
        (
            case when a.tenant_id is not null then 20 else 0 end
          + case when a.codigo_subfatura_normalizado is not null then 25 else 0 end
          + case when a.contrato_master_id is not null then 30 else 0 end
          + case when a.centro_custo is not null or a.unidade_negocio is not null then 10 else 0 end
          + case when a.vigencia_inicio is not null or a.vigencia_fim is not null then 10 else 0 end
          + case when a.status_subfatura is not null then 5 else 0 end
        ) as score_calculado
    from agregado as a
    left join duplicidade as d
        on a.tenant_id = d.tenant_id
        and a.numero_contrato_normalizado = d.numero_contrato_normalizado
        and a.codigo_subfatura_normalizado = d.codigo_subfatura_normalizado
        and a.competencia = d.competencia
)

select
    md5(concat_ws(
        '|',
        'subfatura',
        tenant_id,
        numero_contrato_normalizado,
        codigo_subfatura_normalizado
    )) as subfatura_master_id,
    contrato_master_id,
    tenant_id,
    codigo_subfatura_canonico,
    codigo_subfatura_normalizado,
    numero_contrato_normalizado,
    competencia,
    centro_custo,
    unidade_negocio,
    vigencia_inicio,
    vigencia_fim,
    status_subfatura,
    is_contrato_resolvido,
    has_excecao_bloqueante,
    least(100, greatest(0, score_calculado)) as mdm_confidence_score,
    case
        when has_excecao_bloqueante then 'QUARENTENA'
        when score_calculado < 60 then 'QUARENTENA'
        when score_calculado < 85 then 'CANDIDATE'
        else 'GOLDEN'
    end as mdm_status,
    current_timestamp as dt_processamento
from scored
