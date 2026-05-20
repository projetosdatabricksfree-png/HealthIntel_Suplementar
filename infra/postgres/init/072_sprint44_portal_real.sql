-- Sprint 44.2 — Portal Real: extend chave_api + assinatura table
-- Aditivo: não altera colunas ou tabelas existentes.

-- -----------------------------------------------------------------------
-- Estender plataforma.plano com limite de API keys por plano
-- -----------------------------------------------------------------------
alter table plataforma.plano
    add column if not exists limite_api_keys integer not null default 3;

-- Atualizar limites por plano: free=1, starter=3, pro=10, max=25, enterprise=-1 (ilimitado)
update plataforma.plano set limite_api_keys = 1 where nome = 'free';
update plataforma.plano set limite_api_keys = 3 where nome = 'starter';
update plataforma.plano set limite_api_keys = 10 where nome = 'pro';
update plataforma.plano set limite_api_keys = 25 where nome = 'max';
update plataforma.plano set limite_api_keys = -1 where nome = 'enterprise';

-- -----------------------------------------------------------------------
-- Estender plataforma.chave_api com campos de gestão do portal
-- -----------------------------------------------------------------------
alter table plataforma.chave_api
    add column if not exists nome text,
    add column if not exists ambiente text not null default 'producao'
        check (ambiente in ('sandbox', 'producao')),
    add column if not exists escopos text[] not null default array[]::text[],
    add column if not exists criada_por_usuario_id uuid references plataforma.usuario(id),
    add column if not exists revogada_em timestamptz,
    add column if not exists revogada_por_usuario_id uuid references plataforma.usuario(id),
    add column if not exists expira_em timestamptz;

-- -----------------------------------------------------------------------
-- Assinatura: cache local do Stripe (Stripe é fonte da verdade)
-- -----------------------------------------------------------------------
create table if not exists plataforma.assinatura (
    id uuid primary key default gen_random_uuid(),
    cliente_id uuid not null references plataforma.cliente(id),
    plano_id uuid not null references plataforma.plano(id),
    stripe_customer_id text unique,
    stripe_subscription_id text unique,
    status text not null,                      -- active|past_due|canceled|incomplete|trialing
    cancel_at_period_end boolean not null default false,
    current_period_start timestamptz,
    current_period_end timestamptz,
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now()
);

create index if not exists ix_assinatura_cliente
    on plataforma.assinatura (cliente_id, status);
