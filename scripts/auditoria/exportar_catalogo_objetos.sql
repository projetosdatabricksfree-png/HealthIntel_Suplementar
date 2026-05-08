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
    ),
    relation_objects as (
        select
            n.nspname as object_schema,
            c.relname as object_name,
            case c.relkind
                when 'r' then 'table'
                when 'p' then 'partitioned_table'
                when 'v' then 'view'
                when 'm' then 'materialized_view'
                when 'S' then 'sequence'
                when 'f' then 'foreign_table'
                else c.relkind::text
            end as object_type,
            pg_get_userbyid(c.relowner) as object_owner,
            c.oid::regclass::text as object_identity,
            null::text as parent_schema,
            null::text as parent_name,
            null::text as object_definition
        from pg_catalog.pg_class as c
        inner join pg_catalog.pg_namespace as n
            on n.oid = c.relnamespace
        inner join scoped_schemas as s
            on s.schema_name = n.nspname
        where c.relkind in ('r', 'p', 'v', 'm', 'S', 'f')
    ),
    function_objects as (
        select
            n.nspname as object_schema,
            p.proname as object_name,
            'function'::text as object_type,
            pg_get_userbyid(p.proowner) as object_owner,
            n.nspname || '.' || p.proname || '(' || pg_catalog.pg_get_function_identity_arguments(p.oid) || ')' as object_identity,
            null::text as parent_schema,
            null::text as parent_name,
            pg_catalog.pg_get_functiondef(p.oid) as object_definition
        from pg_catalog.pg_proc as p
        inner join pg_catalog.pg_namespace as n
            on n.oid = p.pronamespace
        inner join scoped_schemas as s
            on s.schema_name = n.nspname
    ),
    trigger_objects as (
        select
            tn.nspname as object_schema,
            t.tgname as object_name,
            'trigger'::text as object_type,
            pg_get_userbyid(tbl.relowner) as object_owner,
            tn.nspname || '.' || tbl.relname || '.' || t.tgname as object_identity,
            tn.nspname as parent_schema,
            tbl.relname as parent_name,
            pg_catalog.pg_get_triggerdef(t.oid, true) as object_definition
        from pg_catalog.pg_trigger as t
        inner join pg_catalog.pg_class as tbl
            on tbl.oid = t.tgrelid
        inner join pg_catalog.pg_namespace as tn
            on tn.oid = tbl.relnamespace
        inner join scoped_schemas as s
            on s.schema_name = tn.nspname
        where not t.tgisinternal
    )
    select *
    from relation_objects
    union all
    select *
    from function_objects
    union all
    select *
    from trigger_objects
    order by
        object_schema,
        object_type,
        object_name,
        object_identity
) to :'output_file' with (format csv, header true)
