-- Sprint 41: Delta ANS 100% — Produtos e Planos
-- Famílias: características de produtos, histórico de planos,
--           serviços opcionais, quadros de corresponsabilidade

create table if not exists bruto_ans.produto_caracteristica (
    competencia integer,
    registro_ans varchar(6),
    codigo_produto varchar(20),
    nome_produto text,
    segmentacao text,
    tipo_contratacao text,
    abrangencia_geografica text,
    cobertura_area text,
    modalidade text,
    uf_comercializacao char(2),
    _carregado_em timestamptz not null default now(),
    _arquivo_origem text not null,
    _lote_id uuid not null,
    _layout_id text not null,
    _layout_versao_id text not null,
    _hash_arquivo text not null,
    _hash_estrutura text not null,
    _status_parse text not null
);

create index if not exists ix_produto_caracteristica_registro_ans
    on bruto_ans.produto_caracteristica (registro_ans);
create index if not exists ix_produto_caracteristica_codigo_produto
    on bruto_ans.produto_caracteristica (codigo_produto);
create index if not exists ix_produto_caracteristica_competencia
    on bruto_ans.produto_caracteristica (competencia);

create table if not exists bruto_ans.produto_tabela_auxiliar (
    competencia integer,
    registro_ans varchar(6),
    codigo_produto varchar(20),
    tipo_tabela text,
    descricao_tabela text,
    codigo_item varchar(20),
    descricao_item text,
    _carregado_em timestamptz not null default now(),
    _arquivo_origem text not null,
    _lote_id uuid not null,
    _layout_id text not null,
    _layout_versao_id text not null,
    _hash_arquivo text not null,
    _hash_estrutura text not null,
    _status_parse text not null
);

create index if not exists ix_produto_tabela_auxiliar_registro_ans
    on bruto_ans.produto_tabela_auxiliar (registro_ans);
create index if not exists ix_produto_tabela_auxiliar_codigo_produto
    on bruto_ans.produto_tabela_auxiliar (codigo_produto);

create table if not exists bruto_ans.historico_plano (
    competencia integer,
    registro_ans varchar(6),
    codigo_plano varchar(20),
    nome_plano text,
    situacao text,
    data_situacao date,
    segmentacao text,
    tipo_contratacao text,
    abrangencia_geografica text,
    uf char(2),
    _carregado_em timestamptz not null default now(),
    _arquivo_origem text not null,
    _lote_id uuid not null,
    _layout_id text not null,
    _layout_versao_id text not null,
    _hash_arquivo text not null,
    _hash_estrutura text not null,
    _status_parse text not null
);

create index if not exists ix_historico_plano_registro_ans
    on bruto_ans.historico_plano (registro_ans);
create index if not exists ix_historico_plano_codigo_plano
    on bruto_ans.historico_plano (codigo_plano);
create index if not exists ix_historico_plano_competencia
    on bruto_ans.historico_plano (competencia);

create table if not exists bruto_ans.plano_servico_opcional (
    competencia integer,
    registro_ans varchar(6),
    codigo_plano varchar(20),
    codigo_servico varchar(20),
    descricao_servico text,
    tipo_servico text,
    _carregado_em timestamptz not null default now(),
    _arquivo_origem text not null,
    _lote_id uuid not null,
    _layout_id text not null,
    _layout_versao_id text not null,
    _hash_arquivo text not null,
    _hash_estrutura text not null,
    _status_parse text not null
);

create index if not exists ix_plano_servico_opcional_registro_ans
    on bruto_ans.plano_servico_opcional (registro_ans, codigo_plano);

create table if not exists bruto_ans.quadro_auxiliar_corresponsabilidade (
    competencia integer,
    registro_ans varchar(6),
    codigo_plano varchar(20),
    tipo_corresponsabilidade text,
    percentual_corresponsabilidade numeric(7, 4),
    valor_corresponsabilidade numeric(18, 2),
    descricao text,
    _carregado_em timestamptz not null default now(),
    _arquivo_origem text not null,
    _lote_id uuid not null,
    _layout_id text not null,
    _layout_versao_id text not null,
    _hash_arquivo text not null,
    _hash_estrutura text not null,
    _status_parse text not null
);

create index if not exists ix_quadro_auxiliar_corresponsabilidade_registro_ans
    on bruto_ans.quadro_auxiliar_corresponsabilidade (registro_ans, codigo_plano);
