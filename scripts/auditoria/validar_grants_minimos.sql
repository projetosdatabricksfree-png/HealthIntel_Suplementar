drop table if exists auditoria_validacao_grants;

create temp table auditoria_validacao_grants as
with relevant_roles(role_name, role_purpose) as (
        values
            ('healthintel_cliente_reader', 'leitura legado consumo_ans'),
            ('healthintel_premium_reader', 'leitura premium consumo_premium_ans')
    ),
    existing_roles as (
        select
            rr.role_name,
            rr.role_purpose,
            r.oid is not null as role_exists
        from relevant_roles as rr
        left join pg_catalog.pg_roles as r
            on r.rolname = rr.role_name
    ),
    role_missing as (
        select
            'INFO'::text as severity,
            'role_not_present'::text as check_type,
            er.role_name,
            null::text as object_schema,
            null::text as object_name,
            null::text as privilege_type,
            'role documentada no projeto, mas ausente no banco auditado; auditoria nao cria roles'::text as message
        from existing_roles as er
        where not er.role_exists
    ),
    required_schema_usage as (
        select
            case when pg_catalog.has_schema_privilege(er.role_name, req.schema_name, 'USAGE') then 'PASS' else 'FAIL' end as severity,
            'required_schema_usage'::text as check_type,
            er.role_name,
            req.schema_name as object_schema,
            req.schema_name as object_name,
            'USAGE'::text as privilege_type,
            case
                when pg_catalog.has_schema_privilege(er.role_name, req.schema_name, 'USAGE') then 'role possui USAGE no schema obrigatorio'
                else 'role sem USAGE no schema obrigatorio'
            end as message
        from (
            values
                ('healthintel_cliente_reader', 'consumo_ans'),
                ('healthintel_premium_reader', 'consumo_premium_ans')
        ) as req(role_name, schema_name)
        inner join existing_roles as er
            on er.role_name = req.role_name
            and er.role_exists
        inner join pg_catalog.pg_namespace as n
            on n.nspname = req.schema_name
    ),
    required_table_select_missing as (
        select
            er.role_name,
            req.schema_name,
            string_agg(c.relname, ', ' order by c.relname) as missing_objects,
            count(*) as missing_count
        from (
            values
                ('healthintel_cliente_reader', 'consumo_ans'),
                ('healthintel_premium_reader', 'consumo_premium_ans')
        ) as req(role_name, schema_name)
        inner join existing_roles as er
            on er.role_name = req.role_name
            and er.role_exists
        inner join pg_catalog.pg_namespace as n
            on n.nspname = req.schema_name
        inner join pg_catalog.pg_class as c
            on c.relnamespace = n.oid
            and c.relkind in ('r', 'p', 'v', 'm', 'f')
        where not pg_catalog.has_table_privilege(er.role_name, c.oid, 'SELECT')
        group by
            er.role_name,
            req.schema_name
    ),
    required_table_select as (
        select
            case when m.missing_count is null then 'PASS' else 'FAIL' end as severity,
            'required_table_select'::text as check_type,
            er.role_name,
            req.schema_name as object_schema,
            '*'::text as object_name,
            'SELECT'::text as privilege_type,
            case
                when m.missing_count is null then 'role possui SELECT em todos os objetos atuais do schema'
                else 'role sem SELECT em objetos do schema: ' || m.missing_objects
            end as message
        from (
            values
                ('healthintel_cliente_reader', 'consumo_ans'),
                ('healthintel_premium_reader', 'consumo_premium_ans')
        ) as req(role_name, schema_name)
        inner join existing_roles as er
            on er.role_name = req.role_name
            and er.role_exists
        inner join pg_catalog.pg_namespace as n
            on n.nspname = req.schema_name
        left join required_table_select_missing as m
            on m.role_name = req.role_name
            and m.schema_name = req.schema_name
    ),
    observational_schema_usage as (
        select
            case when pg_catalog.has_schema_privilege(er.role_name, obs.schema_name, 'USAGE') then 'INFO' else 'WARN' end as severity,
            'observed_schema_usage'::text as check_type,
            er.role_name,
            obs.schema_name as object_schema,
            obs.schema_name as object_name,
            'USAGE'::text as privilege_type,
            case
                when pg_catalog.has_schema_privilege(er.role_name, obs.schema_name, 'USAGE') then 'role possui USAGE observado no schema'
                else 'role existente sem USAGE observado no schema; validar se e esperado'
            end as message
        from (
            values
                ('ref_ans'),
                ('api_ans')
        ) as obs(schema_name)
        cross join existing_roles as er
        inner join pg_catalog.pg_namespace as n
            on n.nspname = obs.schema_name
        where er.role_exists
    )
select *
from role_missing
union all
select *
from required_schema_usage
union all
select *
from required_table_select
union all
select *
from observational_schema_usage;

\o :output_file
copy (
    select *
    from auditoria_validacao_grants
    order by
        severity,
        check_type,
        role_name,
        object_schema,
        object_name
) to stdout with (format csv, header true);
\o
