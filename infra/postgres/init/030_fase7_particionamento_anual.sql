create table if not exists plataforma.retencao_particao_log (
    id bigserial primary key,
    schema_alvo text not null,
    tabela_alvo text not null,
    nome_particao text not null,
    acao text not null check (
        acao in (
            'criada',
            'reaproveitada',
            'destacada',
            'removida',
            'default_recebeu_linha'
        )
    ),
    competencia_inicio integer,
    competencia_fim_exclusivo integer,
    motivo text,
    executado_em timestamptz not null default now(),
    executado_por text not null default current_user
);

create index if not exists ix_retencao_particao_log_lookup
    on plataforma.retencao_particao_log (schema_alvo, tabela_alvo, executado_em desc);

create or replace function plataforma.calcular_janela_carga_anual(
    p_anos_carga integer default 2,
    p_data_referencia date default current_date
)
returns table (
    ano_vigente integer,
    ano_inicial integer,
    ano_final integer,
    ano_preparado integer,
    competencia_minima integer,
    competencia_maxima_exclusiva integer
)
language plpgsql
stable
as $$
begin
    if p_anos_carga < 1 then
        raise exception 'p_anos_carga deve ser maior ou igual a 1. Valor recebido: %',
            p_anos_carga;
    end if;

    ano_vigente := extract(year from p_data_referencia)::integer;
    ano_inicial := ano_vigente - p_anos_carga + 1;
    ano_final := ano_vigente;
    ano_preparado := ano_final + 1;
    competencia_minima := (ano_inicial * 100) + 1;
    competencia_maxima_exclusiva := (ano_preparado * 100) + 1;

    return next;
end;
$$;

create or replace function plataforma.criar_particao_anual_competencia(
    p_schema text,
    p_tabela text,
    p_ano integer
)
returns void
language plpgsql
as $$
declare
    v_parent_regclass regclass;
    v_particao_regclass regclass;
    v_particao_nome text;
    v_inicio integer;
    v_fim integer;
    v_parent_relkind char;
    v_particao_anexada boolean;
begin
    if p_schema is null or btrim(p_schema) = '' then
        raise exception 'p_schema deve ser informado';
    end if;

    if p_tabela is null or btrim(p_tabela) = '' then
        raise exception 'p_tabela deve ser informada';
    end if;

    if p_ano < 1900 or p_ano > 9999 then
        raise exception 'p_ano fora do intervalo esperado: %', p_ano;
    end if;

    v_particao_nome := p_tabela || '_' || p_ano::text;
    v_parent_regclass := to_regclass(format('%I.%I', p_schema, p_tabela));
    v_particao_regclass := to_regclass(format('%I.%I', p_schema, v_particao_nome));
    v_inicio := (p_ano * 100) + 1;
    v_fim := ((p_ano + 1) * 100) + 1;

    if v_parent_regclass is null then
        raise exception 'Tabela-mae %.% nao existe', p_schema, p_tabela;
    end if;

    select c.relkind
      into v_parent_relkind
      from pg_class c
     where c.oid = v_parent_regclass;

    if v_parent_relkind <> 'p' then
        raise exception 'Tabela-mae %.% nao e uma partitioned table', p_schema, p_tabela;
    end if;

    if v_particao_regclass is not null then
        select exists (
            select 1
              from pg_inherits i
             where i.inhparent = v_parent_regclass
               and i.inhrelid = v_particao_regclass
        )
          into v_particao_anexada;

        if v_particao_anexada then
            insert into plataforma.retencao_particao_log (
                schema_alvo,
                tabela_alvo,
                nome_particao,
                acao,
                competencia_inicio,
                competencia_fim_exclusivo,
                motivo
            )
            values (
                p_schema,
                p_tabela,
                format('%I.%I', p_schema, v_particao_nome),
                'reaproveitada',
                v_inicio,
                v_fim,
                'Particao anual ja existia e estava anexada'
            );
            return;
        end if;

        raise exception 'Particao %.% ja existe mas nao esta anexada a %.%',
            p_schema, v_particao_nome, p_schema, p_tabela;
    end if;

    execute format(
        'create table %I.%I partition of %I.%I for values from (%s) to (%s)',
        p_schema,
        v_particao_nome,
        p_schema,
        p_tabela,
        v_inicio,
        v_fim
    );

    insert into plataforma.retencao_particao_log (
        schema_alvo,
        tabela_alvo,
        nome_particao,
        acao,
        competencia_inicio,
        competencia_fim_exclusivo,
        motivo
    )
    values (
        p_schema,
        p_tabela,
        format('%I.%I', p_schema, v_particao_nome),
        'criada',
        v_inicio,
        v_fim,
        'Particao anual criada'
    );
end;
$$;

create or replace function plataforma.preparar_particoes_janela_atual(
    p_schema text,
    p_tabela text,
    p_anos_carga integer default 2
)
returns void
language plpgsql
as $$
declare
    v_janela record;
    v_ano integer;
begin
    select *
      into v_janela
      from plataforma.calcular_janela_carga_anual(p_anos_carga);

    for v_ano in v_janela.ano_inicial..v_janela.ano_preparado loop
        perform plataforma.criar_particao_anual_competencia(p_schema, p_tabela, v_ano);
    end loop;
end;
$$;

create or replace function plataforma.alertar_default_particao()
returns trigger
language plpgsql
as $$
begin
    insert into plataforma.retencao_particao_log (
        schema_alvo,
        tabela_alvo,
        nome_particao,
        acao,
        competencia_inicio,
        motivo
    )
    values (
        TG_TABLE_SCHEMA,
        TG_TABLE_NAME,
        TG_TABLE_SCHEMA || '.' || TG_TABLE_NAME,
        'default_recebeu_linha',
        NEW.competencia,
        'Linha inserida na particao default; competencia=' || NEW.competencia::text
    );

    return NEW;
end;
$$;

drop trigger if exists trg_alertar_default_particao
    on bruto_ans.sib_beneficiario_operadora_default;

create trigger trg_alertar_default_particao
after insert on bruto_ans.sib_beneficiario_operadora_default
for each row
execute function plataforma.alertar_default_particao();

drop trigger if exists trg_alertar_default_particao
    on bruto_ans.sib_beneficiario_municipio_default;

create trigger trg_alertar_default_particao
after insert on bruto_ans.sib_beneficiario_municipio_default
for each row
execute function plataforma.alertar_default_particao();

do $$
declare
    v_janela record;
    v_limite_particao_preparada integer;
    v_total_operadora bigint;
    v_total_municipio bigint;
begin
    select *
      into v_janela
      from plataforma.calcular_janela_carga_anual(2);

    v_limite_particao_preparada := ((v_janela.ano_preparado + 1) * 100) + 1;

    select count(*)
      into v_total_operadora
      from bruto_ans.sib_beneficiario_operadora_default
     where competencia >= v_janela.competencia_minima
       and competencia < v_limite_particao_preparada;

    if v_total_operadora > 0 then
        raise exception
            'Default bruto_ans.sib_beneficiario_operadora_default contem % linhas na janela planejada [% - %). Migracao manual com backup/dry-run obrigatoria.',
            v_total_operadora,
            v_janela.competencia_minima,
            v_limite_particao_preparada;
    end if;

    select count(*)
      into v_total_municipio
      from bruto_ans.sib_beneficiario_municipio_default
     where competencia >= v_janela.competencia_minima
       and competencia < v_limite_particao_preparada;

    if v_total_municipio > 0 then
        raise exception
            'Default bruto_ans.sib_beneficiario_municipio_default contem % linhas na janela planejada [% - %). Migracao manual com backup/dry-run obrigatoria.',
            v_total_municipio,
            v_janela.competencia_minima,
            v_limite_particao_preparada;
    end if;
end $$;

select plataforma.preparar_particoes_janela_atual(
    'bruto_ans',
    'sib_beneficiario_operadora',
    2
);

select plataforma.preparar_particoes_janela_atual(
    'bruto_ans',
    'sib_beneficiario_municipio',
    2
);
