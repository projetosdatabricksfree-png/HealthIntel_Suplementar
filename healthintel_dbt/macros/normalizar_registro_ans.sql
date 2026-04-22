{% macro normalizar_registro_ans(campo) -%}
    lpad(trim({{ campo }}), 6, '0')
{%- endmacro %}
