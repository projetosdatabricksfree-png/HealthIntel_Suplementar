{{
    config(
        materialized='table',
        tags=['delta_ans_100', 'regulatorios_complementares'],
        post_hook=[
            "{{ criar_indice_api(this, 'registro_ans') }}",
            "{{ criar_indice_api(this, 'competencia') }}"
        ]
    )
}}

select
    competencia,
    registro_ans,
    tipo_garantia,
    qt_ocorrencias,
    qt_resolvidas,
    qt_pendentes,
    prazo_medio_resolucao,
    _carregado_em
from {{ ref('stg_monitoramento_garantia_atendimento') }}
