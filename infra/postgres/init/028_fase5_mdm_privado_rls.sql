-- Sprint 30 — MDM privado de contrato e subfatura por tenant.
-- Cria schemas privados, tabelas brutas com tenant_id, RLS por tenant,
-- e revoga acesso de healthintel_cliente_reader (público) aos schemas privados.

create schema if not exists bruto_cliente;
create schema if not exists stg_cliente;
create schema if not exists mdm_privado;

-- Tabelas físicas privadas por tenant ----------------------------------------

create table if not exists bruto_cliente.contrato (
    tenant_id        text not null,
    id_carga         text not null,
    source_system    text,
    fonte_arquivo    text,
    hash_arquivo     text not null,
    competencia      int,
    registro_ans     text,
    cnpj_operadora   text,
    numero_contrato  text,
    tipo_contrato    text,
    vigencia_inicio  date,
    vigencia_fim     date,
    status_contrato  text,
    payload_bruto    jsonb,
    dt_carga         timestamp(3) not null default current_timestamp
);

create index if not exists idx_bruto_cliente_contrato_tenant
    on bruto_cliente.contrato (tenant_id);
create index if not exists idx_bruto_cliente_contrato_hash
    on bruto_cliente.contrato (tenant_id, hash_arquivo);
create index if not exists idx_bruto_cliente_contrato_competencia
    on bruto_cliente.contrato (tenant_id, competencia);
create index if not exists idx_bruto_cliente_contrato_numero
    on bruto_cliente.contrato (tenant_id, numero_contrato);

create table if not exists bruto_cliente.subfatura (
    tenant_id          text not null,
    id_carga           text not null,
    source_system      text,
    fonte_arquivo      text,
    hash_arquivo       text not null,
    competencia        int,
    numero_contrato    text,
    codigo_subfatura   text,
    centro_custo       text,
    unidade_negocio    text,
    vigencia_inicio    date,
    vigencia_fim       date,
    status_subfatura   text,
    payload_bruto      jsonb,
    dt_carga           timestamp(3) not null default current_timestamp
);

create index if not exists idx_bruto_cliente_subfatura_tenant
    on bruto_cliente.subfatura (tenant_id);
create index if not exists idx_bruto_cliente_subfatura_hash
    on bruto_cliente.subfatura (tenant_id, hash_arquivo);
create index if not exists idx_bruto_cliente_subfatura_competencia
    on bruto_cliente.subfatura (tenant_id, competencia);
create index if not exists idx_bruto_cliente_subfatura_chave
    on bruto_cliente.subfatura (tenant_id, numero_contrato, codigo_subfatura);

-- RLS por tenant_id ----------------------------------------------------------
-- A camada de aplicação ou processo de carga privado deve setar
-- `set_config('app.tenant_id', '<tenant>', false)` no início da sessão.
-- Sem isso, RLS retorna zero linhas. Nenhuma carga pode entrar sem tenant.

alter table bruto_cliente.contrato enable row level security;
alter table bruto_cliente.contrato force row level security;
alter table bruto_cliente.subfatura enable row level security;
alter table bruto_cliente.subfatura force row level security;

drop policy if exists rls_bruto_cliente_contrato on bruto_cliente.contrato;
create policy rls_bruto_cliente_contrato
    on bruto_cliente.contrato
    using (tenant_id = current_setting('app.tenant_id', true))
    with check (tenant_id = current_setting('app.tenant_id', true));

drop policy if exists rls_bruto_cliente_subfatura on bruto_cliente.subfatura;
create policy rls_bruto_cliente_subfatura
    on bruto_cliente.subfatura
    using (tenant_id = current_setting('app.tenant_id', true))
    with check (tenant_id = current_setting('app.tenant_id', true));

-- Roles privados (placeholders) ---------------------------------------------

do $$
begin
    if not exists (select 1 from pg_roles where rolname = 'healthintel_premium_reader') then
        create role healthintel_premium_reader nologin;
    end if;
    if not exists (select 1 from pg_roles where rolname = 'healthintel_mdm_privado_owner') then
        create role healthintel_mdm_privado_owner nologin;
    end if;
end
$$;

-- Revogações explícitas: cliente público nunca acessa dados privados ---------

revoke all on schema bruto_cliente from public;
revoke all on schema stg_cliente   from public;
revoke all on schema mdm_privado   from public;

revoke all on schema bruto_cliente from healthintel_cliente_reader;
revoke all on schema stg_cliente   from healthintel_cliente_reader;
revoke all on schema mdm_privado   from healthintel_cliente_reader;

revoke all on all tables in schema bruto_cliente from healthintel_cliente_reader;
revoke all on all tables in schema mdm_privado   from healthintel_cliente_reader;

alter default privileges in schema bruto_cliente
    revoke all on tables from healthintel_cliente_reader;
alter default privileges in schema stg_cliente
    revoke all on tables from healthintel_cliente_reader;
alter default privileges in schema mdm_privado
    revoke all on tables from healthintel_cliente_reader;

-- Premium reader (Sprint 31) ainda não recebe grant em mdm_privado.
-- A leitura premium futura será via api_ans.api_premium_*, não direto aqui.
revoke all on schema mdm_privado from healthintel_premium_reader;

-- MDM privado owner ganha controle dos schemas privados.
grant usage on schema bruto_cliente to healthintel_mdm_privado_owner;
grant usage on schema stg_cliente   to healthintel_mdm_privado_owner;
grant usage on schema mdm_privado   to healthintel_mdm_privado_owner;
grant select, insert, update, delete on all tables in schema bruto_cliente
    to healthintel_mdm_privado_owner;
alter default privileges in schema bruto_cliente
    grant select, insert, update, delete on tables to healthintel_mdm_privado_owner;
alter default privileges in schema stg_cliente
    grant select on tables to healthintel_mdm_privado_owner;
alter default privileges in schema mdm_privado
    grant select on tables to healthintel_mdm_privado_owner;
