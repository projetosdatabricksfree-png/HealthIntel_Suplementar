-- Sprint 41: Delta ANS 100% — Rede, Prestadores e Acreditação Complementares
-- Subfamílias: operadoras canceladas, operadoras acreditadas,
--              prestadores acreditados, produtos/prestadores hospitalares,
--              operadoras/prestadores não hospitalares,
--              solicitações de alteração de rede hospitalar

create table if not exists bruto_ans.operadora_cancelada (
    registro_ans varchar(6),
    razao_social text,
    cnpj varchar(20),
    modalidade text,
    data_cancelamento date,
    motivo_cancelamento text,
    sg_uf char(2),
    _carregado_em timestamptz not null default now(),
    _arquivo_origem text not null,
    _lote_id uuid not null,
    _layout_id text not null,
    _layout_versao_id text not null,
    _hash_arquivo text not null,
    _hash_estrutura text not null,
    _status_parse text not null
);

create index if not exists ix_operadora_cancelada_registro_ans
    on bruto_ans.operadora_cancelada (registro_ans);
create index if not exists ix_operadora_cancelada_uf
    on bruto_ans.operadora_cancelada (sg_uf);

create table if not exists bruto_ans.operadora_acreditada (
    registro_ans varchar(6),
    razao_social text,
    acreditadora text,
    nivel_acreditacao text,
    data_acreditacao date,
    data_validade date,
    _carregado_em timestamptz not null default now(),
    _arquivo_origem text not null,
    _lote_id uuid not null,
    _layout_id text not null,
    _layout_versao_id text not null,
    _hash_arquivo text not null,
    _hash_estrutura text not null,
    _status_parse text not null
);

create index if not exists ix_operadora_acreditada_registro_ans
    on bruto_ans.operadora_acreditada (registro_ans);

create table if not exists bruto_ans.prestador_acreditado (
    cnes varchar(7),
    nm_prestador text,
    cnpj varchar(20),
    cd_municipio varchar(7),
    nm_municipio text,
    sg_uf char(2),
    acreditadora text,
    nivel_acreditacao text,
    data_acreditacao date,
    data_validade date,
    _carregado_em timestamptz not null default now(),
    _arquivo_origem text not null,
    _lote_id uuid not null,
    _layout_id text not null,
    _layout_versao_id text not null,
    _hash_arquivo text not null,
    _hash_estrutura text not null,
    _status_parse text not null
);

create index if not exists ix_prestador_acreditado_cnes
    on bruto_ans.prestador_acreditado (cnes);
create index if not exists ix_prestador_acreditado_municipio
    on bruto_ans.prestador_acreditado (cd_municipio);

create table if not exists bruto_ans.produto_prestador_hospitalar (
    competencia integer,
    registro_ans varchar(6),
    codigo_produto varchar(20),
    cnes varchar(7),
    nm_prestador text,
    cd_municipio varchar(7),
    sg_uf char(2),
    tipo_vinculo text,
    _carregado_em timestamptz not null default now(),
    _arquivo_origem text not null,
    _lote_id uuid not null,
    _layout_id text not null,
    _layout_versao_id text not null,
    _hash_arquivo text not null,
    _hash_estrutura text not null,
    _status_parse text not null
);

create index if not exists ix_produto_prestador_hospitalar_registro_ans
    on bruto_ans.produto_prestador_hospitalar (registro_ans, codigo_produto);
create index if not exists ix_produto_prestador_hospitalar_cnes
    on bruto_ans.produto_prestador_hospitalar (cnes);

create table if not exists bruto_ans.operadora_prestador_nao_hospitalar (
    competencia integer,
    registro_ans varchar(6),
    cnes varchar(7),
    nm_prestador text,
    cd_municipio varchar(7),
    sg_uf char(2),
    tipo_servico text,
    tipo_vinculo text,
    _carregado_em timestamptz not null default now(),
    _arquivo_origem text not null,
    _lote_id uuid not null,
    _layout_id text not null,
    _layout_versao_id text not null,
    _hash_arquivo text not null,
    _hash_estrutura text not null,
    _status_parse text not null
);

create index if not exists ix_operadora_prestador_nao_hospitalar_registro_ans
    on bruto_ans.operadora_prestador_nao_hospitalar (registro_ans, competencia);
create index if not exists ix_operadora_prestador_nao_hospitalar_cnes
    on bruto_ans.operadora_prestador_nao_hospitalar (cnes);

create table if not exists bruto_ans.solicitacao_alteracao_rede_hospitalar (
    competencia integer,
    registro_ans varchar(6),
    nu_solicitacao varchar(30),
    tipo_alteracao text,
    cnes varchar(7),
    nm_prestador text,
    cd_municipio varchar(7),
    sg_uf char(2),
    data_solicitacao date,
    status_solicitacao text,
    _carregado_em timestamptz not null default now(),
    _arquivo_origem text not null,
    _lote_id uuid not null,
    _layout_id text not null,
    _layout_versao_id text not null,
    _hash_arquivo text not null,
    _hash_estrutura text not null,
    _status_parse text not null
);

create index if not exists ix_solicitacao_alteracao_rede_registro_ans
    on bruto_ans.solicitacao_alteracao_rede_hospitalar (registro_ans, competencia);
create index if not exists ix_solicitacao_alteracao_rede_cnes
    on bruto_ans.solicitacao_alteracao_rede_hospitalar (cnes);
