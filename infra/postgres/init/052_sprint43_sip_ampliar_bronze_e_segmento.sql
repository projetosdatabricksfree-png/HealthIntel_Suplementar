-- Sprint 43 — Ampliação bronze SIP + novos marts segmento
-- Fonte ANS publica `sip_mapa_assistencial_YYYYMM.csv` agregada por porte+modalidade+cobertura+contratação
-- e NÃO por operadora/município. O parser anterior pressupunha REGISTRO_ANS/CD_MUNICIPIO que não existem
-- no arquivo. As 5 colunas continuam vivas (compatibilidade com `api_sip_assistencial_operadora`), mas
-- adicionamos as colunas reais do arquivo público para que stg/marts segmento sejam materializados.

-- 1) Adicionar colunas reais da fonte ANS pública
alter table bruto_ans.sip_mapa_assistencial
    add column if not exists porte_operadora      text,
    add column if not exists gr_modalidade        text,
    add column if not exists cobertura            text,
    add column if not exists contratacao          text,
    add column if not exists id_item_asst         text,
    add column if not exists vl_despesa_asst_liq  numeric(18, 2),
    add column if not exists dt_corte             date;

create index if not exists ix_sip_mapa_assistencial_porte_modalidade
    on bruto_ans.sip_mapa_assistencial (porte_operadora, gr_modalidade);
create index if not exists ix_sip_mapa_assistencial_cobertura_contratacao
    on bruto_ans.sip_mapa_assistencial (cobertura, contratacao);

comment on column bruto_ans.sip_mapa_assistencial.porte_operadora is
    'Categoria de porte da operadora — fonte pública é agregada por segmento, não por operadora';
comment on column bruto_ans.sip_mapa_assistencial.gr_modalidade is
    'Grupo de modalidade ANS (seguradora, autogestão, cooperativa, medicina de grupo, etc)';
comment on column bruto_ans.sip_mapa_assistencial.cobertura is
    'Tipo de cobertura (MÉDICO-HOSPITALAR, EXCLUSIVAMENTE ODONTOLÓGICO)';
comment on column bruto_ans.sip_mapa_assistencial.contratacao is
    'Tipo de contratação (Coletivo Empresarial, Coletivo por Adesão, Individual, etc)';
comment on column bruto_ans.sip_mapa_assistencial.id_item_asst is
    'Código do item assistencial (B.01, C.18, etc)';
comment on column bruto_ans.sip_mapa_assistencial.vl_despesa_asst_liq is
    'Valor da despesa assistencial líquida (R$)';
comment on column bruto_ans.sip_mapa_assistencial.dt_corte is
    'Data de corte do dado divulgada pela ANS';
