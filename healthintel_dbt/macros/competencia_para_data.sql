{% macro competencia_para_data(campo) -%}
    to_date({{ campo }}, 'YYYYMM')
{%- endmacro %}
