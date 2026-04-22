{{
    config(
        unique_key=['operadora_id', 'competencia', 'tipo_glosa'],
        incremental_strategy='delete+insert',
        on_schema_change='sync_all_columns',
        tags=['financeiro_v2']
    )
}}

with base as (
    select
        {{ normalizar_registro_ans('registro_ans') }} as registro_ans,
        competencia,
        tipo_glosa,
        qt_glosa,
        valor_glosa,
        valor_faturado,
        taxa_glosa_calculada,
        fonte_publicacao,
        _carregado_em,
        _arquivo_origem,
        _lote_id,
        row_number() over (
            partition by {{ normalizar_registro_ans('registro_ans') }}, competencia, tipo_glosa
            order by _carregado_em desc, _lote_id desc
        ) as rn
    from {{ ref('stg_glosa') }}
)

select
    d.operadora_id,
    base.registro_ans,
    d.nome,
    d.nome_fantasia,
    d.modalidade,
    d.uf_sede,
    base.competencia,
    base.tipo_glosa,
    base.qt_glosa,
    base.valor_glosa,
    base.valor_faturado,
    base.taxa_glosa_calculada,
    case
        when coalesce(base.taxa_glosa_calculada, 0) > {{ var('taxa_glosa_limite', 0.15) }} then 'alta'
        else 'normal'
    end as severidade_glosa,
    base.fonte_publicacao,
    base._carregado_em,
    base._arquivo_origem,
    base._lote_id,
    'glosa_v1' as versao_dataset
from base
inner join {{ ref('dim_operadora_atual') }} as d
    on d.registro_ans = base.registro_ans
where base.rn = 1
