alter table if exists bruto_ans.cadop
    add column if not exists _hash_linha text;

alter table if exists bruto_ans.sib_beneficiario_operadora
    add column if not exists _hash_linha text;

alter table if exists bruto_ans.sib_beneficiario_municipio
    add column if not exists _hash_linha text;

alter table if exists bruto_ans.igr_operadora_trimestral
    add column if not exists _hash_linha text;

alter table if exists bruto_ans.nip_operadora_trimestral
    add column if not exists _hash_linha text;

alter table if exists bruto_ans.rn623_lista_operadora_trimestral
    add column if not exists _hash_linha text;

alter table if exists bruto_ans.idss
    add column if not exists _hash_linha text;

alter table if exists bruto_ans.regime_especial_operadora_trimestral
    add column if not exists _hash_linha text;

alter table if exists bruto_ans.prudencial_operadora_trimestral
    add column if not exists _hash_linha text;

alter table if exists bruto_ans.portabilidade_operadora_mensal
    add column if not exists _hash_linha text;

alter table if exists bruto_ans.taxa_resolutividade_operadora_trimestral
    add column if not exists _hash_linha text;

alter table if exists bruto_ans.diops_operadora_trimestral
    add column if not exists _hash_linha text;

alter table if exists bruto_ans.fip_operadora_trimestral
    add column if not exists _hash_linha text;

alter table if exists bruto_ans.vda_operadora_mensal
    add column if not exists _hash_linha text;

alter table if exists bruto_ans.glosa_operadora_mensal
    add column if not exists _hash_linha text;

alter table if exists bruto_ans.rede_prestador_municipio
    add column if not exists _hash_linha text;

alter table if exists bruto_ans.cnes_estabelecimento
    add column if not exists _hash_linha text;

alter table if exists bruto_ans.tiss_procedimento_trimestral
    add column if not exists _hash_linha text;

create unique index if not exists uq_cadop_competencia_hash
    on bruto_ans.cadop (competencia, _hash_arquivo);

create unique index if not exists uq_sib_operadora_competencia_hash
    on bruto_ans.sib_beneficiario_operadora (competencia, _hash_arquivo);

create unique index if not exists uq_sib_municipio_competencia_hash
    on bruto_ans.sib_beneficiario_municipio (competencia, _hash_arquivo);

create unique index if not exists uq_igr_competencia_hash
    on bruto_ans.igr_operadora_trimestral (trimestre, _hash_arquivo);

create unique index if not exists uq_nip_competencia_hash
    on bruto_ans.nip_operadora_trimestral (trimestre, _hash_arquivo);

create unique index if not exists uq_rn623_competencia_hash
    on bruto_ans.rn623_lista_operadora_trimestral (trimestre, _hash_arquivo);

create unique index if not exists uq_idss_competencia_hash
    on bruto_ans.idss (ano_base, _hash_arquivo);

create unique index if not exists uq_regime_especial_competencia_hash
    on bruto_ans.regime_especial_operadora_trimestral (trimestre, _hash_arquivo);

create unique index if not exists uq_prudencial_competencia_hash
    on bruto_ans.prudencial_operadora_trimestral (trimestre, _hash_arquivo);

create unique index if not exists uq_portabilidade_competencia_hash
    on bruto_ans.portabilidade_operadora_mensal (competencia, _hash_arquivo);

create unique index if not exists uq_taxa_resolutividade_competencia_hash
    on bruto_ans.taxa_resolutividade_operadora_trimestral (trimestre, _hash_arquivo);

create unique index if not exists uq_diops_competencia_hash
    on bruto_ans.diops_operadora_trimestral (trimestre, _hash_arquivo);

create unique index if not exists uq_fip_competencia_hash
    on bruto_ans.fip_operadora_trimestral (trimestre, _hash_arquivo);

create unique index if not exists uq_vda_competencia_hash
    on bruto_ans.vda_operadora_mensal (competencia, _hash_arquivo);

create unique index if not exists uq_glosa_competencia_hash
    on bruto_ans.glosa_operadora_mensal (competencia, _hash_arquivo);

create unique index if not exists uq_rede_competencia_hash
    on bruto_ans.rede_prestador_municipio (competencia, _hash_arquivo);

create unique index if not exists uq_cnes_competencia_hash
    on bruto_ans.cnes_estabelecimento (competencia, _hash_arquivo);

create unique index if not exists uq_tiss_competencia_hash
    on bruto_ans.tiss_procedimento_trimestral (trimestre, _hash_arquivo);
