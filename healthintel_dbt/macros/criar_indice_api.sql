{% macro criar_indice_api(relacao, coluna) -%}
    {{ criar_indices(relacao, coluna) }}
{%- endmacro %}
