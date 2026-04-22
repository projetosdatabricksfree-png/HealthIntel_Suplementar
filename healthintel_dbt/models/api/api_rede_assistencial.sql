{{
    config(
        materialized='table',
        tags=['rede'],
        post_hook=[
            "{{ criar_indices(this, ['operadora_id', 'cd_municipio', 'competencia']) }}"
        ]
    )
}}

select
    cobertura.operadora_id,
    cobertura.registro_ans,
    dim.nome,
    dim.nome_fantasia,
    dim.modalidade,
    dim.uf_sede,
    cobertura.competencia,
    cobertura.competencia_id,
    cobertura.cd_municipio,
    cobertura.nm_municipio,
    cobertura.sg_uf,
    cobertura.nm_regiao,
    cobertura.segmento,
    cobertura.pop_estimada_ibge,
    cobertura.porte_municipio,
    cobertura.qt_prestador,
    cobertura.qt_especialidade_disponivel,
    cobertura.beneficiario_total,
    cobertura.qt_prestador_por_10k_beneficiarios,
    cobertura.limiar_prestador_por_10k,
    cobertura.limiar_especialidade_por_10k,
    cobertura.tem_cobertura,
    cobertura.cobertura_minima_atendida,
    densidade.qt_municipio_coberto,
    densidade.qt_uf_coberto,
    densidade.pct_municipios_cobertos,
    densidade.pct_ufs_cobertos,
    densidade.score_rede,
    cobertura.versao_dataset
from {{ ref('fat_cobertura_rede_municipio') }} as cobertura
left join {{ ref('fat_densidade_rede_operadora') }} as densidade
    on densidade.operadora_id = cobertura.operadora_id
    and densidade.competencia = cobertura.competencia
inner join {{ ref('dim_operadora_atual') }} as dim
    on dim.operadora_id = cobertura.operadora_id
