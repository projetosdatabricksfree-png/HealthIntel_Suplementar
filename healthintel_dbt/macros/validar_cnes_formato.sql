{% macro validar_cnes_formato(campo) -%}
    (
        {{ normalizar_cnes(campo) }} is not null
        and {{ normalizar_cnes(campo) }} ~ '^[0-9]{7}$'
    )
{%- endmacro %}

