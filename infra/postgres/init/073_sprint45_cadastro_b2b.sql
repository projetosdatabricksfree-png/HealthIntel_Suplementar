-- Sprint 45 — cadastro B2B profissional
-- Perfil comercial do usuário além do auth (email/senha). Aditivo, idempotente.

create table if not exists plataforma.usuario_perfil_b2b (
    usuario_id uuid primary key references plataforma.usuario(id) on delete cascade,
    empresa text not null,
    cnpj char(14) not null,
    telefone text not null,
    cargo text not null,
    segmento text not null check (segmento in (
        'operadora',
        'corretora_administradora',
        'healthtech',
        'consultoria',
        'hospital_prestador',
        'escritorio_juridico',
        'bi_dados',
        'outro'
    )),
    objetivo_uso text not null check (objetivo_uso in (
        'testar_api',
        'avaliar_dados_ans',
        'integrar_bi',
        'pesquisa_regulatoria',
        'avaliacao_comercial'
    )),
    site_empresa text,
    tamanho_empresa text,
    mensagem text,
    aceite_termos_em timestamptz not null,
    aceite_lgpd_em timestamptz not null,
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now()
);

create index if not exists ix_usuario_perfil_b2b_cnpj
    on plataforma.usuario_perfil_b2b (cnpj);

create index if not exists ix_usuario_perfil_b2b_segmento
    on plataforma.usuario_perfil_b2b (segmento);

comment on table plataforma.usuario_perfil_b2b is
    'Perfil comercial B2B do usuário (empresa, CNPJ, segmento, objetivo, aceites legais).';
