{{
    config(
        post_hook=[
            "{{ criar_indice_api(this, 'competencia') }}",
            "{{ criar_indice_api(this, 'cnes_normalizado') }}",
            "{{ criar_indice_api(this, 'estabelecimento_master_id') }}"
        ]
    )
}}

with validado as (
    select
        competencia,
        cnes,
        cnes_normalizado,
        cnpj_normalizado,
        cnpj_tamanho_valido,
        cnpj_digito_valido,
        cnpj_is_sequencia_invalida,
        cnes_formato_valido,
        documento_quality_status,
        motivo_invalidade_documento,
        razao_social,
        nome_fantasia,
        sg_uf,
        cd_municipio,
        nm_municipio,
        tipo_unidade,
        tipo_unidade_desc,
        row_number() over (
            partition by competencia, cnes_normalizado
            order by _carregado_em desc nulls last, _lote_id desc nulls last
        ) as rn
    from {{ ref('dq_cnes_documento') }}
    where documento_quality_status = 'VALIDO'
      and cnes_formato_valido
      and cnpj_digito_valido
),

mdm_est as (
    select
        estabelecimento_master_id,
        cnes_canonico,
        status_mdm,
        confidence_score
    from {{ ref('mdm_estabelecimento_master') }}
),

mdm_pres as (
    select
        prestador_master_id,
        estabelecimento_master_id,
        cnes_canonico
    from {{ ref('mdm_prestador_master') }}
)

select
    mdm_est.estabelecimento_master_id,
    mdm_pres.prestador_master_id,
    validado.competencia,
    validado.cnes,
    validado.cnes_normalizado,
    validado.cnpj_normalizado,
    validado.razao_social,
    validado.nome_fantasia,
    validado.sg_uf,
    validado.cd_municipio,
    validado.nm_municipio,
    validado.tipo_unidade,
    validado.tipo_unidade_desc,
    validado.cnes_formato_valido,
    validado.cnpj_tamanho_valido,
    validado.cnpj_digito_valido,
    validado.cnpj_is_sequencia_invalida,
    -- is_cnpj_estrutural_valido: CNPJ tem tamanho 14, dígito válido e não é sequência repetida
    (
        validado.cnpj_tamanho_valido
        and validado.cnpj_digito_valido
        and not validado.cnpj_is_sequencia_invalida
    ) as is_cnpj_estrutural_valido,
    -- municipio_valido: código IBGE do município está preenchido e tem 6 dígitos
    (
        validado.cd_municipio is not null
        and length(validado.cd_municipio) = 6
    ) as municipio_valido,
    validado.documento_quality_status,
    validado.motivo_invalidade_documento,
    mdm_est.status_mdm,
    mdm_est.confidence_score as mdm_confidence_score,
    -- quality_score_cnes: 100 se VALIDO na sprint 28, 50 se sequencia, 20 se formato, 0 c.c.
    least(100, greatest(0,
        case validado.documento_quality_status
            when 'VALIDO' then 100
            when 'SEQUENCIA_INVALIDA' then 50
            when 'INVALIDO_FORMATO' then 20
            else 0
        end
    ))::numeric(5, 2) as quality_score_cnes,
    -- quality_score_mdm: herdado do confidence_score do MDM (já entre 0-100)
    least(100, greatest(0, mdm_est.confidence_score))::numeric(5, 2) as quality_score_mdm,
    -- quality_score_publicacao: placeholder para métricas de freshness e completude futuras
    100::numeric(5, 2) as quality_score_publicacao,
    current_timestamp as dt_processamento
from validado
inner join mdm_est
    on validado.cnes_normalizado = mdm_est.cnes_canonico
left join mdm_pres
    on mdm_est.estabelecimento_master_id = mdm_pres.estabelecimento_master_id
where validado.rn = 1