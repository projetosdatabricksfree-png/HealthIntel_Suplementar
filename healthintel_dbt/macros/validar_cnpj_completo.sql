{% macro validar_cnpj_completo(campo) -%}
    {%- set doc = normalizar_cnpj(campo) -%}
    case
        when {{ doc }} is null then 'NULO'
        when {{ doc }} in (
            '00000000000000', '11111111111111', '22222222222222', '33333333333333',
            '44444444444444', '55555555555555', '66666666666666', '77777777777777',
            '88888888888888', '99999999999999'
        ) then 'SEQUENCIA_INVALIDA'
        when length({{ doc }}) <> 14 then 'INVALIDO_FORMATO'
        when not ({{ validar_cnpj_digito(campo) }}) then 'INVALIDO_DIGITO'
        else 'VALIDO'
    end
{%- endmacro %}