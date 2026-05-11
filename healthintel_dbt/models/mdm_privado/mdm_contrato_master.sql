{{
    config(
        tags=['mdm_privado', 'contrato', 'master']
    )
}}

with stg as (
    select
        tenant_id,
        registro_ans_origem,
        registro_ans_canonico,
        cnpj_operadora_origem,
        cnpj_operadora_canonico,
        cnpj_operadora_quality_status,
        numero_contrato_origem,
        numero_contrato_normalizado,
        tipo_contrato,
        vigencia_inicio,
        vigencia_fim,
        status_contrato
    from {{ ref('stg_cliente_contrato') }}
    where tenant_id is not null
      and numero_contrato_normalizado is not null
),

operadora_publica as (
    select
        operadora_master_id,
        registro_ans_canonico,
        cnpj_canonico
    from {{ ref('mdm_operadora_master') }}
),

resolvido as (
    select
        s.tenant_id,
        s.numero_contrato_normalizado,
        s.numero_contrato_origem as numero_contrato_canonico,
        s.registro_ans_canonico,
        s.cnpj_operadora_canonico,
        s.cnpj_operadora_quality_status,
        s.tipo_contrato,
        s.vigencia_inicio,
        s.vigencia_fim,
        s.status_contrato,
        op_reg.operadora_master_id  as operadora_master_id_por_registro,
        op_cnpj.operadora_master_id as operadora_master_id_por_cnpj,
        op_reg.cnpj_canonico        as cnpj_publico_por_registro
    from stg as s
    left join operadora_publica as op_reg
        on s.registro_ans_canonico = op_reg.registro_ans_canonico
       and s.registro_ans_canonico is not null
    left join operadora_publica as op_cnpj
        on s.cnpj_operadora_canonico = op_cnpj.cnpj_canonico
       and s.cnpj_operadora_canonico is not null
),

agregado as (
    select
        tenant_id,
        numero_contrato_normalizado,
        max(numero_contrato_canonico)        as numero_contrato_canonico,
        max(registro_ans_canonico)           as registro_ans_canonico,
        max(cnpj_operadora_canonico)         as cnpj_operadora_canonico,
        max(cnpj_operadora_quality_status)   as cnpj_operadora_quality_status,
        max(tipo_contrato)                   as tipo_contrato,
        min(vigencia_inicio)                 as vigencia_inicio,
        max(vigencia_fim)                    as vigencia_fim,
        max(status_contrato)                 as status_contrato,
        coalesce(
            max(operadora_master_id_por_registro),
            max(operadora_master_id_por_cnpj)
        ) as operadora_master_id,
        bool_or(
            operadora_master_id_por_registro is not null
            and cnpj_operadora_canonico is not null
            and cnpj_publico_por_registro is not null
            and cnpj_operadora_canonico <> cnpj_publico_por_registro
        ) as cnpj_divergente_mdm
    from resolvido
    group by tenant_id, numero_contrato_normalizado
),

scored as (
    select
        a.*,
        a.operadora_master_id is not null as is_operadora_mdm_resolvida,
        a.cnpj_operadora_quality_status = 'VALIDO' as is_cnpj_operadora_estrutural_valido,
        coalesce(a.cnpj_divergente_mdm, false) as has_excecao_bloqueante,
        (
            case when a.tenant_id is not null then 20 else 0 end
          + case when a.numero_contrato_normalizado is not null then 25 else 0 end
          + case when a.operadora_master_id is not null then 25 else 0 end
          + case when a.cnpj_operadora_quality_status = 'VALIDO' then 10 else 0 end
          + case when a.vigencia_inicio is not null or a.vigencia_fim is not null then 10 else 0 end
          + case when a.status_contrato is not null then 10 else 0 end
        ) as score_calculado
    from agregado as a
)

select
    md5(concat_ws(
        '|',
        'contrato',
        tenant_id,
        numero_contrato_normalizado,
        coalesce(registro_ans_canonico, ''),
        coalesce(cnpj_operadora_canonico, '')
    )) as contrato_master_id,
    tenant_id,
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
