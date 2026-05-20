-- Sprint 44.1 — Auth real + multi-tenant
-- Aplicar uma vez em produção: psql -f 071_sprint44_auth_multitenant.sql

create extension if not exists citext;

-- Identidade do usuário (pessoa física)
create table if not exists plataforma.usuario (
    id uuid primary key default gen_random_uuid(),
    email citext not null unique,
    email_verificado_em timestamptz,
    senha_hash text,
    senha_atualizada_em timestamptz,
    nome text not null,
    avatar_url text,
    google_sub text unique,
    status text not null default 'pendente_email',
    ultimo_login_em timestamptz,
    falhas_login smallint not null default 0,
    bloqueado_ate timestamptz,
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now()
);

create index if not exists ix_usuario_email on plataforma.usuario (email);
create index if not exists ix_usuario_google_sub on plataforma.usuario (google_sub) where google_sub is not null;

-- Vínculo N:M usuário ↔ cliente com role
create table if not exists plataforma.cliente_usuario (
    id uuid primary key default gen_random_uuid(),
    cliente_id uuid not null references plataforma.cliente(id) on delete cascade,
    usuario_id uuid not null references plataforma.usuario(id) on delete cascade,
    role text not null check (role in ('owner','admin','developer','billing','viewer')),
    status text not null default 'ativo',
    convidado_por_id uuid references plataforma.usuario(id),
    aceito_em timestamptz,
    criado_em timestamptz not null default now(),
    unique (cliente_id, usuario_id)
);

create index if not exists ix_cliente_usuario_usuario on plataforma.cliente_usuario (usuario_id, status);
create index if not exists ix_cliente_usuario_cliente on plataforma.cliente_usuario (cliente_id, status);

-- Tokens de uso único (verificar_email, reset_senha, convite_equipe)
create table if not exists plataforma.token_verificacao (
    id uuid primary key default gen_random_uuid(),
    usuario_id uuid not null references plataforma.usuario(id) on delete cascade,
    tipo text not null check (tipo in ('verificar_email','reset_senha','convite_equipe')),
    hash_token char(64) not null unique,
    expira_em timestamptz not null,
    consumido_em timestamptz,
    ip_origem inet,
    criado_em timestamptz not null default now()
);

create index if not exists ix_token_verificacao_usuario on plataforma.token_verificacao (usuario_id, tipo, consumido_em);

-- Sessões server-side (refresh tokens; access token é JWT curto em memória/localStorage)
create table if not exists plataforma.sessao (
    id uuid primary key default gen_random_uuid(),
    usuario_id uuid not null references plataforma.usuario(id) on delete cascade,
    cliente_id_ativo uuid references plataforma.cliente(id),
    hash_refresh_token char(64) not null unique,
    user_agent text,
    ip inet,
    criada_em timestamptz not null default now(),
    expira_em timestamptz not null,
    revogada_em timestamptz,
    ultima_atividade_em timestamptz not null default now()
);

create index if not exists ix_sessao_usuario_ativa on plataforma.sessao (usuario_id, revogada_em);
create index if not exists ix_sessao_refresh on plataforma.sessao (hash_refresh_token);

-- Audit log de auth / API key / equipe (separado de auditoria_cobranca)
create table if not exists plataforma.audit_log (
    id bigserial primary key,
    usuario_id uuid references plataforma.usuario(id),
    cliente_id uuid references plataforma.cliente(id),
    acao text not null,
    entidade text,
    entidade_id text,
    ip inet,
    user_agent text,
    payload jsonb,
    criado_em timestamptz not null default now()
);

create index if not exists ix_audit_log_usuario on plataforma.audit_log (usuario_id, criado_em desc);
create index if not exists ix_audit_log_cliente on plataforma.audit_log (cliente_id, criado_em desc);

-- Backfill: clientes existentes → usuario (owner) para preservar acesso
insert into plataforma.usuario (id, email, nome, status, email_verificado_em)
select
    gen_random_uuid(),
    c.email,
    c.nome,
    'ativo',
    now()
from plataforma.cliente c
where not exists (
    select 1 from plataforma.usuario u where u.email = c.email
);

insert into plataforma.cliente_usuario (cliente_id, usuario_id, role, aceito_em)
select c.id, u.id, 'owner', now()
from plataforma.cliente c
join plataforma.usuario u on u.email = c.email
on conflict (cliente_id, usuario_id) do nothing;
