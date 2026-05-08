\copy (
    with scoped_schemas(schema_name) as (
        values
            ('bruto_ans'),
            ('stg_ans'),
            ('int_ans'),
            ('nucleo_ans'),
            ('api_ans'),
            ('consumo_ans'),
            ('consumo_premium_ans'),
            ('ref_ans'),
            ('plataforma')
    )
    select
        coalesce(rn.nspname, cn.nspname) as object_schema,
        rel.relname as table_name,
        c.conname as constraint_name,
        case c.contype
            when 'c' then 'check'
            when 'f' then 'foreign_key'
            when 'p' then 'primary_key'
            when 'u' then 'unique'
            when 't' then 'constraint_trigger'
            when 'x' then 'exclusion'
            else c.contype::text
        end as constraint_type,
        (
            select string_agg(a.attname, ',' order by cols.ordinality)
            from unnest(c.conkey) with ordinality as cols(attnum, ordinality)
            inner join pg_catalog.pg_attribute as a
                on a.attrelid = c.conrelid
                and a.attnum = cols.attnum
        ) as columns,
        frn.nspname as referenced_schema,
        frel.relname as referenced_table,
        (
            select string_agg(a.attname, ',' order by cols.ordinality)
            from unnest(c.confkey) with ordinality as cols(attnum, ordinality)
            inner join pg_catalog.pg_attribute as a
                on a.attrelid = c.confrelid
                and a.attnum = cols.attnum
        ) as referenced_columns,
        pg_catalog.pg_get_constraintdef(c.oid, true) as constraint_definition
    from pg_catalog.pg_constraint as c
    inner join pg_catalog.pg_namespace as cn
        on cn.oid = c.connamespace
    left join pg_catalog.pg_class as rel
        on rel.oid = c.conrelid
    left join pg_catalog.pg_namespace as rn
        on rn.oid = rel.relnamespace
    left join pg_catalog.pg_class as frel
        on frel.oid = c.confrelid
    left join pg_catalog.pg_namespace as frn
        on frn.oid = frel.relnamespace
    inner join scoped_schemas as s
        on s.schema_name = coalesce(rn.nspname, cn.nspname)
    order by
        object_schema,
        table_name,
        constraint_name
) to :'output_file' with (format csv, header true)
