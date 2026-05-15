-- Release 0.9 Core ANS Comercial — Grants explicitos para healthintel_cliente_reader.
-- Idempotente: pode ser executado multiplas vezes sem efeito colateral.
--
-- Objetivo:
--   * Garantir que healthintel_cliente_reader veja APENAS as 12 tabelas com
--     status=disponivel no catalogo comercial (docs/catalogo_dados/consumo_ans/catalogo_consumo_ans.yml).
--   * Revogar acesso a schemas internos e tabelas parciais/bloqueadas/fora_do_escopo.
--
-- Origem:
--   * Reforco final apos 022_consumo_ans.sql (cria role) e 050_delta_ans_grants.sql.
--   * Auditoria empirica em scripts/auditoria/auditar_grants_cliente_reader.py.

-- 1. Garantir role (idempotente)
do $$
begin
    if not exists (select 1 from pg_roles where rolname = 'healthintel_cliente_reader') then
        create role healthintel_cliente_reader nologin;
    end if;
end
$$;

-- 2. Revogar TUDO antes de reconceder (clean slate em consumo_ans)
revoke all on schema consumo_ans from healthintel_cliente_reader;
revoke all on all tables in schema consumo_ans from healthintel_cliente_reader;
revoke all on all sequences in schema consumo_ans from healthintel_cliente_reader;

-- 3. Conceder USAGE no schema consumo_ans
grant usage on schema consumo_ans to healthintel_cliente_reader;

-- 4. Conceder SELECT explicito apenas nas 12 tabelas disponivel.
--    Tabelas parciais, vazia_bloqueada e fora_do_escopo NAO recebem grant.
--    Lista deve corresponder ao catalogo YAML versionado.

do $$
declare
    tabela_nome text;
    tabelas_disponivel text[] := array[
        'consumo_produto_plano',
        'consumo_historico_plano',
        'consumo_regulatorio_operadora_trimestre',
        'consumo_igr',
        'consumo_nip',
        'consumo_idss',
        'consumo_taxa_resolutividade_operadora_trimestral',
        'consumo_prudencial_operadora_trimestral',
        'consumo_financeiro_operadora_trimestre',
        'consumo_glosa_operadora_mensal',
        'consumo_tuss_procedimento_vigente',
        'consumo_regime_especial_operadora_trimestral'
    ];
begin
    foreach tabela_nome in array tabelas_disponivel
    loop
        if exists (
            select 1 from information_schema.tables
            where table_schema = 'consumo_ans'
              and table_name = tabela_nome
        ) then
            execute format(
                'grant select on consumo_ans.%I to healthintel_cliente_reader',
                tabela_nome
            );
        else
            raise notice 'Tabela consumo_ans.% nao encontrada (sera concedida quando criada via dbt).', tabela_nome;
        end if;
    end loop;
end
$$;

-- 5. Default privileges: apenas para o owner padrao (healthintel) — novas tabelas
--    em consumo_ans NAO recebem grant automatico. Cada tabela disponivel precisa
--    ser adicionada explicitamente neste arquivo + ao catalogo YAML.
--
--    Removemos default privileges do 022_consumo_ans.sql para evitar exposicao
--    de tabelas novas (parciais, bloqueadas) sem revisao.
alter default privileges for role healthintel in schema consumo_ans
    revoke select on tables from healthintel_cliente_reader;

-- 6. Schemas internos: REVOKE total e idempotente.
do $$
declare
    schema_interno text;
    schemas_bloqueados text[] := array[
        'bruto_ans',
        'stg_ans',
        'int_ans',
        'nucleo_ans',
        'api_ans',
        'plataforma',
        'mdm_ans',
        'mdm_privado',
        'quality_ans',
        'bruto_cliente',
        'stg_cliente',
        'consumo_premium_ans',
        'public'
    ];
begin
    foreach schema_interno in array schemas_bloqueados
    loop
        if exists (
            select 1 from information_schema.schemata
            where schema_name = schema_interno
        ) then
            execute format('revoke all on schema %I from healthintel_cliente_reader', schema_interno);
            execute format('revoke all on all tables in schema %I from healthintel_cliente_reader', schema_interno);
            execute format('revoke all on all sequences in schema %I from healthintel_cliente_reader', schema_interno);
            execute format('revoke all on all functions in schema %I from healthintel_cliente_reader', schema_interno);
        end if;
    end loop;
end
$$;

-- 7. Garantir que default privileges em schemas internos NAO concedem nada novo.
do $$
declare
    schema_interno text;
    schemas_bloqueados text[] := array[
        'bruto_ans', 'stg_ans', 'int_ans', 'nucleo_ans', 'api_ans',
        'plataforma', 'mdm_ans', 'mdm_privado', 'quality_ans',
        'bruto_cliente', 'stg_cliente', 'consumo_premium_ans'
    ];
begin
    foreach schema_interno in array schemas_bloqueados
    loop
        if exists (
            select 1 from information_schema.schemata
            where schema_name = schema_interno
        ) then
            execute format(
                'alter default privileges in schema %I revoke select on tables from healthintel_cliente_reader',
                schema_interno
            );
        end if;
    end loop;
end
$$;

-- 8. Auditoria final inline: contagem de tabelas acessiveis e schemas com privilegio.
--    Esta consulta nao falha o script, apenas registra via NOTICE.
do $$
declare
    n_tabelas integer;
    n_schemas integer;
begin
    select count(*) into n_tabelas
    from information_schema.role_table_grants
    where grantee = 'healthintel_cliente_reader'
      and privilege_type = 'SELECT';

    select count(distinct table_schema) into n_schemas
    from information_schema.role_table_grants
    where grantee = 'healthintel_cliente_reader'
      and privilege_type = 'SELECT';

    raise notice '[release 0.9] healthintel_cliente_reader: % tabelas SELECT em % schema(s).',
        n_tabelas, n_schemas;
end
$$;
