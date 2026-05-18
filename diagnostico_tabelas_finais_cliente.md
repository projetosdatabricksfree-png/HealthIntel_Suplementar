# Diagnóstico: Tabelas Finais de Cliente — HealthIntel

**Gerado em:** 2026-05-17 23:34 UTC  
**Objetivo:** Identificar o que está pronto para uso comercial em `api_ans` e `consumo_ans`.

---

## Resumo Executivo

| Schema | Prontas | Vazias | Total | Registros Prontos |
|--------|---------|--------|-------|-------------------|
| **api_ans** | 45 | 56 | 101 | 11,770,796 |
| **consumo_ans** | 17 | 9 | 26 | 812,778 |

---

## `api_ans` — Tabelas PRONTAS para uso comercial

**45 tabelas populadas** com 11,770,796 registros totais.

| Domínio | Tabela | Registros | Período Coberto | Períodos Distintos |
|---------|--------|-----------|-----------------|-------------------|
| financeiro | `api_bronze_diops` | 10,232,252 | 1T2023 → 4T2025 | 13 |
| financeiro | `api_prata_diops` | 11,563 | 1T2023 → 4T2025 | 13 |
| financeiro | `api_prata_financeiro_periodo` | 10,978 | 1T2023 → 4T2025 | 13 |
| mercado/beneficiários | `api_bronze_sib_municipio` | 59,892 | 202603 → 202603 | 1 |
| mercado/beneficiários | `api_market_share_mensal` | 59,197 | 202603 → 202603 | 1 |
| mercado/beneficiários | `api_prata_municipio_metrica` | 59,197 | 202603 → 202603 | 1 |
| mercado/beneficiários | `api_prata_sib_municipio` | 59,892 | 202603 → 202603 | 1 |
| operadora | `api_bronze_cadop` | 1,107 | 202605 → 202605 | 1 |
| operadora | `api_bronze_sib_operadora` | 803 | 202603 → 202603 | 1 |
| operadora | `api_glosa_operadora_mensal` | 4,170 | 202501 → 202501 | 1 |
| operadora | `api_operadora` | 1,107 | sem coluna temporal | — |
| operadora | `api_prata_cadop` | 1,107 | sem coluna temporal | — |
| operadora | `api_prata_operadora_enriquecida` | 757 | 202603 → 202603 | 1 |
| operadora | `api_prata_sib_operadora` | 803 | 202603 → 202603 | 1 |
| operadora | `api_premium_mdm_operadora` | 1,107 | sem coluna temporal | — |
| operadora | `api_premium_operadora_360_validado` | 757 | 202603 → 202603 | 1 |
| operadora | `api_prudencial_operadora_trimestral` | 11,216 | 1T2024 → 4T2025 | 10 |
| operadora | `api_regime_especial_operadora` | 53 | 1T2003 → 1T2025 | 15 |
| operadora | `api_regime_especial_operadora_trimestral` | 117 | 1T2002 → 1T2025 | 20 |
| operadora | `api_regulatorio_operadora_trimestral` | 125,287 | 201101 → 202604 | 184 |
| operadora | `api_score_operadora_mensal` | 757 | 202603 → 202603 | 1 |
| operadora | `api_score_regulatorio_operadora_mensal` | 136,032 | 1T2003 → 4T2025 | 207 |
| operadora | `api_score_v2_operadora_mensal` | 136,034 | 1T2003 → 4T2025 | 207 |
| operadora | `api_score_v3_operadora_mensal` | 757 | sem coluna temporal | — |
| operadora | `api_taxa_resolutividade_operadora_trimestral` | 26,062 | 201501 → 201910 | 58 |
| outros | `api_quadro_auxiliar_corresponsabilidade` | 1,032 | 202505 → 202505 | 1 |
| premium/MDM | `api_premium_quality_dataset` | 2 | sem coluna temporal | — |
| produtos/planos | `api_historico_plano` | 163,567 | 202505 → 202505 | 1 |
| produtos/planos | `api_premium_tuss_procedimento` | 3,500 | sem coluna temporal | — |
| produtos/planos | `api_produto_plano` | 163,661 | 202605 → 202605 | 1 |
| produtos/planos | `api_tuss_procedimento_vigente` | 64,654 | sem coluna temporal | — |
| regulatório | `api_bronze_glosa` | 4,170 | 202501 → 202501 | 1 |
| regulatório | `api_bronze_idss` | 13,072 | sem coluna temporal | — |
| regulatório | `api_bronze_igr` | 150,501 | 201501 → 202604 | 136 |
| regulatório | `api_bronze_nip` | 53,637 | 201101 → 202012 | 120 |
| regulatório | `api_prata_glosa` | 4,170 | 202501 → 202501 | 1 |
| regulatório | `api_prata_idss` | 13,072 | sem coluna temporal | — |
| regulatório | `api_prata_igr` | 136,908 | 201501 → 202604 | 136 |
| regulatório | `api_prata_nip` | 53,637 | 201101 → 202012 | 120 |
| score/ranking | `api_oportunidade_municipio_mensal` | 646 | 202603 → 202603 | 1 |
| score/ranking | `api_oportunidade_v2_municipio_mensal` | 646 | 202603 → 202603 | 1 |
| score/ranking | `api_ranking_composto_mensal` | 757 | sem coluna temporal | — |
| score/ranking | `api_ranking_crescimento` | 757 | 202603 → 202603 | 1 |
| score/ranking | `api_ranking_oportunidade` | 646 | 202603 → 202603 | 1 |
| score/ranking | `api_ranking_score` | 757 | 202603 → 202603 | 1 |

---

## `api_ans` — Tabelas VAZIAS (causa provável)

**56 tabelas sem dados** — detalhamento por domínio:

| Domínio | Tabela | Causa Provável |
|---------|--------|----------------|
| financeiro | `api_bronze_fip` | Fonte FIP não carregada em bruto_ans |
| financeiro | `api_prata_fip` | Fonte FIP não carregada em bruto_ans |
| mercado/beneficiários | `api_cnes_municipio` | Fonte CNES não carregada em bruto_ans |
| mercado/beneficiários | `api_prata_cnes_municipio` | Fonte CNES não carregada em bruto_ans |
| mercado/beneficiários | `api_valor_comercial_medio_municipio` | Fonte bruta ausente ou dbt model dependente de dado não carregado |
| operadora | `api_financeiro_operadora_mensal` | fat_vda_operadora: fonte VDA não carregada em bruto_ans |
| operadora | `api_operadora_acreditada` | Fonte bruta ausente ou dbt model dependente de dado não carregado |
| operadora | `api_operadora_cancelada` | Fonte bruta ausente ou dbt model dependente de dado não carregado |
| operadora | `api_operadora_prestador_nao_hospitalar` | produto_prestador: registro_ans=NULL em todos os registros brutos |
| operadora | `api_penalidade_operadora` | Fonte bruta ausente ou dbt model dependente de dado não carregado |
| operadora | `api_portabilidade_operadora_mensal` | Fonte portabilidade não carregada em bruto_ans |
| operadora | `api_ressarcimento_sus_operadora_plano` | Fonte ressarcimento não carregada em bruto_ans |
| operadora | `api_rpc_operadora_mes` | Fonte bruta ausente ou dbt model dependente de dado não carregado |
| operadora | `api_sip_assistencial_operadora` | Fonte SIB/SIP não carregada ou registro_ans=NULL no bruto |
| operadora | `api_tiss_ambulatorial_operadora_mes` | Fonte TISS não carregada em bruto_ans |
| operadora | `api_tiss_hospitalar_operadora_mes` | Fonte TISS não carregada em bruto_ans |
| operadora | `api_tiss_operadora_trimestral` | Fonte TISS não carregada em bruto_ans |
| outros | `api_beneficiario_informacao_consolidada` | SIB beneficiário não materializado via dbt |
| outros | `api_beneficiario_regiao_geografica` | SIB beneficiário não materializado via dbt |
| outros | `api_bronze_vda` | Fonte VDA não carregada em bruto_ans |
| outros | `api_faixa_preco` | Fonte bruta ausente ou dbt model dependente de dado não carregado |
| outros | `api_garantia_atendimento` | Fonte bruta ausente ou dbt model dependente de dado não carregado |
| outros | `api_iap` | Fonte bruta ausente ou dbt model dependente de dado não carregado |
| outros | `api_ntrp_area_comercializacao` | Fonte bruta ausente ou dbt model dependente de dado não carregado |
| outros | `api_ntrp_vcm_faixa_etaria` | Fonte bruta ausente ou dbt model dependente de dado não carregado |
| outros | `api_peona_sus` | Fonte bruta ausente ou dbt model dependente de dado não carregado |
| outros | `api_pfa` | Fonte bruta ausente ou dbt model dependente de dado não carregado |
| outros | `api_prata_tiss_procedimento` | Fonte TISS não carregada em bruto_ans |
| outros | `api_prata_vda` | Fonte VDA não carregada em bruto_ans |
| outros | `api_programa_qualificacao_institucional` | Fonte bruta ausente ou dbt model dependente de dado não carregado |
| outros | `api_promoprev` | Fonte bruta ausente ou dbt model dependente de dado não carregado |
| outros | `api_reajuste_agrupamento` | Fonte bruta ausente ou dbt model dependente de dado não carregado |
| outros | `api_ressarcimento_beneficiario_abi` | Fonte ressarcimento não carregada em bruto_ans |
| outros | `api_ressarcimento_cobranca_arrecadacao` | Fonte ressarcimento não carregada em bruto_ans |
| outros | `api_ressarcimento_hc` | Fonte ressarcimento não carregada em bruto_ans |
| outros | `api_ressarcimento_indice_pagamento` | Fonte ressarcimento não carregada em bruto_ans |
| outros | `api_rn623_lista_trimestral` | Fonte bruta ausente ou dbt model dependente de dado não carregado |
| outros | `api_sinistralidade_procedimento` | Fonte bruta ausente ou dbt model dependente de dado não carregado |
| outros | `api_vazio_assistencial` | Fonte bruta ausente ou dbt model dependente de dado não carregado |
| premium/MDM | `api_premium_contrato_validado` | Schema premium/MDM não implementado nesta fase |
| premium/MDM | `api_premium_subfatura_validada` | Schema premium/MDM não implementado nesta fase |
| produtos/planos | `api_painel_precificacao` | painel_precificacao: registro_ans=NULL em todos os registros brutos |
| produtos/planos | `api_plano_servico_opcional` | Fonte bruta ausente ou dbt model dependente de dado não carregado |
| produtos/planos | `api_premium_tiss_procedimento_tuss_validado` | Fonte TISS não carregada em bruto_ans |
| produtos/planos | `api_produto_prestador_hospitalar` | produto_prestador: registro_ans=NULL em todos os registros brutos |
| produtos/planos | `api_tiss_plano_mes` | Fonte TISS não carregada em bruto_ans |
| rede prestadora | `api_alteracao_rede_hospitalar` | Fonte rede assistencial não carregada em bruto_ans |
| rede prestadora | `api_bronze_rede_assistencial` | Fonte rede assistencial não carregada em bruto_ans |
| rede prestadora | `api_cnes_rede_gap` | Fonte CNES não carregada em bruto_ans |
| rede prestadora | `api_prata_cnes_rede_gap` | Fonte CNES não carregada em bruto_ans |
| rede prestadora | `api_prata_rede_assistencial` | Fonte rede assistencial não carregada em bruto_ans |
| rede prestadora | `api_premium_cnes_estabelecimento_validado` | Fonte CNES não carregada em bruto_ans |
| rede prestadora | `api_premium_mdm_prestador` | produto_prestador: registro_ans=NULL em todos os registros brutos |
| rede prestadora | `api_prestador_acreditado` | produto_prestador: registro_ans=NULL em todos os registros brutos |
| rede prestadora | `api_rede_assistencial` | Fonte rede assistencial não carregada em bruto_ans |
| regulatório | `api_taxa_cobertura_plano` | Fonte bruta ausente ou dbt model dependente de dado não carregado |

---

## `consumo_ans` — Tabelas PRONTAS

**17 tabelas populadas** com 812,778 registros.

| Tabela | Registros | Período Coberto | Períodos Distintos |
|--------|-----------|-----------------|-------------------|
| `consumo_beneficiarios_municipio_mes` | 646 | 202603 → 202603 | 1 |
| `consumo_beneficiarios_operadora_mes` | 757 | 202603 → 202603 | 1 |
| `consumo_financeiro_operadora_trimestre` | 10,978 | 1T2023 → 4T2025 | 13 |
| `consumo_glosa_operadora_mensal` | 4,170 | 202501 → 202501 | 1 |
| `consumo_historico_plano` | 163,567 | 202505 → 202505 | 1 |
| `consumo_idss` | 13,072 | sem coluna temporal | — |
| `consumo_igr` | 136,908 | 201501 → 202604 | 136 |
| `consumo_nip` | 53,637 | 201101 → 202012 | 120 |
| `consumo_operadora_360` | 757 | 202603 → 202603 | 1 |
| `consumo_oportunidade_municipio` | 646 | 202603 → 202603 | 1 |
| `consumo_produto_plano` | 163,661 | 202605 → 202605 | 1 |
| `consumo_prudencial_operadora_trimestral` | 11,216 | 1T2024 → 4T2025 | 10 |
| `consumo_regime_especial_operadora_trimestral` | 117 | 1T2002 → 1T2025 | 20 |
| `consumo_regulatorio_operadora_trimestre` | 161,173 | 201101 → 202604 | 184 |
| `consumo_score_operadora_mes` | 757 | 202603 → 202603 | 1 |
| `consumo_taxa_resolutividade_operadora_trimestral` | 26,062 | 201501 → 201910 | 58 |
| `consumo_tuss_procedimento_vigente` | 64,654 | sem coluna temporal | — |

---

## `consumo_ans` — Tabelas VAZIAS

| Tabela | Causa Provável |
|--------|----------------|
| `consumo_beneficiarios_cobertura_municipio` | SIB beneficiário não materializado via dbt |
| `consumo_plano_servico_opcional` | Fonte bruta ausente ou dbt model dependente de dado não carregado |
| `consumo_precificacao_plano` | painel_precificacao: registro_ans=NULL em todos os registros brutos |
| `consumo_rede_acreditacao` | Fonte rede assistencial não carregada em bruto_ans |
| `consumo_rede_assistencial_municipio` | Fonte rede assistencial não carregada em bruto_ans |
| `consumo_regulatorio_complementar_operadora` | Fonte bruta ausente ou dbt model dependente de dado não carregado |
| `consumo_ressarcimento_sus_operadora` | Fonte ressarcimento não carregada em bruto_ans |
| `consumo_sip_assistencial_operadora` | Fonte SIB/SIP não carregada ou registro_ans=NULL no bruto |
| `consumo_tiss_utilizacao_operadora_mes` | Fonte TISS não carregada em bruto_ans |

---

## Cobertura por Domínio (api_ans)

| Domínio | Prontas | Vazias | Status |
|---------|---------|--------|--------|
| operadora | 18 | 12 | ⚠️ Parcial |
| score/ranking | 6 | 0 | ✅ Completo |
| regulatório | 8 | 1 | ⚠️ Parcial |
| financeiro | 3 | 2 | ⚠️ Parcial |
| mercado/beneficiários | 4 | 3 | ⚠️ Parcial |
| produtos/planos | 4 | 5 | ⚠️ Parcial |
| rede prestadora | 0 | 9 | ❌ Nenhuma pronta |
| premium/MDM | 1 | 2 | ⚠️ Parcial |
| outros | 1 | 22 | ⚠️ Parcial |

---

## Próximos Passos para Completar a Cobertura

1. **Carregar CADOP** (`make dag-run-real-cadop COMPETENCIA=202605`) → desbloqueia modelos de operadora enriquecida
2. **Corrigir `registro_ans=NULL`** em `painel_precificacao`, `produto_prestador_hospitalar`, `sip_mapa_assistencial` na ingestion → 75M registros desbloqueados
3. **Carregar CNES** → desbloqueia tabelas de rede prestadora
4. **Carregar FIP/VDA** → desbloqueia tabelas financeiras (`financeiro_operadora`, `glosa_vda`)
5. **Carregar TISS** → desbloqueia tabelas de procedimentos TISS
6. **Carregar SIB completo** (beneficiários) → desbloqueia `fat_beneficiario_operadora`
