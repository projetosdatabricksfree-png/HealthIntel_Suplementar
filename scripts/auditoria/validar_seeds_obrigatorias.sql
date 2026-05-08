\copy (
    with required_seeds(seed_schema, seed_name) as (
        values
            ('ref_ans', 'ref_modalidade'),
            ('ref_ans', 'ref_indicador_financeiro')
    ),
    seed_status as (
        select
            r.seed_schema,
            r.seed_name,
            to_regclass(format('%I.%I', r.seed_schema, r.seed_name)) as relation_oid
        from required_seeds as r
    )
    select
        case
            when s.relation_oid is null then 'FAIL'
            when seed_counts.row_count > 0 then 'PASS'
            else 'FAIL'
        end as severity,
        'required_seed_populated' as check_type,
        s.seed_schema,
        s.seed_name,
        (s.relation_oid is not null) as exists,
        seed_counts.row_count,
        case
            when s.relation_oid is null then 'seed obrigatoria ausente'
            when seed_counts.row_count > 0 then 'seed obrigatoria existe e possui linhas'
            else 'seed obrigatoria existe, mas esta vazia'
        end as message
    from seed_status as s
    left join lateral (
        select
            case
                when s.relation_oid is null then null::bigint
                else (
                    xpath(
                        '/row/count/text()',
                        query_to_xml(format('select count(*) as count from %I.%I', s.seed_schema, s.seed_name), false, true, '')
                    )
                )[1]::text::bigint
            end as row_count
    ) as seed_counts
        on true
    order by
        s.seed_schema,
        s.seed_name
) to :'output_file' with (format csv, header true)
