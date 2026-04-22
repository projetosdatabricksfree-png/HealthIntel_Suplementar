create schema if not exists bruto_ans;
create schema if not exists stg_ans;
create schema if not exists int_ans;
create schema if not exists nucleo_ans;
create schema if not exists api_ans;
create schema if not exists ref_ans;
create schema if not exists plataforma;

-- bruto_ans.cadop (operadoras)
create table if not exists bruto_ans.cadop (
    _lote_id uuid not null,
    _carregado_em timestamp not null default now(),
    registro_ans varchar(6) not null,
    cnpj varchar(14),
    razao_social varchar(256),
    nome_fantasia varchar(256),
    modalidade varchar(50),
    logradouro varchar(256),
    numero varchar(10),
    complemento varchar(256),
    bairro varchar(100),
    cidade varchar(100),
    uf varchar(2),
    cep varchar(8),
    ddd varchar(2),
    telefone varchar(10),
    fax varchar(10),
    endereco_eletronico varchar(256),
    representante varchar(256),
    cargo_representante varchar(100),
    regiao_de_comercializacao varchar(100),
    data_registro_ans date,
    primary key (registro_ans, _lote_id)
);
create index if not exists ix_cadop_registro_ans on bruto_ans.cadop (registro_ans);

-- bruto_ans.sib_beneficiario_operadora (beneficiarios por operadora, particionado por competencia)
create table if not exists bruto_ans.sib_beneficiario_operadora (
    _lote_id uuid not null,
    _carregado_em timestamp not null default now(),
    competencia varchar(6) not null,
    cd_operadora integer not null,
    beneficiario_id varchar(50),
    cpf_cnpj varchar(14),
    data_nascimento date,
    sexo varchar(1),
    plano_id varchar(50),
    cobertura_hospitalar boolean,
    cobertura_ambulatorial boolean,
    cobertura_odontologica boolean,
    ativo boolean,
    primary key (cd_operadora, competencia, _lote_id)
) partition by range (competencia);

create index if not exists ix_sib_operadora_competencia_brin on bruto_ans.sib_beneficiario_operadora using brin (competencia);
create index if not exists ix_sib_operadora_cd on bruto_ans.sib_beneficiario_operadora (cd_operadora);

-- bruto_ans.sib_beneficiario_municipio (beneficiarios por municipio, particionado por competencia)
create table if not exists bruto_ans.sib_beneficiario_municipio (
    _lote_id uuid not null,
    _carregado_em timestamp not null default now(),
    competencia varchar(6) not null,
    cd_municipio integer not null,
    cd_operadora integer not null,
    beneficiario_id varchar(50),
    ativo boolean,
    primary key (cd_municipio, cd_operadora, competencia, _lote_id)
) partition by range (competencia);

create index if not exists ix_sib_municipio_competencia_brin on bruto_ans.sib_beneficiario_municipio using brin (competencia);
create index if not exists ix_sib_municipio_cd_municipio on bruto_ans.sib_beneficiario_municipio (cd_municipio);

-- plataforma.log_uso (particionado por data)
create table if not exists plataforma.log_uso (
    _id uuid primary key default gen_random_uuid(),
    _criado_em timestamp not null default now(),
    competencia varchar(6),
    cliente_id integer,
    endpoint varchar(256),
    metodo varchar(10),
    status_code integer,
    tempo_ms integer,
    erro_msg text
) partition by range (competencia);
