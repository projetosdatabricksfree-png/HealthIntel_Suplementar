{% macro validar_registro_ans_formato(campo) -%}
    {%- set digito = "regexp_replace(coalesce(cast(" ~ campo ~ " as text), ''), '[^0-9]', '', 'g')" -%}
    (
        nullif({{ digito }}, '') is not null
        and length(lpad({{ digito }}, 6, '0')) = 6
        and lpad({{ digito }}, 6, '0') ~ '^[0-9]{6}$'
    )
{%- endmacro %}

