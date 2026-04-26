{% macro normalizar_cnes(campo) -%}
    {%- set digito = "regexp_replace(coalesce(cast(" ~ campo ~ " as text), ''), '[^0-9]', '', 'g')" -%}
    case
        when nullif({{ digito }}, '') is null then null
        else lpad({{ digito }}, 7, '0')
    end
{%- endmacro %}

