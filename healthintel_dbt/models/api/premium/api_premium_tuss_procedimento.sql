{{
    config(
        post_hook=[
            "{{ criar_indice_api(this, 'codigo_tuss') }}",
            "{{ criar_indice_api(this, 'versao_tuss') }}"
        ]
    )
}}

-- Superfície de serviço premium para catálogo TUSS.
-- Modo CI sintético — não comercial (ver docs/produto/tiss_tuss_premium.md).
-- Exclusivamente para a Sprint 32 e FastAPI futura.

select
    codigo_tuss,
    descricao_tuss,
    grupo,
    subgrupo,
    capitulo,
    vigencia_inicio,
    vigencia_fim,
    versao_tuss,
    is_tuss_vigente,
    rol_segmento,
    rol_obrigatorio_medico,
    rol_obrigatorio_odonto,
    rol_carencia_dias,
    rol_vigencia_inicio,
    rol_vigencia_fim,
    quality_score_tuss,
    dt_processamento
from {{ ref('dim_tuss_procedimento') }}