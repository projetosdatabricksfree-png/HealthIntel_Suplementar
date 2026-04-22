alter table if exists plataforma.plano
    add column if not exists descricao text,
    add column if not exists preco_base_centavos integer not null default 0,
    add column if not exists franquia_requisicoes_mes integer not null default 0,
    add column if not exists preco_excedente_mil_requisicoes_centavos integer not null default 0,
    add column if not exists ordem_upgrade smallint not null default 1,
    add column if not exists permite_upgrade_automatico boolean not null default true;

alter table if exists plataforma.cliente
    add column if not exists status_cobranca text not null default 'em_dia',
    add column if not exists dia_fechamento smallint not null default 1;

create table if not exists plataforma.ciclo_faturamento (
    id uuid primary key,
    cliente_id uuid not null references plataforma.cliente(id),
    referencia char(7) not null,
    inicio_periodo date not null,
    fim_periodo date not null,
    status text not null,
    valor_estimado_centavos bigint not null default 0,
    registros_faturaveis bigint not null default 0,
    fechado_em timestamptz,
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now(),
    unique (cliente_id, referencia)
);

create index if not exists ix_ciclo_faturamento_referencia
    on plataforma.ciclo_faturamento (referencia, status);

create table if not exists plataforma.fatura_consumo (
    id uuid primary key,
    ciclo_id uuid not null references plataforma.ciclo_faturamento(id),
    cliente_id uuid not null references plataforma.cliente(id),
    plano_id uuid not null references plataforma.plano(id),
    referencia char(7) not null,
    requisicoes_total bigint not null default 0,
    requisicoes_faturaveis bigint not null default 0,
    franquia_requisicoes_mes integer not null default 0,
    requisicoes_excedentes bigint not null default 0,
    blocos_excedentes integer not null default 0,
    endpoints_faturaveis integer not null default 0,
    latencia_media_ms integer not null default 0,
    valor_base_centavos integer not null default 0,
    valor_excedente_centavos integer not null default 0,
    valor_total_centavos bigint not null default 0,
    status text not null,
    regra_faturamento jsonb not null default '{}'::jsonb,
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now(),
    unique (cliente_id, referencia)
);

create index if not exists ix_fatura_consumo_referencia
    on plataforma.fatura_consumo (referencia, status);

create table if not exists plataforma.historico_plano (
    id uuid primary key,
    cliente_id uuid not null references plataforma.cliente(id),
    plano_origem_id uuid not null references plataforma.plano(id),
    plano_destino_id uuid not null references plataforma.plano(id),
    tipo_movimentacao text not null,
    motivo text not null,
    origem text not null,
    solicitado_por text not null,
    efetivado_em timestamptz not null default now(),
    chaves_atualizadas integer not null default 0
);

create index if not exists ix_historico_plano_cliente_tempo
    on plataforma.historico_plano (cliente_id, efetivado_em desc);

create table if not exists plataforma.auditoria_cobranca (
    id uuid primary key,
    cliente_id uuid references plataforma.cliente(id),
    referencia char(7),
    evento text not null,
    ator text not null,
    origem text not null,
    payload jsonb not null default '{}'::jsonb,
    criado_em timestamptz not null default now()
);

create index if not exists ix_auditoria_cobranca_evento_tempo
    on plataforma.auditoria_cobranca (evento, criado_em desc);

insert into plataforma.plano (
    id,
    nome,
    limite_rpm,
    endpoint_permitido,
    status,
    descricao,
    preco_base_centavos,
    franquia_requisicoes_mes,
    preco_excedente_mil_requisicoes_centavos,
    ordem_upgrade,
    permite_upgrade_automatico
)
values
    (
        '11111111-1111-1111-1111-111111111111',
        'starter_local',
        120,
        array['/v1/operadoras'],
        'ativo',
        'Plano local de entrada para desenvolvimento.',
        249000,
        5000,
        3500,
        1,
        true
    ),
    (
        '11111111-1111-1111-1111-111111111112',
        'growth_local',
        300,
        array['/v1/'],
        'ativo',
        'Plano local para consumo recorrente.',
        699000,
        20000,
        3000,
        2,
        true
    ),
    (
        '11111111-1111-1111-1111-111111111113',
        'pro_local',
        1000,
        array['/v1/'],
        'ativo',
        'Plano local para consumo corporativo intenso.',
        1490000,
        100000,
        2500,
        3,
        true
    ),
    (
        '11111111-1111-1111-1111-111111111114',
        'enterprise_local',
        5000,
        array['/v1/'],
        'ativo',
        'Plano local enterprise com tratamento comercial dedicado.',
        0,
        0,
        0,
        4,
        false
    ),
    (
        '11111111-1111-1111-1111-111111111199',
        'admin_interno',
        5000,
        array['/v1/', '/admin/'],
        'ativo',
        'Plano interno para operacao e administracao da plataforma.',
        0,
        0,
        0,
        99,
        false
    )
on conflict (id) do update set
    nome = excluded.nome,
    limite_rpm = excluded.limite_rpm,
    endpoint_permitido = excluded.endpoint_permitido,
    status = excluded.status,
    descricao = excluded.descricao,
    preco_base_centavos = excluded.preco_base_centavos,
    franquia_requisicoes_mes = excluded.franquia_requisicoes_mes,
    preco_excedente_mil_requisicoes_centavos = excluded.preco_excedente_mil_requisicoes_centavos,
    ordem_upgrade = excluded.ordem_upgrade,
    permite_upgrade_automatico = excluded.permite_upgrade_automatico;

insert into plataforma.cliente (
    id,
    nome,
    email,
    status,
    plano_id,
    status_cobranca,
    dia_fechamento
)
values
    (
        '22222222-2222-2222-2222-222222222222',
        'cliente_local_healthintel',
        'dev@healthintel.local',
        'ativo',
        '11111111-1111-1111-1111-111111111111',
        'em_dia',
        1
    ),
    (
        '22222222-2222-2222-2222-222222222299',
        'ops_local_healthintel',
        'ops@healthintel.local',
        'ativo',
        '11111111-1111-1111-1111-111111111199',
        'em_dia',
        1
    )
on conflict (id) do update set
    nome = excluded.nome,
    email = excluded.email,
    status = excluded.status,
    plano_id = excluded.plano_id,
    status_cobranca = excluded.status_cobranca,
    dia_fechamento = excluded.dia_fechamento;

insert into plataforma.chave_api (
    id,
    cliente_id,
    plano_id,
    hash_chave,
    prefixo_chave,
    status
)
values
    (
        '33333333-3333-3333-3333-333333333399',
        '22222222-2222-2222-2222-222222222299',
        '11111111-1111-1111-1111-111111111199',
        'f86991b86048a91fe77eec2346379bbb3ea8eb853405b482cf4f950992cf1860',
        'hi_local_a',
        'ativo'
    )
on conflict (id) do update set
    cliente_id = excluded.cliente_id,
    plano_id = excluded.plano_id,
    hash_chave = excluded.hash_chave,
    prefixo_chave = excluded.prefixo_chave,
    status = excluded.status;
