set search_path to plataforma, public;

do $$
declare
    v_cliente_id_tipo text;
begin
    select format_type(a.atttypid, a.atttypmod)
      into v_cliente_id_tipo
    from pg_attribute a
    where a.attrelid = 'plataforma.cliente'::regclass
      and a.attname = 'id'
      and a.attnum > 0
      and not a.attisdropped;

    if v_cliente_id_tipo is null then
        raise exception 'Tabela plataforma.cliente(id) nao encontrada. Sprint 38 requer cliente real.';
    end if;

    if v_cliente_id_tipo <> 'uuid' then
        raise exception 'plataforma.cliente(id) esperado como uuid, encontrado %', v_cliente_id_tipo;
    end if;
end $$;

create table if not exists plataforma.cliente_dataset_acesso (
    id bigserial primary key,
    cliente_id uuid not null references plataforma.cliente(id),
    dataset_codigo text not null references plataforma.politica_dataset(dataset_codigo),
    plano text not null,
    acesso_historico boolean not null default false,
    competencia_inicio integer,
    competencia_fim integer,
    anos_historico integer,
    limite_requisicao_mensal bigint,
    permite_exportacao boolean not null default false,
    ativo boolean not null default true,
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now(),
    constraint ck_cliente_dataset_acesso_competencia
        check (
            acesso_historico = false
            or (
                competencia_inicio is not null
                and competencia_fim is not null
                and competencia_inicio <= competencia_fim
                and competencia_inicio % 100 between 1 and 12
                and competencia_fim % 100 between 1 and 12
            )
        )
);

create index if not exists ix_cliente_dataset_acesso_lookup
    on plataforma.cliente_dataset_acesso (cliente_id, dataset_codigo)
    where ativo = true;

create unique index if not exists ux_cliente_dataset_acesso_ativo
    on plataforma.cliente_dataset_acesso (cliente_id, dataset_codigo)
    where ativo = true;

create table if not exists plataforma.solicitacao_historico (
    id bigserial primary key,
    cliente_id uuid not null references plataforma.cliente(id),
    dataset_codigo text not null references plataforma.politica_dataset(dataset_codigo),
    competencia_inicio integer not null,
    competencia_fim integer not null,
    status text not null default 'pendente'
        check (status in (
            'pendente',
            'aprovada',
            'em_execucao',
            'concluida',
            'rejeitada',
            'cancelada',
            'erro'
        )),
    motivo text,
    solicitado_em timestamptz not null default now(),
    aprovado_em timestamptz,
    iniciado_em timestamptz,
    finalizado_em timestamptz,
    erro text,
    criado_por text not null default current_user,
    constraint ck_solicitacao_historico_competencia
        check (
            competencia_inicio <= competencia_fim
            and competencia_inicio % 100 between 1 and 12
            and competencia_fim % 100 between 1 and 12
        )
);

create index if not exists ix_solicitacao_historico_status
    on plataforma.solicitacao_historico (status, solicitado_em);

create index if not exists ix_solicitacao_historico_cliente_dataset
    on plataforma.solicitacao_historico (cliente_id, dataset_codigo, solicitado_em desc);

create or replace function plataforma.atualizar_coluna_atualizado_em()
returns trigger
language plpgsql
as $$
begin
    new.atualizado_em = now();
    return new;
end;
$$;

drop trigger if exists trg_cliente_dataset_acesso_atualizado_em
    on plataforma.cliente_dataset_acesso;

create trigger trg_cliente_dataset_acesso_atualizado_em
before update on plataforma.cliente_dataset_acesso
for each row execute function plataforma.atualizar_coluna_atualizado_em();

comment on table plataforma.cliente_dataset_acesso is
'Controla entitlement de historico sob demanda por cliente/dataset/faixa. Nao duplica bases por cliente.';

comment on column plataforma.cliente_dataset_acesso.acesso_historico is
'Quando true, permite acesso historico apenas dentro da faixa competencia_inicio..competencia_fim.';

comment on column plataforma.cliente_dataset_acesso.permite_exportacao is
'Exportacao completa historica permanece bloqueada no MVP; campo reservado para pos-MVP controlado.';

comment on table plataforma.solicitacao_historico is
'Workflow auditavel de pedidos de historico sob demanda. No MVP a aprovacao e operacional via SQL/runbook; endpoint admin completo e pos-MVP.';

comment on column plataforma.solicitacao_historico.status is
'Estados: pendente, aprovada, em_execucao, concluida, rejeitada, cancelada, erro.';
