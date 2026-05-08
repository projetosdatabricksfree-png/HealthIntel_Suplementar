copy (
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
    schema_grants as (
        select
            n.nspname as object_schema,
            n.nspname as object_name,
            'schema'::text as object_type,
            case when acl.grantee = 0 then 'PUBLIC' else pg_get_userbyid(acl.grantee) end as grantee,
            case when acl.grantor = 0 then 'PUBLIC' else pg_get_userbyid(acl.grantor) end as grantor,
            acl.privilege_type::text as privilege_type,
            acl.is_grantable
        from pg_catalog.pg_namespace as n
        inner join scoped_schemas as s
            on s.schema_name = n.nspname
        cross join lateral pg_catalog.aclexplode(coalesce(n.nspacl, pg_catalog.acldefault('n', n.nspowner))) as acl
    ),
    relation_grants as (
        select
            n.nspname as object_schema,
            c.relname as object_name,
            case c.relkind
                when 'S' then 'sequence'
                when 'v' then 'view'
                when 'm' then 'materialized_view'
                when 'p' then 'partitioned_table'
                when 'f' then 'foreign_table'
                else 'table'
            end as object_type,
            case when acl.grantee = 0 then 'PUBLIC' else pg_get_userbyid(acl.grantee) end as grantee,
            case when acl.grantor = 0 then 'PUBLIC' else pg_get_userbyid(acl.grantor) end as grantor,
            acl.privilege_type::text as privilege_type,
            acl.is_grantable
        from pg_catalog.pg_class as c
        inner join pg_catalog.pg_namespace as n
            on n.oid = c.relnamespace
        inner join scoped_schemas as s
            on s.schema_name = n.nspname
        cross join lateral pg_catalog.aclexplode(
            coalesce(
                c.relacl,
                case
                    when c.relkind = 'S' then pg_catalog.acldefault('s', c.relowner)
                    else pg_catalog.acldefault('r', c.relowner)
                end
            )
        ) as acl
        where c.relkind in ('r', 'p', 'v', 'm', 'S', 'f')
    ),
    function_grants as (
        select
            n.nspname as object_schema,
            p.proname || '(' || pg_catalog.pg_get_function_identity_arguments(p.oid) || ')' as object_name,
            'function'::text as object_type,
            case when acl.grantee = 0 then 'PUBLIC' else pg_get_userbyid(acl.grantee) end as grantee,
            case when acl.grantor = 0 then 'PUBLIC' else pg_get_userbyid(acl.grantor) end as grantor,
            acl.privilege_type::text as privilege_type,
            acl.is_grantable
        from pg_catalog.pg_proc as p
        inner join pg_catalog.pg_namespace as n
            on n.oid = p.pronamespace
        inner join scoped_schemas as s
            on s.schema_name = n.nspname
        cross join lateral pg_catalog.aclexplode(coalesce(p.proacl, pg_catalog.acldefault('f', p.proowner))) as acl
    ),
    default_grants as (
        select
            n.nspname as object_schema,
            case d.defaclobjtype
                when 'r' then 'tables'
                when 'S' then 'sequences'
                when 'f' then 'functions'
                when 'T' then 'types'
                when 'n' then 'schemas'
                else d.defaclobjtype::text
            end as object_name,
            'default_privileges'::text as object_type,
            case when acl.grantee = 0 then 'PUBLIC' else pg_get_userbyid(acl.grantee) end as grantee,
            case when acl.grantor = 0 then 'PUBLIC' else pg_get_userbyid(acl.grantor) end as grantor,
            acl.privilege_type::text as privilege_type,
            acl.is_grantable
        from pg_catalog.pg_default_acl as d
        inner join pg_catalog.pg_namespace as n
            on n.oid = d.defaclnamespace
        inner join scoped_schemas as s
            on s.schema_name = n.nspname
        cross join lateral pg_catalog.aclexplode(d.defaclacl) as acl
    )
    select *
    from schema_grants
    union all
    select *
    from relation_grants
    union all
    select *
    from function_grants
    union all
    select *
    from default_grants
    order by
        object_schema,
        object_type,
        object_name,
        grantee,
        privilege_type
) to stdout with (format csv, header true);
