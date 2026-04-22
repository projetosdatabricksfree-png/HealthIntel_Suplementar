create table if not exists bruto_ans.cadop (
    registro_ans varchar(20),
    cnpj varchar(20),
    razao_social text,
    nome_fantasia text,
    modalidade text,
    cidade text,
    uf char(2),
    competencia integer,
    _carregado_em timestamptz not null default now(),
    _arquivo_origem text not null,
    _lote_id uuid not null,
    _layout_id text not null,
    _layout_versao_id text not null,
    _hash_arquivo text not null,
    _hash_estrutura text not null,
    _status_parse text not null
);

create index if not exists ix_cadop_registro_ans on bruto_ans.cadop (registro_ans);
create index if not exists ix_cadop_layout_versao on bruto_ans.cadop (_layout_versao_id);

create table if not exists bruto_ans.sib_beneficiario_operadora (
    competencia integer not null,
    registro_ans varchar(6) not null,
    beneficiario_medico integer,
    beneficiario_odonto integer,
    beneficiario_total integer,
    _carregado_em timestamptz not null default now(),
    _arquivo_origem text not null,
    _lote_id uuid not null,
    _layout_id text not null,
    _layout_versao_id text not null,
    _hash_arquivo text not null,
    _hash_estrutura text not null,
    _status_parse text not null
) partition by range (competencia);

create table if not exists bruto_ans.sib_beneficiario_operadora_default
    partition of bruto_ans.sib_beneficiario_operadora default;

create index if not exists ix_sib_operadora_competencia
    on bruto_ans.sib_beneficiario_operadora (competencia, registro_ans);

create table if not exists bruto_ans.sib_beneficiario_municipio (
    competencia integer not null,
    registro_ans varchar(6) not null,
    codigo_ibge varchar(7),
    municipio text,
    uf char(2),
    beneficiario_medico integer,
    beneficiario_odonto integer,
    beneficiario_total integer,
    _carregado_em timestamptz not null default now(),
    _arquivo_origem text not null,
    _lote_id uuid not null,
    _layout_id text not null,
    _layout_versao_id text not null,
    _hash_arquivo text not null,
    _hash_estrutura text not null,
    _status_parse text not null
) partition by range (competencia);

create table if not exists bruto_ans.sib_beneficiario_municipio_default
    partition of bruto_ans.sib_beneficiario_municipio default;

create index if not exists ix_sib_municipio_competencia
    on bruto_ans.sib_beneficiario_municipio (competencia, registro_ans, codigo_ibge);

create table if not exists plataforma.execucao_layout (
    id uuid primary key,
    arquivo_id text not null,
    dataset text not null,
    layout_id text not null,
    layout_versao_id text not null,
    status text not null,
    iniciado_em timestamptz not null,
    finalizado_em timestamptz,
    registros_processados integer not null default 0,
    registros_com_erro integer not null default 0
);

create table if not exists plataforma.dataset_layout_ativo (
    dataset text primary key,
    layout_id text not null,
    layout_versao_id text not null,
    atualizado_em timestamptz not null default now()
);

create table if not exists plataforma.erro_parse (
    id bigserial primary key,
    lote_id uuid not null,
    arquivo_origem text not null,
    linha_origem integer,
    coluna_origem text,
    valor_origem text,
    codigo_erro text not null,
    mensagem_erro text not null,
    criado_em timestamptz not null default now()
);

create table if not exists plataforma.controle_reprocessamento (
    id uuid primary key,
    dataset text not null,
    arquivo_origem text not null,
    layout_versao_origem text not null,
    layout_versao_destino text not null,
    status text not null,
    solicitado_em timestamptz not null default now(),
    finalizado_em timestamptz
);

create table if not exists plataforma.arquivo_quarentena (
    id uuid primary key,
    dataset text not null,
    arquivo_origem text not null,
    hash_arquivo text not null,
    hash_estrutura text,
    motivo text not null,
    status text not null,
    criado_em timestamptz not null default now()
);

create table if not exists plataforma.mapa_layout_resolvido (
    id bigserial primary key,
    lote_id uuid not null,
    layout_id text not null,
    layout_versao_id text not null,
    origem_coluna text not null,
    destino_raw text not null,
    regra_transformacao text,
    criado_em timestamptz not null default now()
);

create table if not exists plataforma.versao_dataset (
    id uuid primary key,
    dataset text not null,
    versao text not null,
    competencia text,
    hash_arquivo text not null,
    hash_estrutura text,
    carregado_em timestamptz not null default now(),
    registros bigint not null default 0,
    status text not null
);

create table if not exists plataforma.job (
    id uuid primary key,
    dag_id text not null,
    nome_job text not null,
    fonte_ans text,
    status text not null,
    iniciado_em timestamptz not null,
    finalizado_em timestamptz,
    registro_processado bigint not null default 0,
    registro_com_falha bigint not null default 0,
    mensagem_erro text
);
