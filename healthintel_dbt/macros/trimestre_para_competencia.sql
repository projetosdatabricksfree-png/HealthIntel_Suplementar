{% macro trimestre_para_competencia(campo) -%}
    case
        when regexp_replace(coalesce({{ campo }}::text, ''), '[^0-9]', '', 'g') ~ '^[0-9]{6}$'
            and substr(regexp_replace(coalesce({{ campo }}::text, ''), '[^0-9]', '', 'g'), 5, 2)::integer between 1 and 12
            then regexp_replace(coalesce({{ campo }}::text, ''), '[^0-9]', '', 'g')
        when regexp_replace(coalesce({{ campo }}::text, ''), '[^0-9]', '', 'g') ~ '^[0-9]{5}$'
            then case right(regexp_replace(coalesce({{ campo }}::text, ''), '[^0-9]', '', 'g'), 1)
                when '1' then substr(regexp_replace(coalesce({{ campo }}::text, ''), '[^0-9]', '', 'g'), 1, 4) || '03'
                when '2' then substr(regexp_replace(coalesce({{ campo }}::text, ''), '[^0-9]', '', 'g'), 1, 4) || '06'
                when '3' then substr(regexp_replace(coalesce({{ campo }}::text, ''), '[^0-9]', '', 'g'), 1, 4) || '09'
                when '4' then substr(regexp_replace(coalesce({{ campo }}::text, ''), '[^0-9]', '', 'g'), 1, 4) || '12'
                else null
            end
        else null
    end
{%- endmacro %}
