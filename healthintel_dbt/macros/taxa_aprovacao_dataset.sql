{% macro taxa_aprovacao_dataset(dataset_nome, relacao_origem) -%}
(
    select round(
        case
            when coalesce(src.total_registros, 0) = 0 then 1
            else greatest(
                0,
                1 - (coalesce(qtd_quarentena.total_quarentena, 0)::numeric / src.total_registros)
            )
        end,
        4
    )
    from (
        select count(*)::numeric as total_registros
        from {{ relacao_origem }}
    ) as src
    cross join (
        select count(*)::numeric as total_quarentena
        from plataforma.arquivo_quarentena
        where dataset = '{{ dataset_nome }}'
    ) as qtd_quarentena
)
{%- endmacro %}
