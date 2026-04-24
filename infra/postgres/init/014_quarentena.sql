create table if not exists bruto_ans.cadop_quarentena (
    id_quarentena bigserial primary key,
    lote_id uuid not null,
    arquivo_origem text not null,
    linha_original jsonb not null,
    motivo_rejeicao text not null,
    regra_falhou text not null,
    _carregado_em timestamptz not null default now()
);

create table if not exists bruto_ans.sib_operadora_quarentena (
    id_quarentena bigserial primary key,
    lote_id uuid not null,
    arquivo_origem text not null,
    linha_original jsonb not null,
    motivo_rejeicao text not null,
    regra_falhou text not null,
    _carregado_em timestamptz not null default now()
);

create table if not exists bruto_ans.sib_municipio_quarentena (
    id_quarentena bigserial primary key,
    lote_id uuid not null,
    arquivo_origem text not null,
    linha_original jsonb not null,
    motivo_rejeicao text not null,
    regra_falhou text not null,
    _carregado_em timestamptz not null default now()
);

create table if not exists bruto_ans.igr_quarentena (
    id_quarentena bigserial primary key,
    lote_id uuid not null,
    arquivo_origem text not null,
    linha_original jsonb not null,
    motivo_rejeicao text not null,
    regra_falhou text not null,
    _carregado_em timestamptz not null default now()
);

create table if not exists bruto_ans.nip_quarentena (
    id_quarentena bigserial primary key,
    lote_id uuid not null,
    arquivo_origem text not null,
    linha_original jsonb not null,
    motivo_rejeicao text not null,
    regra_falhou text not null,
    _carregado_em timestamptz not null default now()
);

create table if not exists bruto_ans.idss_quarentena (
    id_quarentena bigserial primary key,
    lote_id uuid not null,
    arquivo_origem text not null,
    linha_original jsonb not null,
    motivo_rejeicao text not null,
    regra_falhou text not null,
    _carregado_em timestamptz not null default now()
);

create table if not exists bruto_ans.diops_quarentena (
    id_quarentena bigserial primary key,
    lote_id uuid not null,
    arquivo_origem text not null,
    linha_original jsonb not null,
    motivo_rejeicao text not null,
    regra_falhou text not null,
    _carregado_em timestamptz not null default now()
);

create table if not exists bruto_ans.fip_quarentena (
    id_quarentena bigserial primary key,
    lote_id uuid not null,
    arquivo_origem text not null,
    linha_original jsonb not null,
    motivo_rejeicao text not null,
    regra_falhou text not null,
    _carregado_em timestamptz not null default now()
);

create table if not exists bruto_ans.vda_quarentena (
    id_quarentena bigserial primary key,
    lote_id uuid not null,
    arquivo_origem text not null,
    linha_original jsonb not null,
    motivo_rejeicao text not null,
    regra_falhou text not null,
    _carregado_em timestamptz not null default now()
);

create table if not exists bruto_ans.glosa_quarentena (
    id_quarentena bigserial primary key,
    lote_id uuid not null,
    arquivo_origem text not null,
    linha_original jsonb not null,
    motivo_rejeicao text not null,
    regra_falhou text not null,
    _carregado_em timestamptz not null default now()
);

create table if not exists bruto_ans.rede_assistencial_quarentena (
    id_quarentena bigserial primary key,
    lote_id uuid not null,
    arquivo_origem text not null,
    linha_original jsonb not null,
    motivo_rejeicao text not null,
    regra_falhou text not null,
    _carregado_em timestamptz not null default now()
);

create or replace view plataforma.vw_resumo_quarentena as
select
    q.dataset,
    q.arquivo_origem,
    coalesce(v.competencia, 'desconhecida') as competencia,
    q.hash_arquivo,
    count(*) as total_registros,
    min(q.criado_em) as primeiro_registro_em,
    max(q.criado_em) as ultimo_registro_em,
    array_agg(distinct q.status order by q.status) as status_quarentena
from plataforma.arquivo_quarentena q
left join lateral (
    select competencia
    from plataforma.versao_dataset v
    where v.dataset = q.dataset
      and v.hash_arquivo = q.hash_arquivo
    order by v.carregado_em desc
    limit 1
) v on true
group by 1, 2, 3, 4;
