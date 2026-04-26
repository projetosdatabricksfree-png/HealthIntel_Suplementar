{% macro validar_cnpj_digito(campo) -%}
    {%- set doc = normalizar_cnpj(campo) -%}
    (
        case
            when {{ doc }} is null then false
            when length({{ doc }}) <> 14 then false
            when {{ doc }} in (
                '00000000000000', '11111111111111', '22222222222222', '33333333333333',
                '44444444444444', '55555555555555', '66666666666666', '77777777777777',
                '88888888888888', '99999999999999'
            ) then false
            else (
                (
                    case
                        when 11 - mod(
                            cast(substring({{ doc }} from 1 for 1) as integer) * 5
                            + cast(substring({{ doc }} from 2 for 1) as integer) * 4
                            + cast(substring({{ doc }} from 3 for 1) as integer) * 3
                            + cast(substring({{ doc }} from 4 for 1) as integer) * 2
                            + cast(substring({{ doc }} from 5 for 1) as integer) * 9
                            + cast(substring({{ doc }} from 6 for 1) as integer) * 8
                            + cast(substring({{ doc }} from 7 for 1) as integer) * 7
                            + cast(substring({{ doc }} from 8 for 1) as integer) * 6
                            + cast(substring({{ doc }} from 9 for 1) as integer) * 5
                            + cast(substring({{ doc }} from 10 for 1) as integer) * 4
                            + cast(substring({{ doc }} from 11 for 1) as integer) * 3
                            + cast(substring({{ doc }} from 12 for 1) as integer) * 2,
                            11
                        ) >= 10 then 0
                        else 11 - mod(
                            cast(substring({{ doc }} from 1 for 1) as integer) * 5
                            + cast(substring({{ doc }} from 2 for 1) as integer) * 4
                            + cast(substring({{ doc }} from 3 for 1) as integer) * 3
                            + cast(substring({{ doc }} from 4 for 1) as integer) * 2
                            + cast(substring({{ doc }} from 5 for 1) as integer) * 9
                            + cast(substring({{ doc }} from 6 for 1) as integer) * 8
                            + cast(substring({{ doc }} from 7 for 1) as integer) * 7
                            + cast(substring({{ doc }} from 8 for 1) as integer) * 6
                            + cast(substring({{ doc }} from 9 for 1) as integer) * 5
                            + cast(substring({{ doc }} from 10 for 1) as integer) * 4
                            + cast(substring({{ doc }} from 11 for 1) as integer) * 3
                            + cast(substring({{ doc }} from 12 for 1) as integer) * 2,
                            11
                        )
                    end
                ) = cast(substring({{ doc }} from 13 for 1) as integer)
                and (
                    case
                        when 11 - mod(
                            cast(substring({{ doc }} from 1 for 1) as integer) * 6
                            + cast(substring({{ doc }} from 2 for 1) as integer) * 5
                            + cast(substring({{ doc }} from 3 for 1) as integer) * 4
                            + cast(substring({{ doc }} from 4 for 1) as integer) * 3
                            + cast(substring({{ doc }} from 5 for 1) as integer) * 2
                            + cast(substring({{ doc }} from 6 for 1) as integer) * 9
                            + cast(substring({{ doc }} from 7 for 1) as integer) * 8
                            + cast(substring({{ doc }} from 8 for 1) as integer) * 7
                            + cast(substring({{ doc }} from 9 for 1) as integer) * 6
                            + cast(substring({{ doc }} from 10 for 1) as integer) * 5
                            + cast(substring({{ doc }} from 11 for 1) as integer) * 4
                            + cast(substring({{ doc }} from 12 for 1) as integer) * 3
                            + cast(substring({{ doc }} from 13 for 1) as integer) * 2,
                            11
                        ) >= 10 then 0
                        else 11 - mod(
                            cast(substring({{ doc }} from 1 for 1) as integer) * 6
                            + cast(substring({{ doc }} from 2 for 1) as integer) * 5
                            + cast(substring({{ doc }} from 3 for 1) as integer) * 4
                            + cast(substring({{ doc }} from 4 for 1) as integer) * 3
                            + cast(substring({{ doc }} from 5 for 1) as integer) * 2
                            + cast(substring({{ doc }} from 6 for 1) as integer) * 9
                            + cast(substring({{ doc }} from 7 for 1) as integer) * 8
                            + cast(substring({{ doc }} from 8 for 1) as integer) * 7
                            + cast(substring({{ doc }} from 9 for 1) as integer) * 6
                            + cast(substring({{ doc }} from 10 for 1) as integer) * 5
                            + cast(substring({{ doc }} from 11 for 1) as integer) * 4
                            + cast(substring({{ doc }} from 12 for 1) as integer) * 3
                            + cast(substring({{ doc }} from 13 for 1) as integer) * 2,
                            11
                        )
                    end
                ) = cast(substring({{ doc }} from 14 for 1) as integer)
            )
        end
    )
{%- endmacro %}

