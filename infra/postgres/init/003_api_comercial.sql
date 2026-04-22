create table if not exists plataforma.plano (
    id uuid primary key,
    nome text not null unique,
    limite_rpm integer not null,
    endpoint_permitido text[] not null,
    status text not null,
    criado_em timestamptz not null default now()
);

create table if not exists plataforma.cliente (
    id uuid primary key,
    nome text not null,
    email text not null unique,
    status text not null,
    plano_id uuid not null references plataforma.plano(id),
    criado_em timestamptz not null default now()
);

create table if not exists plataforma.chave_api (
    id uuid primary key,
    cliente_id uuid not null references plataforma.cliente(id),
    plano_id uuid not null references plataforma.plano(id),
    hash_chave char(64) not null unique,
    prefixo_chave char(10) not null,
    status text not null,
    criado_em timestamptz not null default now(),
    ultimo_uso_em timestamptz
);

create index if not exists ix_chave_api_hash on plataforma.chave_api (hash_chave);
create index if not exists ix_chave_api_cliente on plataforma.chave_api (cliente_id, status);

create table if not exists plataforma.log_uso (
    id bigserial,
    chave_id uuid not null references plataforma.chave_api(id),
    cliente_id uuid not null references plataforma.cliente(id),
    plano_id uuid not null references plataforma.plano(id),
    endpoint text not null,
    rota text,
    metodo text not null,
    codigo_status integer not null,
    latencia_ms integer not null,
    cache_hit boolean not null default false,
    timestamp_req timestamptz not null,
    hash_ip text,
    primary key (id, timestamp_req)
) partition by range (timestamp_req);

create table if not exists plataforma.log_uso_default
    partition of plataforma.log_uso default;

create index if not exists ix_log_uso_chave_tempo
    on plataforma.log_uso (chave_id, timestamp_req desc);

create index if not exists ix_log_uso_endpoint_tempo
    on plataforma.log_uso (endpoint, timestamp_req desc);

insert into plataforma.plano (
    id,
    nome,
    limite_rpm,
    endpoint_permitido,
    status
)
values (
    '11111111-1111-1111-1111-111111111111',
    'starter_local',
    120,
    array['/v1/operadoras'],
    'ativo'
)
on conflict (id) do update set
    nome = excluded.nome,
    limite_rpm = excluded.limite_rpm,
    endpoint_permitido = excluded.endpoint_permitido,
    status = excluded.status;

insert into plataforma.cliente (
    id,
    nome,
    email,
    status,
    plano_id
)
values (
    '22222222-2222-2222-2222-222222222222',
    'cliente_local_healthintel',
    'dev@healthintel.local',
    'ativo',
    '11111111-1111-1111-1111-111111111111'
)
on conflict (id) do update set
    nome = excluded.nome,
    email = excluded.email,
    status = excluded.status,
    plano_id = excluded.plano_id;

insert into plataforma.chave_api (
    id,
    cliente_id,
    plano_id,
    hash_chave,
    prefixo_chave,
    status
)
values (
    '33333333-3333-3333-3333-333333333333',
    '22222222-2222-2222-2222-222222222222',
    '11111111-1111-1111-1111-111111111111',
    '03a8ec4513a37da92e91ef48d8de09ab2a281aad5456ad89c9b734e879f3a78c',
    'hi_local_d',
    'ativo'
)
on conflict (id) do update set
    cliente_id = excluded.cliente_id,
    plano_id = excluded.plano_id,
    hash_chave = excluded.hash_chave,
    prefixo_chave = excluded.prefixo_chave,
    status = excluded.status;
