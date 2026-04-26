{% macro normalizar_cpf(campo) -%}
    nullif(regexp_replace(coalesce(cast({{ campo }} as text), ''), '[^0-9]', '', 'g'), '')
{%- endmacro %}

