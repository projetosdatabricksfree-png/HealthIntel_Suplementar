# Relatório Tabela a Tabela — HealthIntel PostgreSQL

**Gerado em:** 2026-05-17 23:34 UTC  
**Banco:** PostgreSQL 16 · Docker `healthintel_postgres`

---

## Resumo Executivo

| Métrica | Valor |
|---------|-------|
| **Total de Tabelas** | 455 |
| **Preenchidas** | 199 |
| **Vazias** | 256 |
| **Com Erro** | 0 |
| **Total de Registros (estimado+real)** | 141,742,830 |
| **Schemas** | 14 |

---

## Sumário por Schema

| Schema | Camada | Tabelas | Preenchidas | Vazias | Registros | Tamanho |
|--------|--------|---------|-------------|--------|-----------|---------|
| **api_ans** | serving/API | 101 | 45 | 56 | 11,770,796 | 273.1 MB |
| **bruto_ans** | bronze | 102 | 29 | 73 | 127,633,077 | 32.1 GB |
| **bruto_cliente** | bronze cliente | 2 | 0 | 2 | 0 | 80.0 KB |
| **consumo_ans** | serving/cliente | 26 | 17 | 9 | 812,778 | 108.0 MB |
| **consumo_premium_ans** | premium | 11 | 4 | 7 | 5,366 | 1.1 MB |
| **mdm_ans** | MDM público | 9 | 2 | 7 | 2,214 | 488.0 KB |
| **mdm_privado** | MDM privado | 8 | 0 | 8 | 0 | 64.0 KB |
| **nucleo_ans** | gold/núcleo | 39 | 28 | 11 | 755,050 | 157.0 MB |
| **plataforma** | governança | 38 | 22 | 16 | 16,805 | 9.0 MB |
| **public** | sistema | 42 | 22 | 20 | 16,725 | 11.0 MB |
| **quality_ans** | qualidade | 5 | 2 | 3 | 2,214 | 552.0 KB |
| **ref_ans** | referência | 11 | 11 | 0 | 12,831 | 1.2 MB |
| **stg_ans** | staging | 59 | 17 | 42 | 714,974 | 0.0 B |
| **stg_cliente** | staging cliente | 2 | 0 | 2 | 0 | 0.0 B |

---

## Schema: `api_ans` — serving/API

| Tabela | Status | Registros | Tipo Count | Col. Temporal | Período (min→max) | Períodos | Tamanho |
|--------|--------|-----------|-----------|---------------|-------------------|----------|---------|
| `api_bronze_cadop` | ✅ preenchida | 1,107 | real | competencia | 202605 → 202605 | 1 | 0.0 B |
| `api_bronze_diops` | ✅ preenchida | 10,232,252 | real | trimestre | 1T2023 → 4T2025 | 13 | 0.0 B |
| `api_bronze_glosa` | ✅ preenchida | 4,170 | real | competencia | 202501 → 202501 | 1 | 0.0 B |
| `api_bronze_idss` | ✅ preenchida | 13,072 | real | — | — | — | 0.0 B |
| `api_bronze_igr` | ✅ preenchida | 150,501 | real | trimestre | 201501 → 202604 | 136 | 0.0 B |
| `api_bronze_nip` | ✅ preenchida | 53,637 | real | trimestre | 201101 → 202012 | 120 | 0.0 B |
| `api_bronze_sib_municipio` | ✅ preenchida | 59,892 | real | competencia | 202603 → 202603 | 1 | 0.0 B |
| `api_bronze_sib_operadora` | ✅ preenchida | 803 | real | competencia | 202603 → 202603 | 1 | 0.0 B |
| `api_glosa_operadora_mensal` | ✅ preenchida | 4,170 | real | competencia | 202501 → 202501 | 1 | 488.0 KB |
| `api_historico_plano` | ✅ preenchida | 163,567 | real | competencia | 202505 → 202505 | 1 | 14.0 MB |
| `api_market_share_mensal` | ✅ preenchida | 59,197 | real | competencia | 202603 → 202603 | 1 | 15.5 MB |
| `api_operadora` | ✅ preenchida | 1,107 | real | — | — | — | 328.0 KB |
| `api_oportunidade_municipio_mensal` | ✅ preenchida | 646 | real | competencia | 202603 → 202603 | 1 | 136.0 KB |
| `api_oportunidade_v2_municipio_mensal` | ✅ preenchida | 646 | real | competencia | 202603 → 202603 | 1 | 264.0 KB |
| `api_prata_cadop` | ✅ preenchida | 1,107 | real | — | — | — | 272.0 KB |
| `api_prata_diops` | ✅ preenchida | 11,563 | real | trimestre | 1T2023 → 4T2025 | 13 | 1.4 MB |
| `api_prata_financeiro_periodo` | ✅ preenchida | 10,978 | real | trimestre | 1T2023 → 4T2025 | 13 | 2.8 MB |
| `api_prata_glosa` | ✅ preenchida | 4,170 | real | competencia | 202501 → 202501 | 1 | 712.0 KB |
| `api_prata_idss` | ✅ preenchida | 13,072 | real | — | — | — | 2.5 MB |
| `api_prata_igr` | ✅ preenchida | 136,908 | real | trimestre | 201501 → 202604 | 136 | 22.4 MB |
| `api_prata_municipio_metrica` | ✅ preenchida | 59,197 | real | competencia | 202603 → 202603 | 1 | 8.5 MB |
| `api_prata_nip` | ✅ preenchida | 53,637 | real | trimestre | 201101 → 202012 | 120 | 11.8 MB |
| `api_prata_operadora_enriquecida` | ✅ preenchida | 757 | real | competencia | 202603 → 202603 | 1 | 136.0 KB |
| `api_prata_sib_municipio` | ✅ preenchida | 59,892 | real | competencia | 202603 → 202603 | 1 | 7.5 MB |
| `api_prata_sib_operadora` | ✅ preenchida | 803 | real | competencia | 202603 → 202603 | 1 | 136.0 KB |
| `api_premium_mdm_operadora` | ✅ preenchida | 1,107 | real | — | — | — | 296.0 KB |
| `api_premium_operadora_360_validado` | ✅ preenchida | 757 | real | competencia | 202603 → 202603 | 1 | 264.0 KB |
| `api_premium_quality_dataset` | ✅ preenchida | 2 | real | — | — | — | 16.0 KB |
| `api_premium_tuss_procedimento` | ✅ preenchida | 3,500 | real | — | — | — | 560.0 KB |
| `api_produto_plano` | ✅ preenchida | 163,661 | real | competencia | 202605 → 202605 | 1 | 38.0 MB |
| `api_prudencial_operadora_trimestral` | ✅ preenchida | 11,216 | real | trimestre | 1T2024 → 4T2025 | 10 | 1.3 MB |
| `api_quadro_auxiliar_corresponsabilidade` | ✅ preenchida | 1,032 | real | competencia | 202505 → 202505 | 1 | 208.0 KB |
| `api_ranking_composto_mensal` | ✅ preenchida | 757 | real | — | — | — | 360.0 KB |
| `api_ranking_crescimento` | ✅ preenchida | 757 | real | competencia | 202603 → 202603 | 1 | 136.0 KB |
| `api_ranking_oportunidade` | ✅ preenchida | 646 | real | competencia | 202603 → 202603 | 1 | 136.0 KB |
| `api_ranking_score` | ✅ preenchida | 757 | real | competencia | 202603 → 202603 | 1 | 136.0 KB |
| `api_regime_especial_operadora` | ✅ preenchida | 53 | real | trimestre | 1T2003 → 1T2025 | 15 | 24.0 KB |
| `api_regime_especial_operadora_trimestral` | ✅ preenchida | 117 | real | trimestre | 1T2002 → 1T2025 | 20 | 40.0 KB |
| `api_regulatorio_operadora_trimestral` | ✅ preenchida | 125,287 | real | trimestre | 201101 → 202604 | 184 | 27.7 MB |
| `api_score_operadora_mensal` | ✅ preenchida | 757 | real | competencia | 202603 → 202603 | 1 | 344.0 KB |
| `api_score_regulatorio_operadora_mensal` | ✅ preenchida | 136,032 | real | competencia | 1T2003 → 4T2025 | 207 | 31.0 MB |
| `api_score_v2_operadora_mensal` | ✅ preenchida | 136,034 | real | competencia | 1T2003 → 4T2025 | 207 | 67.5 MB |
| `api_score_v3_operadora_mensal` | ✅ preenchida | 757 | real | — | — | — | 360.0 KB |
| `api_taxa_resolutividade_operadora_trimestral` | ✅ preenchida | 26,062 | real | trimestre | 201501 → 201910 | 58 | 4.0 MB |
| `api_tuss_procedimento_vigente` | ✅ preenchida | 64,654 | real | — | — | — | 11.0 MB |
| `api_alteracao_rede_hospitalar` | ⬜ vazia | 0 | real | competencia | — | — | 8.0 KB |
| | | | | | *Fonte rede assistencial não carregada em bruto_ans* | | |
| `api_beneficiario_informacao_consolidada` | ⬜ vazia | 0 | real | competencia | — | — | 8.0 KB |
| | | | | | *SIB beneficiário não materializado via dbt* | | |
| `api_beneficiario_regiao_geografica` | ⬜ vazia | 0 | real | competencia | — | — | 8.0 KB |
| | | | | | *SIB beneficiário não materializado via dbt* | | |
| `api_bronze_fip` | ⬜ vazia | 0 | real | trimestre | — | — | 0.0 B |
| | | | | | *Fonte FIP não carregada em bruto_ans* | | |
| `api_bronze_rede_assistencial` | ⬜ vazia | 0 | real | competencia | — | — | 0.0 B |
| | | | | | *Fonte rede assistencial não carregada em bruto_ans* | | |
| `api_bronze_vda` | ⬜ vazia | 0 | real | competencia | — | — | 0.0 B |
| | | | | | *Fonte VDA não carregada em bruto_ans* | | |
| `api_cnes_municipio` | ⬜ vazia | 0 | real | competencia | — | — | 40.0 KB |
| | | | | | *Fonte CNES não carregada em bruto_ans* | | |
| `api_cnes_rede_gap` | ⬜ vazia | 0 | real | competencia | — | — | 32.0 KB |
| | | | | | *Fonte CNES não carregada em bruto_ans* | | |
| `api_faixa_preco` | ⬜ vazia | 0 | real | competencia | — | — | 8.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `api_financeiro_operadora_mensal` | ⬜ vazia | 0 | real | competencia | — | — | 8.0 KB |
| | | | | | *fat_vda_operadora: fonte VDA não carregada em bruto_ans* | | |
| `api_garantia_atendimento` | ⬜ vazia | 0 | real | competencia | — | — | 8.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `api_iap` | ⬜ vazia | 0 | real | competencia | — | — | 8.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `api_ntrp_area_comercializacao` | ⬜ vazia | 0 | real | competencia | — | — | 8.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `api_ntrp_vcm_faixa_etaria` | ⬜ vazia | 0 | real | competencia | — | — | 8.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `api_operadora_acreditada` | ⬜ vazia | 0 | real | data_acreditacao | — | — | 8.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `api_operadora_cancelada` | ⬜ vazia | 0 | real | data_cancelamento | — | — | 8.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `api_operadora_prestador_nao_hospitalar` | ⬜ vazia | 0 | real | competencia | — | — | 8.0 KB |
| | | | | | *produto_prestador: registro_ans=NULL em todos os registros brutos* | | |
| `api_painel_precificacao` | ⬜ vazia | 0 | real | competencia | — | — | 8.0 KB |
| | | | | | *painel_precificacao: registro_ans=NULL em todos os registros brutos* | | |
| `api_penalidade_operadora` | ⬜ vazia | 0 | real | competencia | — | — | 8.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `api_peona_sus` | ⬜ vazia | 0 | real | competencia | — | — | 8.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `api_pfa` | ⬜ vazia | 0 | real | competencia | — | — | 8.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `api_plano_servico_opcional` | ⬜ vazia | 0 | real | competencia | — | — | 24.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `api_portabilidade_operadora_mensal` | ⬜ vazia | 0 | real | competencia | — | — | 24.0 KB |
| | | | | | *Fonte portabilidade não carregada em bruto_ans* | | |
| `api_prata_cnes_municipio` | ⬜ vazia | 0 | real | competencia | — | — | 32.0 KB |
| | | | | | *Fonte CNES não carregada em bruto_ans* | | |
| `api_prata_cnes_rede_gap` | ⬜ vazia | 0 | real | competencia | — | — | 32.0 KB |
| | | | | | *Fonte CNES não carregada em bruto_ans* | | |
| `api_prata_fip` | ⬜ vazia | 0 | real | trimestre | — | — | 8.0 KB |
| | | | | | *Fonte FIP não carregada em bruto_ans* | | |
| `api_prata_rede_assistencial` | ⬜ vazia | 0 | real | competencia | — | — | 32.0 KB |
| | | | | | *Fonte rede assistencial não carregada em bruto_ans* | | |
| `api_prata_tiss_procedimento` | ⬜ vazia | 0 | real | trimestre | — | — | 40.0 KB |
| | | | | | *Fonte TISS não carregada em bruto_ans* | | |
| `api_prata_vda` | ⬜ vazia | 0 | real | competencia | — | — | 24.0 KB |
| | | | | | *Fonte VDA não carregada em bruto_ans* | | |
| `api_premium_cnes_estabelecimento_validado` | ⬜ vazia | 0 | real | competencia | — | — | 8.0 KB |
| | | | | | *Fonte CNES não carregada em bruto_ans* | | |
| `api_premium_contrato_validado` | ⬜ vazia | 0 | real | — | — | — | 8.0 KB |
| | | | | | *Schema premium/MDM não implementado nesta fase* | | |
| `api_premium_mdm_prestador` | ⬜ vazia | 0 | real | — | — | — | 8.0 KB |
| | | | | | *produto_prestador: registro_ans=NULL em todos os registros brutos* | | |
| `api_premium_subfatura_validada` | ⬜ vazia | 0 | real | competencia | — | — | 8.0 KB |
| | | | | | *Schema premium/MDM não implementado nesta fase* | | |
| `api_premium_tiss_procedimento_tuss_validado` | ⬜ vazia | 0 | real | trimestre | — | — | 8.0 KB |
| | | | | | *Fonte TISS não carregada em bruto_ans* | | |
| `api_prestador_acreditado` | ⬜ vazia | 0 | real | data_acreditacao | — | — | 8.0 KB |
| | | | | | *produto_prestador: registro_ans=NULL em todos os registros brutos* | | |
| `api_produto_prestador_hospitalar` | ⬜ vazia | 0 | real | competencia | — | — | 8.0 KB |
| | | | | | *produto_prestador: registro_ans=NULL em todos os registros brutos* | | |
| `api_programa_qualificacao_institucional` | ⬜ vazia | 0 | real | competencia | — | — | 8.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `api_promoprev` | ⬜ vazia | 0 | real | competencia | — | — | 8.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `api_reajuste_agrupamento` | ⬜ vazia | 0 | real | competencia | — | — | 8.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `api_rede_assistencial` | ⬜ vazia | 0 | real | competencia | — | — | 32.0 KB |
| | | | | | *Fonte rede assistencial não carregada em bruto_ans* | | |
| `api_ressarcimento_beneficiario_abi` | ⬜ vazia | 0 | real | competencia | — | — | 8.0 KB |
| | | | | | *Fonte ressarcimento não carregada em bruto_ans* | | |
| `api_ressarcimento_cobranca_arrecadacao` | ⬜ vazia | 0 | real | competencia | — | — | 8.0 KB |
| | | | | | *Fonte ressarcimento não carregada em bruto_ans* | | |
| `api_ressarcimento_hc` | ⬜ vazia | 0 | real | competencia | — | — | 8.0 KB |
| | | | | | *Fonte ressarcimento não carregada em bruto_ans* | | |
| `api_ressarcimento_indice_pagamento` | ⬜ vazia | 0 | real | competencia | — | — | 8.0 KB |
| | | | | | *Fonte ressarcimento não carregada em bruto_ans* | | |
| `api_ressarcimento_sus_operadora_plano` | ⬜ vazia | 0 | real | competencia | — | — | 8.0 KB |
| | | | | | *Fonte ressarcimento não carregada em bruto_ans* | | |
| `api_rn623_lista_trimestral` | ⬜ vazia | 0 | real | trimestre | — | — | 8.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `api_rpc_operadora_mes` | ⬜ vazia | 0 | real | competencia | — | — | 8.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `api_sinistralidade_procedimento` | ⬜ vazia | 0 | real | trimestre | — | — | 8.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `api_sip_assistencial_operadora` | ⬜ vazia | 0 | real | competencia | — | — | 32.0 KB |
| | | | | | *Fonte SIB/SIP não carregada ou registro_ans=NULL no bruto* | | |
| `api_taxa_cobertura_plano` | ⬜ vazia | 0 | real | competencia | — | — | 8.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `api_tiss_ambulatorial_operadora_mes` | ⬜ vazia | 0 | real | competencia | — | — | 8.0 KB |
| | | | | | *Fonte TISS não carregada em bruto_ans* | | |
| `api_tiss_hospitalar_operadora_mes` | ⬜ vazia | 0 | real | competencia | — | — | 8.0 KB |
| | | | | | *Fonte TISS não carregada em bruto_ans* | | |
| `api_tiss_operadora_trimestral` | ⬜ vazia | 0 | real | trimestre | — | — | 8.0 KB |
| | | | | | *Fonte TISS não carregada em bruto_ans* | | |
| `api_tiss_plano_mes` | ⬜ vazia | 0 | real | competencia | — | — | 8.0 KB |
| | | | | | *Fonte TISS não carregada em bruto_ans* | | |
| `api_valor_comercial_medio_municipio` | ⬜ vazia | 0 | real | competencia | — | — | 8.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `api_vazio_assistencial` | ⬜ vazia | 0 | real | competencia | — | — | 32.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |

## Schema: `bruto_ans` — bronze

| Tabela | Status | Registros | Tipo Count | Col. Temporal | Período (min→max) | Períodos | Tamanho |
|--------|--------|-----------|-----------|---------------|-------------------|----------|---------|
| `ans_arquivo_generico` | ✅ preenchida | 7 | real | data_ingestao | 2026-05-13 19:51:48.58963+00 → 2026-05-14 04:58:26.617089+00 | 7 | 64.0 KB |
| `cadop` | ✅ preenchida | 1,107 | real | competencia | 202605 → 202605 | 1 | 624.0 KB |
| `diops_operadora_trimestral` | ✅ preenchida | 10,232,252 | real | trimestre | 1T2023 → 4T2025 | 13 | 0.0 B |
| `diops_operadora_trimestral_default` | ✅ preenchida | 10,191,724 | estimado | trimestre | 1T2023 → 4T2025 | 13 | 3.5 GB |
| `glosa_operadora_mensal` | ✅ preenchida | 4,170 | real | competencia | 202501 → 202501 | 1 | 0.0 B |
| `glosa_operadora_mensal_2025` | ✅ preenchida | 4,170 | real | competencia | 202501 → 202501 | 1 | 2.0 MB |
| `historico_plano` | ✅ preenchida | 347,715 | real | competencia | 202505 → 202505 | 1 | 109.7 MB |
| `idss` | ✅ preenchida | 13,072 | real | — | — | — | 6.3 MB |
| `igr_operadora_trimestral` | ✅ preenchida | 150,501 | real | trimestre | 201501 → 202604 | 136 | 65.9 MB |
| `nip_operadora_trimestral` | ✅ preenchida | 53,637 | real | trimestre | 201101 → 202012 | 120 | 26.0 MB |
| `operadora_prestador_nao_hospitalar` | ✅ preenchida | 31,959,000 | estimado | competencia | 202605 → 202605 | 1 | 8.5 GB |
| `painel_precificacao` | ✅ preenchida | 30,149,562 | estimado | competencia | 202504 → 202504 | 1 | 7.8 GB |
| `plano_servico_opcional` | ✅ preenchida | 32,314 | real | competencia | 202505 → 202505 | 1 | 11.2 MB |
| `produto_caracteristica` | ✅ preenchida | 163,969 | real | competencia | 202605 → 202605 | 1 | 78.2 MB |
| `produto_prestador_hospitalar` | ✅ preenchida | 42,907,740 | estimado | competencia | 202605 → 202605 | 1 | 11.4 GB |
| `produto_tabela_auxiliar` | ✅ preenchida | 877,472 | real | competencia | 202505 → 202505 | 1 | 355.8 MB |
| `prudencial_operadora_trimestral` | ✅ preenchida | 11,216 | real | trimestre | 1T2024 → 4T2025 | 10 | 0.0 B |
| `prudencial_operadora_trimestral_default` | ✅ preenchida | 11,216 | real | trimestre | 1T2024 → 4T2025 | 10 | 5.1 MB |
| `quadro_auxiliar_corresponsabilidade` | ✅ preenchida | 11,081 | real | competencia | 202505 → 202505 | 1 | 4.5 MB |
| `regime_especial_operadora_trimestral` | ✅ preenchida | 118 | real | trimestre | 1T2002 → 1T2025 | 20 | 0.0 B |
| `regime_especial_operadora_trimestral_default` | ✅ preenchida | 118 | real | trimestre | 1T2002 → 1T2025 | 20 | 152.0 KB |
| `sib_beneficiario_municipio` | ✅ preenchida | 59,892 | real | competencia | 202603 → 202603 | 1 | 0.0 B |
| `sib_beneficiario_municipio_2026` | ✅ preenchida | 59,892 | real | competencia | 202603 → 202603 | 1 | 25.8 MB |
| `sib_beneficiario_operadora` | ✅ preenchida | 803 | real | competencia | 202603 → 202603 | 1 | 0.0 B |
| `sib_beneficiario_operadora_2026` | ✅ preenchida | 803 | real | competencia | 202603 → 202603 | 1 | 408.0 KB |
| `sip_mapa_assistencial` | ✅ preenchida | 133,392 | real | competencia | 202001 → 202410 | 20 | 42.4 MB |
| `taxa_resolutividade_operadora_trimestral` | ✅ preenchida | 63,366 | real | trimestre | 201501 → 201910 | 58 | 0.0 B |
| `taxa_resolutividade_operadora_trimestral_default` | ✅ preenchida | 63,366 | real | trimestre | 201501 → 201910 | 58 | 28.5 MB |
| `tuss_terminologia_oficial` | ✅ preenchida | 129,402 | real | — | — | — | 44.5 MB |
| `ans_linha_generica` | ⬜ vazia | 0 | real | data_ingestao | — | — | 32.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `beneficiario_informacao_consolidada` | ⬜ vazia | 0 | real | competencia | — | — | 24.0 KB |
| | | | | | *SIB beneficiário não materializado via dbt* | | |
| `beneficiario_regiao_geografica` | ⬜ vazia | 0 | real | competencia | — | — | 16.0 KB |
| | | | | | *SIB beneficiário não materializado via dbt* | | |
| `cadop_quarentena` | ⬜ vazia | 0 | real | — | — | — | 16.0 KB |
| | | | | | *CADOP não carregado em bruto_ans* | | |
| `cnes_estabelecimento` | ⬜ vazia | 0 | real | competencia | — | — | 0.0 B |
| | | | | | *Fonte CNES não carregada em bruto_ans* | | |
| `cnes_estabelecimento_default` | ⬜ vazia | 0 | real | competencia | — | — | 32.0 KB |
| | | | | | *Fonte CNES não carregada em bruto_ans* | | |
| `depara_sip_tuss` | ⬜ vazia | 0 | real | — | — | — | 32.0 KB |
| | | | | | *Fonte SIB/SIP não carregada ou registro_ans=NULL no bruto* | | |
| `diops_quarentena` | ⬜ vazia | 0 | real | — | — | — | 16.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `faixa_preco` | ⬜ vazia | 0 | real | competencia | — | — | 16.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `fip_operadora_trimestral` | ⬜ vazia | 0 | real | trimestre | — | — | 0.0 B |
| | | | | | *Fonte FIP não carregada em bruto_ans* | | |
| `fip_operadora_trimestral_default` | ⬜ vazia | 0 | real | trimestre | — | — | 32.0 KB |
| | | | | | *Fonte FIP não carregada em bruto_ans* | | |
| `fip_quarentena` | ⬜ vazia | 0 | real | — | — | — | 16.0 KB |
| | | | | | *Fonte FIP não carregada em bruto_ans* | | |
| `glosa_operadora_mensal_2026` | ⬜ vazia | 0 | real | competencia | — | — | 40.0 KB |
| | | | | | *VDA/glosa: fonte VDA não carregada em bruto_ans* | | |
| `glosa_operadora_mensal_2027` | ⬜ vazia | 0 | real | competencia | — | — | 40.0 KB |
| | | | | | *VDA/glosa: fonte VDA não carregada em bruto_ans* | | |
| `glosa_operadora_mensal_default` | ⬜ vazia | 0 | real | competencia | — | — | 40.0 KB |
| | | | | | *VDA/glosa: fonte VDA não carregada em bruto_ans* | | |
| `glosa_quarentena` | ⬜ vazia | 0 | real | — | — | — | 16.0 KB |
| | | | | | *VDA/glosa: fonte VDA não carregada em bruto_ans* | | |
| `iap` | ⬜ vazia | 0 | real | competencia | — | — | 16.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `idss_quarentena` | ⬜ vazia | 0 | real | — | — | — | 16.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `igr_quarentena` | ⬜ vazia | 0 | real | — | — | — | 16.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `monitoramento_garantia_atendimento` | ⬜ vazia | 0 | real | competencia | — | — | 16.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `nip_quarentena` | ⬜ vazia | 0 | real | — | — | — | 16.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `ntrp_area_comercializacao` | ⬜ vazia | 0 | real | competencia | — | — | 24.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `ntrp_vcm_faixa_etaria` | ⬜ vazia | 0 | real | competencia | — | — | 16.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `operadora_acreditada` | ⬜ vazia | 0 | real | data_validade | — | — | 16.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `operadora_cancelada` | ⬜ vazia | 0 | real | data_cancelamento | — | — | 24.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `penalidade_operadora` | ⬜ vazia | 0 | real | competencia | — | — | 24.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `peona_sus` | ⬜ vazia | 0 | real | competencia | — | — | 16.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `percentual_reajuste_agrupamento` | ⬜ vazia | 0 | real | competencia | — | — | 16.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `pfa` | ⬜ vazia | 0 | real | competencia | — | — | 16.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `portabilidade_operadora_mensal` | ⬜ vazia | 0 | real | competencia | — | — | 0.0 B |
| | | | | | *Fonte portabilidade não carregada em bruto_ans* | | |
| `portabilidade_operadora_mensal_default` | ⬜ vazia | 0 | real | competencia | — | — | 32.0 KB |
| | | | | | *Fonte portabilidade não carregada em bruto_ans* | | |
| `prestador_acreditado` | ⬜ vazia | 0 | real | data_validade | — | — | 24.0 KB |
| | | | | | *produto_prestador: registro_ans=NULL em todos os registros brutos* | | |
| `prestador_cadastral` | ⬜ vazia | 0 | real | — | — | — | 32.0 KB |
| | | | | | *produto_prestador: registro_ans=NULL em todos os registros brutos* | | |
| `prestador_cadastral_snapshot_anterior` | ⬜ vazia | 0 | real | — | — | — | 16.0 KB |
| | | | | | *produto_prestador: registro_ans=NULL em todos os registros brutos* | | |
| `programa_qualificacao_institucional` | ⬜ vazia | 0 | real | competencia | — | — | 16.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `promoprev` | ⬜ vazia | 0 | real | competencia | — | — | 16.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `qualiss` | ⬜ vazia | 0 | real | — | — | — | 32.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `qualiss_snapshot_anterior` | ⬜ vazia | 0 | real | — | — | — | 16.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `rede_assistencial_quarentena` | ⬜ vazia | 0 | real | — | — | — | 16.0 KB |
| | | | | | *Fonte rede assistencial não carregada em bruto_ans* | | |
| `rede_prestador_municipio` | ⬜ vazia | 0 | real | competencia | — | — | 0.0 B |
| | | | | | *Fonte rede assistencial não carregada em bruto_ans* | | |
| `rede_prestador_municipio_default` | ⬜ vazia | 0 | real | competencia | — | — | 24.0 KB |
| | | | | | *Fonte rede assistencial não carregada em bruto_ans* | | |
| `ressarcimento_beneficiario_abi` | ⬜ vazia | 0 | real | competencia | — | — | 24.0 KB |
| | | | | | *Fonte ressarcimento não carregada em bruto_ans* | | |
| `ressarcimento_cobranca_arrecadacao` | ⬜ vazia | 0 | real | competencia | — | — | 16.0 KB |
| | | | | | *Fonte ressarcimento não carregada em bruto_ans* | | |
| `ressarcimento_hc` | ⬜ vazia | 0 | real | competencia | — | — | 24.0 KB |
| | | | | | *Fonte ressarcimento não carregada em bruto_ans* | | |
| `ressarcimento_indice_pagamento` | ⬜ vazia | 0 | real | competencia | — | — | 16.0 KB |
| | | | | | *Fonte ressarcimento não carregada em bruto_ans* | | |
| `ressarcimento_sus_operadora_plano` | ⬜ vazia | 0 | real | competencia | — | — | 16.0 KB |
| | | | | | *Fonte ressarcimento não carregada em bruto_ans* | | |
| `rn623_lista_operadora_trimestral` | ⬜ vazia | 0 | real | trimestre | — | — | 24.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `rol_procedimento` | ⬜ vazia | 0 | real | — | — | — | 32.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `rpc` | ⬜ vazia | 0 | real | competencia | — | — | 0.0 B |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `rpc_default` | ⬜ vazia | 0 | real | competencia | — | — | 16.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `sib_beneficiario_municipio_2025` | ⬜ vazia | 0 | real | competencia | — | — | 24.0 KB |
| | | | | | *SIB beneficiário não materializado via dbt* | | |
| `sib_beneficiario_municipio_2027` | ⬜ vazia | 0 | real | competencia | — | — | 24.0 KB |
| | | | | | *SIB beneficiário não materializado via dbt* | | |
| `sib_beneficiario_municipio_default` | ⬜ vazia | 0 | real | competencia | — | — | 24.0 KB |
| | | | | | *SIB beneficiário não materializado via dbt* | | |
| `sib_beneficiario_operadora_2025` | ⬜ vazia | 0 | real | competencia | — | — | 24.0 KB |
| | | | | | *SIB beneficiário não materializado via dbt* | | |
| `sib_beneficiario_operadora_2027` | ⬜ vazia | 0 | real | competencia | — | — | 24.0 KB |
| | | | | | *SIB beneficiário não materializado via dbt* | | |
| `sib_beneficiario_operadora_default` | ⬜ vazia | 0 | real | competencia | — | — | 48.0 KB |
| | | | | | *SIB beneficiário não materializado via dbt* | | |
| `sib_municipio_quarentena` | ⬜ vazia | 0 | real | — | — | — | 16.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `sib_operadora_quarentena` | ⬜ vazia | 0 | real | — | — | — | 16.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `solicitacao_alteracao_rede_hospitalar` | ⬜ vazia | 0 | real | competencia | — | — | 24.0 KB |
| | | | | | *Fonte rede assistencial não carregada em bruto_ans* | | |
| `taxa_cobertura_plano` | ⬜ vazia | 0 | real | competencia | — | — | 24.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `tiss_ambulatorial` | ⬜ vazia | 0 | real | competencia | — | — | 0.0 B |
| | | | | | *Fonte TISS não carregada em bruto_ans* | | |
| `tiss_ambulatorial_default` | ⬜ vazia | 0 | real | competencia | — | — | 16.0 KB |
| | | | | | *Fonte TISS não carregada em bruto_ans* | | |
| `tiss_dados_plano` | ⬜ vazia | 0 | real | competencia | — | — | 0.0 B |
| | | | | | *Fonte TISS não carregada em bruto_ans* | | |
| `tiss_dados_plano_default` | ⬜ vazia | 0 | real | competencia | — | — | 16.0 KB |
| | | | | | *Fonte TISS não carregada em bruto_ans* | | |
| `tiss_hospitalar` | ⬜ vazia | 0 | real | competencia | — | — | 0.0 B |
| | | | | | *Fonte TISS não carregada em bruto_ans* | | |
| `tiss_hospitalar_default` | ⬜ vazia | 0 | real | competencia | — | — | 16.0 KB |
| | | | | | *Fonte TISS não carregada em bruto_ans* | | |
| `tiss_procedimento_trimestral` | ⬜ vazia | 0 | real | trimestre | — | — | 0.0 B |
| | | | | | *Fonte TISS não carregada em bruto_ans* | | |
| `tiss_procedimento_trimestral_default` | ⬜ vazia | 0 | real | trimestre | — | — | 32.0 KB |
| | | | | | *Fonte TISS não carregada em bruto_ans* | | |
| `tuss_procedimento` | ⬜ vazia | 0 | real | — | — | — | 64.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `valor_comercial_medio_municipio` | ⬜ vazia | 0 | real | competencia | — | — | 16.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `vda_operadora_mensal` | ⬜ vazia | 0 | real | competencia | — | — | 0.0 B |
| | | | | | *Fonte VDA não carregada em bruto_ans* | | |
| `vda_operadora_mensal_default` | ⬜ vazia | 0 | real | competencia | — | — | 32.0 KB |
| | | | | | *Fonte VDA não carregada em bruto_ans* | | |
| `vda_quarentena` | ⬜ vazia | 0 | real | — | — | — | 16.0 KB |
| | | | | | *Fonte VDA não carregada em bruto_ans* | | |

## Schema: `bruto_cliente` — bronze cliente

| Tabela | Status | Registros | Tipo Count | Col. Temporal | Período (min→max) | Períodos | Tamanho |
|--------|--------|-----------|-----------|---------------|-------------------|----------|---------|
| `contrato` | ⬜ vazia | 0 | real | competencia | — | — | 40.0 KB |
| | | | | | *Schema premium/MDM/quality não implementado nesta fase* | | |
| `subfatura` | ⬜ vazia | 0 | real | competencia | — | — | 40.0 KB |
| | | | | | *Schema premium/MDM/quality não implementado nesta fase* | | |

## Schema: `consumo_ans` — serving/cliente

| Tabela | Status | Registros | Tipo Count | Col. Temporal | Período (min→max) | Períodos | Tamanho |
|--------|--------|-----------|-----------|---------------|-------------------|----------|---------|
| `consumo_beneficiarios_municipio_mes` | ✅ preenchida | 646 | real | competencia | 202603 → 202603 | 1 | 136.0 KB |
| `consumo_beneficiarios_operadora_mes` | ✅ preenchida | 757 | real | competencia | 202603 → 202603 | 1 | 136.0 KB |
| `consumo_financeiro_operadora_trimestre` | ✅ preenchida | 10,978 | real | trimestre | 1T2023 → 4T2025 | 13 | 2.5 MB |
| `consumo_glosa_operadora_mensal` | ✅ preenchida | 4,170 | real | competencia | 202501 → 202501 | 1 | 456.0 KB |
| `consumo_historico_plano` | ✅ preenchida | 163,567 | real | competencia | 202505 → 202505 | 1 | 14.0 MB |
| `consumo_idss` | ✅ preenchida | 13,072 | real | — | — | — | 1.1 MB |
| `consumo_igr` | ✅ preenchida | 136,908 | real | trimestre | 201501 → 202604 | 136 | 15.0 MB |
| `consumo_nip` | ✅ preenchida | 53,637 | real | trimestre | 201101 → 202012 | 120 | 5.5 MB |
| `consumo_operadora_360` | ✅ preenchida | 757 | real | competencia | 202603 → 202603 | 1 | 264.0 KB |
| `consumo_oportunidade_municipio` | ✅ preenchida | 646 | real | competencia | 202603 → 202603 | 1 | 136.0 KB |
| `consumo_produto_plano` | ✅ preenchida | 163,661 | real | competencia | 202605 → 202605 | 1 | 33.0 MB |
| `consumo_prudencial_operadora_trimestral` | ✅ preenchida | 11,216 | real | trimestre | 1T2024 → 4T2025 | 10 | 1.1 MB |
| `consumo_regime_especial_operadora_trimestral` | ✅ preenchida | 117 | real | trimestre | 1T2002 → 1T2025 | 20 | 40.0 KB |
| `consumo_regulatorio_operadora_trimestre` | ✅ preenchida | 161,173 | real | trimestre | 201101 → 202604 | 184 | 20.5 MB |
| `consumo_score_operadora_mes` | ✅ preenchida | 757 | real | competencia | 202603 → 202603 | 1 | 136.0 KB |
| `consumo_taxa_resolutividade_operadora_trimestral` | ✅ preenchida | 26,062 | real | trimestre | 201501 → 201910 | 58 | 3.6 MB |
| `consumo_tuss_procedimento_vigente` | ✅ preenchida | 64,654 | real | — | — | — | 10.0 MB |
| `consumo_beneficiarios_cobertura_municipio` | ⬜ vazia | 0 | real | competencia | — | — | 8.0 KB |
| | | | | | *SIB beneficiário não materializado via dbt* | | |
| `consumo_plano_servico_opcional` | ⬜ vazia | 0 | real | competencia | — | — | 8.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `consumo_precificacao_plano` | ⬜ vazia | 0 | real | competencia | — | — | 8.0 KB |
| | | | | | *painel_precificacao: registro_ans=NULL em todos os registros brutos* | | |
| `consumo_rede_acreditacao` | ⬜ vazia | 0 | real | data_acreditacao | — | — | 8.0 KB |
| | | | | | *Fonte rede assistencial não carregada em bruto_ans* | | |
| `consumo_rede_assistencial_municipio` | ⬜ vazia | 0 | real | competencia | — | — | 8.0 KB |
| | | | | | *Fonte rede assistencial não carregada em bruto_ans* | | |
| `consumo_regulatorio_complementar_operadora` | ⬜ vazia | 0 | real | competencia | — | — | 8.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `consumo_ressarcimento_sus_operadora` | ⬜ vazia | 0 | real | competencia | — | — | 8.0 KB |
| | | | | | *Fonte ressarcimento não carregada em bruto_ans* | | |
| `consumo_sip_assistencial_operadora` | ⬜ vazia | 0 | real | competencia | — | — | 8.0 KB |
| | | | | | *Fonte SIB/SIP não carregada ou registro_ans=NULL no bruto* | | |
| `consumo_tiss_utilizacao_operadora_mes` | ⬜ vazia | 0 | real | competencia | — | — | 8.0 KB |
| | | | | | *Fonte TISS não carregada em bruto_ans* | | |

## Schema: `consumo_premium_ans` — premium

| Tabela | Status | Registros | Tipo Count | Col. Temporal | Período (min→max) | Períodos | Tamanho |
|--------|--------|-----------|-----------|---------------|-------------------|----------|---------|
| `consumo_premium_mdm_operadora` | ✅ preenchida | 1,107 | real | — | — | — | 296.0 KB |
| `consumo_premium_operadora_360_validado` | ✅ preenchida | 757 | real | competencia | 202603 → 202603 | 1 | 264.0 KB |
| `consumo_premium_quality_dataset` | ✅ preenchida | 2 | real | — | — | — | 16.0 KB |
| `xref_tiss_tuss_procedimento` | ✅ preenchida | 3,500 | real | — | — | — | 464.0 KB |
| `consumo_premium_cnes_estabelecimento_validado` | ⬜ vazia | 0 | real | competencia | — | — | 8.0 KB |
| | | | | | *Schema premium/MDM/quality não implementado nesta fase* | | |
| `consumo_premium_contrato_inconsistencia` | ⬜ vazia | 0 | real | — | — | — | 8.0 KB |
| | | | | | *Schema premium/MDM/quality não implementado nesta fase* | | |
| `consumo_premium_contrato_subfatura_operadora` | ⬜ vazia | 0 | real | competencia | — | — | 8.0 KB |
| | | | | | *Schema premium/MDM/quality não implementado nesta fase* | | |
| `consumo_premium_contrato_validado` | ⬜ vazia | 0 | real | — | — | — | 8.0 KB |
| | | | | | *Schema premium/MDM/quality não implementado nesta fase* | | |
| `consumo_premium_mdm_prestador` | ⬜ vazia | 0 | real | — | — | — | 8.0 KB |
| | | | | | *Schema premium/MDM/quality não implementado nesta fase* | | |
| `consumo_premium_subfatura_validada` | ⬜ vazia | 0 | real | competencia | — | — | 8.0 KB |
| | | | | | *Schema premium/MDM/quality não implementado nesta fase* | | |
| `consumo_premium_tiss_procedimento_tuss_validado` | ⬜ vazia | 0 | real | trimestre | — | — | 8.0 KB |
| | | | | | *Schema premium/MDM/quality não implementado nesta fase* | | |

## Schema: `mdm_ans` — MDM público

| Tabela | Status | Registros | Tipo Count | Col. Temporal | Período (min→max) | Períodos | Tamanho |
|--------|--------|-----------|-----------|---------------|-------------------|----------|---------|
| `mdm_operadora_master` | ✅ preenchida | 1,107 | real | — | — | — | 296.0 KB |
| `xref_operadora_origem` | ✅ preenchida | 1,107 | real | — | — | — | 136.0 KB |
| `mdm_estabelecimento_exception` | ⬜ vazia | 0 | real | — | — | — | 8.0 KB |
| | | | | | *Schema premium/MDM/quality não implementado nesta fase* | | |
| `mdm_estabelecimento_master` | ⬜ vazia | 0 | real | — | — | — | 8.0 KB |
| | | | | | *Schema premium/MDM/quality não implementado nesta fase* | | |
| `mdm_operadora_exception` | ⬜ vazia | 0 | real | — | — | — | 8.0 KB |
| | | | | | *Schema premium/MDM/quality não implementado nesta fase* | | |
| `mdm_prestador_exception` | ⬜ vazia | 0 | real | — | — | — | 8.0 KB |
| | | | | | *Schema premium/MDM/quality não implementado nesta fase* | | |
| `mdm_prestador_master` | ⬜ vazia | 0 | real | — | — | — | 8.0 KB |
| | | | | | *Schema premium/MDM/quality não implementado nesta fase* | | |
| `xref_estabelecimento_origem` | ⬜ vazia | 0 | real | — | — | — | 8.0 KB |
| | | | | | *Schema premium/MDM/quality não implementado nesta fase* | | |
| `xref_prestador_origem` | ⬜ vazia | 0 | real | — | — | — | 8.0 KB |
| | | | | | *Schema premium/MDM/quality não implementado nesta fase* | | |

## Schema: `mdm_privado` — MDM privado

| Tabela | Status | Registros | Tipo Count | Col. Temporal | Período (min→max) | Períodos | Tamanho |
|--------|--------|-----------|-----------|---------------|-------------------|----------|---------|
| `mdm_contrato_exception` | ⬜ vazia | 0 | real | — | — | — | 8.0 KB |
| | | | | | *Schema premium/MDM/quality não implementado nesta fase* | | |
| `mdm_contrato_master` | ⬜ vazia | 0 | real | — | — | — | 8.0 KB |
| | | | | | *Schema premium/MDM/quality não implementado nesta fase* | | |
| `mdm_operadora_contrato_exception` | ⬜ vazia | 0 | real | — | — | — | 8.0 KB |
| | | | | | *Schema premium/MDM/quality não implementado nesta fase* | | |
| `mdm_prestador_contrato_exception` | ⬜ vazia | 0 | real | — | — | — | 8.0 KB |
| | | | | | *Schema premium/MDM/quality não implementado nesta fase* | | |
| `mdm_subfatura_exception` | ⬜ vazia | 0 | real | — | — | — | 8.0 KB |
| | | | | | *Schema premium/MDM/quality não implementado nesta fase* | | |
| `mdm_subfatura_master` | ⬜ vazia | 0 | real | competencia | — | — | 8.0 KB |
| | | | | | *Schema premium/MDM/quality não implementado nesta fase* | | |
| `xref_contrato_origem` | ⬜ vazia | 0 | real | — | — | — | 8.0 KB |
| | | | | | *Schema premium/MDM/quality não implementado nesta fase* | | |
| `xref_subfatura_origem` | ⬜ vazia | 0 | real | — | — | — | 8.0 KB |
| | | | | | *Schema premium/MDM/quality não implementado nesta fase* | | |

## Schema: `nucleo_ans` — gold/núcleo

| Tabela | Status | Registros | Tipo Count | Col. Temporal | Período (min→max) | Períodos | Tamanho |
|--------|--------|-----------|-----------|---------------|-------------------|----------|---------|
| `dim_competencia` | ✅ preenchida | 1 | real | competencia | 202603 → 202603 | 1 | 16.0 KB |
| `dim_localidade` | ✅ preenchida | 646 | real | — | — | — | 72.0 KB |
| `dim_modalidade` | ✅ preenchida | 8 | real | — | — | — | 16.0 KB |
| `dim_operadora_atual` | ✅ preenchida | 1,107 | real | — | — | — | 224.0 KB |
| `dim_segmentacao` | ✅ preenchida | 4 | real | — | — | — | 16.0 KB |
| `dim_tuss_procedimento` | ✅ preenchida | 3,500 | real | — | — | — | 560.0 KB |
| `dim_tuss_terminologia` | ✅ preenchida | 3,500 | real | — | — | — | 440.0 KB |
| `fat_beneficiario_localidade` | ✅ preenchida | 59,197 | real | competencia | 202603 → 202603 | 1 | 7.5 MB |
| `fat_beneficiario_operadora` | ✅ preenchida | 757 | real | competencia | 202603 → 202603 | 1 | 112.0 KB |
| `fat_financeiro_operadora_trimestral` | ✅ preenchida | 10,978 | real | trimestre | 1T2023 → 4T2025 | 13 | 5.5 MB |
| `fat_glosa_operadora_mensal` | ✅ preenchida | 4,083 | real | competencia | 202501 → 202501 | 1 | 2.2 MB |
| `fat_idss_operadora` | ✅ preenchida | 10,409 | real | — | — | — | 1.3 MB |
| `fat_market_share_mensal` | ✅ preenchida | 59,197 | real | competencia | 202603 → 202603 | 1 | 15.8 MB |
| `fat_monitoramento_regulatorio_trimestral` | ✅ preenchida | 161,173 | real | trimestre | 201101 → 202604 | 184 | 37.9 MB |
| `fat_oportunidade_municipio_mensal` | ✅ preenchida | 646 | real | competencia | 202603 → 202603 | 1 | 184.0 KB |
| `fat_oportunidade_v2_municipio_mensal` | ✅ preenchida | 646 | real | competencia | 202603 → 202603 | 1 | 328.0 KB |
| `fat_ranking_composto_mensal` | ✅ preenchida | 757 | real | — | — | — | 264.0 KB |
| `fat_reclamacao_operadora` | ✅ preenchida | 368 | real | trimestre | 202012 → 202012 | 1 | 112.0 KB |
| `fat_regime_especial_historico` | ✅ preenchida | 53 | real | data_fim | — | — | 48.0 KB |
| `fat_score_operadora_mensal` | ✅ preenchida | 757 | real | competencia | 202603 → 202603 | 1 | 184.0 KB |
| `fat_score_regulatorio_operadora_mensal` | ✅ preenchida | 136,032 | real | competencia | 1T2003 → 4T2025 | 207 | 31.0 MB |
| `fat_score_v2_operadora_mensal` | ✅ preenchida | 136,034 | real | competencia | 1T2003 → 4T2025 | 207 | 31.5 MB |
| `fat_score_v3_operadora_mensal` | ✅ preenchida | 757 | real | — | — | — | 264.0 KB |
| `mart_mercado_municipio` | ✅ preenchida | 646 | real | competencia | 202603 → 202603 | 1 | 136.0 KB |
| `mart_operadora_360` | ✅ preenchida | 757 | real | competencia | 202603 → 202603 | 1 | 264.0 KB |
| `mart_regulatorio_operadora` | ✅ preenchida | 161,173 | real | trimestre | 201101 → 202604 | 184 | 20.5 MB |
| `mart_score_operadora` | ✅ preenchida | 757 | real | competencia | 202603 → 202603 | 1 | 136.0 KB |
| `snap_operadora` | ✅ preenchida | 1,107 | real | — | — | — | 328.0 KB |
| `dim_tipo_contratacao` | ⬜ vazia | 0 | real | — | — | — | 8.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `fat_cnes_estabelecimento_municipio` | ⬜ vazia | 0 | real | competencia | — | — | 8.0 KB |
| | | | | | *Fonte CNES não carregada em bruto_ans* | | |
| `fat_cnes_rede_gap_municipio` | ⬜ vazia | 0 | real | competencia | — | — | 8.0 KB |
| | | | | | *Fonte CNES não carregada em bruto_ans* | | |
| `fat_cobertura_rede_municipio` | ⬜ vazia | 0 | real | competencia | — | — | 8.0 KB |
| | | | | | *Fonte rede assistencial não carregada em bruto_ans* | | |
| `fat_densidade_rede_operadora` | ⬜ vazia | 0 | real | competencia | — | — | 8.0 KB |
| | | | | | *Fonte rede assistencial não carregada em bruto_ans* | | |
| `fat_sinistralidade_procedimento` | ⬜ vazia | 0 | real | trimestre | — | — | 8.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `fat_tiss_procedimento_operadora` | ⬜ vazia | 0 | real | trimestre | — | — | 8.0 KB |
| | | | | | *Fonte TISS não carregada em bruto_ans* | | |
| `fat_vazio_assistencial_municipio` | ⬜ vazia | 0 | real | competencia | — | — | 8.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `fat_vda_operadora_mensal` | ⬜ vazia | 0 | real | competencia | — | — | 8.0 KB |
| | | | | | *Fonte VDA não carregada em bruto_ans* | | |
| `mart_rede_assistencial` | ⬜ vazia | 0 | real | competencia | — | — | 8.0 KB |
| | | | | | *Fonte rede assistencial não carregada em bruto_ans* | | |
| `mart_tiss_procedimento` | ⬜ vazia | 0 | real | trimestre | — | — | 8.0 KB |
| | | | | | *Fonte TISS não carregada em bruto_ans* | | |

## Schema: `plataforma` — governança

| Tabela | Status | Registros | Tipo Count | Col. Temporal | Período (min→max) | Períodos | Tamanho |
|--------|--------|-----------|-----------|---------------|-------------------|----------|---------|
| `arquivo_fonte_ans` | ✅ preenchida | 364 | real | dataset_codigo | beneficiario_regiao_geografica → valor_comercial_medio_municipio | 45 | 488.0 KB |
| `arquivo_quarentena` | ✅ preenchida | 56 | real | dataset | beneficiario_regiao_geografica → valor_comercial_medio_municipio | 23 | 80.0 KB |
| `backup_execucao` | ✅ preenchida | 9 | real | — | — | — | 48.0 KB |
| `chave_api` | ✅ preenchida | 3 | real | — | — | — | 80.0 KB |
| `cliente` | ✅ preenchida | 3 | real | — | — | — | 48.0 KB |
| `execucao_layout` | ✅ preenchida | 10 | real | dataset | cadop → tuss_oficial | 10 | 32.0 KB |
| `fonte_dado_ans` | ✅ preenchida | 14,637 | real | dataset_codigo | caderno_ss_generico → tiss_hospitalar | 12 | 6.7 MB |
| `ingestao_janela_decisao` | ✅ preenchida | 85 | real | competencia | 201901 → 202701 | 15 | 112.0 KB |
| `job` | ✅ preenchida | 194 | real | — | — | — | 112.0 KB |
| `log_uso` | ✅ preenchida | 400 | real | — | — | — | 0.0 B |
| `log_uso_default` | ✅ preenchida | 400 | real | — | — | — | 248.0 KB |
| `lote_ingestao` | ✅ preenchida | 157 | real | competencia | 202001 → 202605 | 41 | 152.0 KB |
| `mapa_layout_resolvido` | ✅ preenchida | 133 | real | — | — | — | 72.0 KB |
| `plano` | ✅ preenchida | 13 | real | — | — | — | 48.0 KB |
| `politica_dataset` | ✅ preenchida | 28 | real | dataset_codigo | ans_arquivo_generico → vda | 28 | 64.0 KB |
| `retencao_particao_log` | ✅ preenchida | 126 | real | — | — | — | 96.0 KB |
| `tentativa_carga_ans` | ✅ preenchida | 108 | real | competencia | 202001 → 202605 | 22 | 192.0 KB |
| `versao_dataset` | ✅ preenchida | 10 | real | competencia | 202410 → 202605 | 4 | 32.0 KB |
| `vw_ingestao_janela_resumo` | ✅ preenchida | 6 | real | dataset_codigo | glosa → sib_operadora | 3 | 0.0 B |
| `vw_resumo_quarentena` | ✅ preenchida | 27 | real | competencia | 202605 → desconhecida | 2 | 0.0 B |
| `vw_tamanho_dataset` | ✅ preenchida | 28 | real | dataset_codigo | ans_arquivo_generico → vda | 28 | 0.0 B |
| `vw_versao_vigente` | ✅ preenchida | 8 | real | dataset_codigo | cnes_estabelecimento → tuss_procedimento | 8 | 0.0 B |
| `auditoria_cobranca` | ⬜ vazia | 0 | real | — | — | — | 24.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `backup_alerta` | ⬜ vazia | 0 | real | — | — | — | 24.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `ciclo_faturamento` | ⬜ vazia | 0 | real | — | — | — | 32.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `cliente_dataset_acesso` | ⬜ vazia | 0 | real | dataset_codigo | — | — | 32.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `controle_reprocessamento` | ⬜ vazia | 0 | real | dataset | — | — | 16.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `dataset_layout_ativo` | ⬜ vazia | 0 | real | dataset | — | — | 16.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `erro_parse` | ⬜ vazia | 0 | real | — | — | — | 16.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `fatura_consumo` | ⬜ vazia | 0 | real | — | — | — | 32.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `historico_plano` | ⬜ vazia | 0 | real | — | — | — | 24.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `publicacao_financeira` | ⬜ vazia | 0 | real | trimestre | — | — | 32.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `publicacao_financeira_v2` | ⬜ vazia | 0 | real | competencia | — | — | 32.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `publicacao_rede` | ⬜ vazia | 0 | real | competencia | — | — | 16.0 KB |
| | | | | | *Fonte rede assistencial não carregada em bruto_ans* | | |
| `publicacao_regulatoria` | ⬜ vazia | 0 | real | competencia | — | — | 32.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `reclassificacao_dataset_pendente` | ⬜ vazia | 0 | real | dataset_codigo | — | — | 32.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `solicitacao_historico` | ⬜ vazia | 0 | real | dataset_codigo | — | — | 64.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `versao_dataset_vigente` | ⬜ vazia | 0 | real | dataset_codigo | — | — | 80.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |

## Schema: `public` — sistema

| Tabela | Status | Registros | Tipo Count | Col. Temporal | Período (min→max) | Períodos | Tamanho |
|--------|--------|-----------|-----------|---------------|-------------------|----------|---------|
| `ab_permission` | ✅ preenchida | 5 | real | — | — | — | 40.0 KB |
| `ab_permission_view` | ✅ preenchida | 212 | real | — | — | — | 72.0 KB |
| `ab_permission_view_role` | ✅ preenchida | 228 | real | — | — | — | 72.0 KB |
| `ab_role` | ✅ preenchida | 5 | real | — | — | — | 40.0 KB |
| `ab_user` | ✅ preenchida | 1 | real | — | — | — | 80.0 KB |
| `ab_user_role` | ✅ preenchida | 1 | real | — | — | — | 40.0 KB |
| `ab_view_menu` | ✅ preenchida | 93 | real | — | — | — | 40.0 KB |
| `alembic_version` | ✅ preenchida | 1 | real | — | — | — | 24.0 KB |
| `dag` | ✅ preenchida | 40 | real | dataset_expression | — | — | 488.0 KB |
| `dag_code` | ✅ preenchida | 40 | real | — | — | — | 152.0 KB |
| `dag_run` | ✅ preenchida | 215 | real | data_interval_start | 2025-01-01 00:00:00+00 → 2026-05-16 00:00:00+00 | 74 | 2.6 MB |
| `dag_tag` | ✅ preenchida | 133 | real | — | — | — | 56.0 KB |
| `job` | ✅ preenchida | 545 | real | — | — | — | 768.0 KB |
| `log` | ✅ preenchida | 12,019 | real | — | — | — | 3.9 MB |
| `log_template` | ✅ preenchida | 2 | real | — | — | — | 32.0 KB |
| `rendered_task_instance_fields` | ✅ preenchida | 514 | real | — | — | — | 400.0 KB |
| `serialized_dag` | ✅ preenchida | 40 | real | data_compressed | — | — | 272.0 KB |
| `session` | ✅ preenchida | 1,444 | real | data | — | — | 528.0 KB |
| `slot_pool` | ✅ preenchida | 1 | real | — | — | — | 48.0 KB |
| `task_fail` | ✅ preenchida | 322 | real | — | — | — | 168.0 KB |
| `task_instance` | ✅ preenchida | 644 | real | — | — | — | 760.0 KB |
| `xcom` | ✅ preenchida | 220 | real | — | — | — | 184.0 KB |
| `ab_register_user` | ⬜ vazia | 0 | real | — | — | — | 32.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `callback_request` | ⬜ vazia | 0 | real | — | — | — | 16.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `connection` | ⬜ vazia | 0 | real | — | — | — | 24.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `dag_owner_attributes` | ⬜ vazia | 0 | real | — | — | — | 16.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `dag_pickle` | ⬜ vazia | 0 | real | — | — | — | 16.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `dag_run_note` | ⬜ vazia | 0 | real | — | — | — | 16.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `dag_schedule_dataset_reference` | ⬜ vazia | 0 | real | dataset_id | — | — | 8.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `dag_warning` | ⬜ vazia | 0 | real | — | — | — | 16.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `dagrun_dataset_event` | ⬜ vazia | 0 | real | — | — | — | 24.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `dataset` | ⬜ vazia | 0 | real | — | — | — | 24.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `dataset_dag_run_queue` | ⬜ vazia | 0 | real | dataset_id | — | — | 8.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `dataset_event` | ⬜ vazia | 0 | real | dataset_id | — | — | 24.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `import_error` | ⬜ vazia | 0 | real | — | — | — | 32.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `sla_miss` | ⬜ vazia | 0 | real | — | — | — | 24.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `task_instance_note` | ⬜ vazia | 0 | real | — | — | — | 16.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `task_map` | ⬜ vazia | 0 | real | — | — | — | 16.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `task_outlet_dataset_reference` | ⬜ vazia | 0 | real | dataset_id | — | — | 16.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `task_reschedule` | ⬜ vazia | 0 | real | — | — | — | 32.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `trigger` | ⬜ vazia | 0 | real | — | — | — | 16.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `variable` | ⬜ vazia | 0 | real | — | — | — | 24.0 KB |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |

## Schema: `quality_ans` — qualidade

| Tabela | Status | Registros | Tipo Count | Col. Temporal | Período (min→max) | Períodos | Tamanho |
|--------|--------|-----------|-----------|---------------|-------------------|----------|---------|
| `dq_cadop_documento` | ✅ preenchida | 1,107 | real | — | — | — | 280.0 KB |
| `dq_operadora_documento` | ✅ preenchida | 1,107 | real | — | — | — | 248.0 KB |
| `audit_operadora_razao_social_divergente_cadop` | ⬜ vazia | 0 | real | — | — | — | 8.0 KB |
| | | | | | *Schema premium/MDM/quality não implementado nesta fase* | | |
| `dq_cnes_documento` | ⬜ vazia | 0 | real | competencia | — | — | 8.0 KB |
| | | | | | *Schema premium/MDM/quality não implementado nesta fase* | | |
| `dq_prestador_documento` | ⬜ vazia | 0 | real | competencia | — | — | 8.0 KB |
| | | | | | *Schema premium/MDM/quality não implementado nesta fase* | | |

## Schema: `ref_ans` — referência

| Tabela | Status | Registros | Tipo Count | Col. Temporal | Período (min→max) | Períodos | Tamanho |
|--------|--------|-----------|-----------|---------------|-------------------|----------|---------|
| `ref_competencia` | ✅ preenchida | 192 | real | competencia | 201501 → 203012 | 192 | 40.0 KB |
| `ref_indicador_financeiro` | ✅ preenchida | 4 | real | — | — | — | 16.0 KB |
| `ref_modalidade` | ✅ preenchida | 8 | real | — | — | — | 16.0 KB |
| `ref_municipio_ibge` | ✅ preenchida | 5,571 | real | — | — | — | 368.0 KB |
| `ref_parametro_rede` | ✅ preenchida | 6 | real | — | — | — | 16.0 KB |
| `ref_parto_cesareo` | ✅ preenchida | 16 | real | trimestre | 2024T1 → 2025T4 | 8 | 16.0 KB |
| `ref_populacao_municipio` | ✅ preenchida | 3 | real | — | — | — | 16.0 KB |
| `ref_rol_procedimento` | ✅ preenchida | 3,500 | real | — | — | — | 304.0 KB |
| `ref_tuss` | ✅ preenchida | 3,500 | real | — | — | — | 368.0 KB |
| `ref_uf` | ✅ preenchida | 27 | real | — | — | — | 16.0 KB |
| `score_pesos` | ✅ preenchida | 4 | real | — | — | — | 16.0 KB |

## Schema: `stg_ans` — staging

| Tabela | Status | Registros | Tipo Count | Col. Temporal | Período (min→max) | Períodos | Tamanho |
|--------|--------|-----------|-----------|---------------|-------------------|----------|---------|
| `stg_ans_arquivo_generico` | ✅ preenchida | 7 | real | data_ingestao | 2026-05-13 19:51:48.58963+00 → 2026-05-14 04:58:26.617089+00 | 7 | 0.0 B |
| `stg_cadop` | ✅ preenchida | 1,107 | real | — | — | — | 0.0 B |
| `stg_diops` | ✅ preenchida | 11,563 | real | trimestre | 1T2023 → 4T2025 | 13 | 0.0 B |
| `stg_glosa` | ✅ preenchida | 4,170 | real | competencia | 202501 → 202501 | 1 | 0.0 B |
| `stg_historico_plano` | ✅ preenchida | 163,567 | real | competencia | 202505 → 202505 | 1 | 0.0 B |
| `stg_idss` | ✅ preenchida | 13,072 | real | — | — | — | 0.0 B |
| `stg_igr` | ✅ preenchida | 136,908 | real | trimestre | 201501 → 202604 | 136 | 0.0 B |
| `stg_nip` | ✅ preenchida | 53,637 | real | trimestre | 201101 → 202012 | 120 | 0.0 B |
| `stg_produto_caracteristica` | ✅ preenchida | 163,661 | real | competencia | 202605 → 202605 | 1 | 0.0 B |
| `stg_prudencial` | ✅ preenchida | 11,216 | real | trimestre | 1T2024 → 4T2025 | 10 | 0.0 B |
| `stg_quadro_auxiliar_corresponsabilidade` | ✅ preenchida | 1,032 | real | competencia | 202505 → 202505 | 1 | 0.0 B |
| `stg_regime_especial` | ✅ preenchida | 117 | real | trimestre | 1T2002 → 1T2025 | 20 | 0.0 B |
| `stg_sib_municipio` | ✅ preenchida | 59,892 | real | competencia | 202603 → 202603 | 1 | 0.0 B |
| `stg_sib_operadora` | ✅ preenchida | 803 | real | competencia | 202603 → 202603 | 1 | 0.0 B |
| `stg_taxa_resolutividade` | ✅ preenchida | 26,062 | real | trimestre | 201501 → 201910 | 58 | 0.0 B |
| `stg_tuss_terminologia` | ✅ preenchida | 3,500 | real | — | — | — | 0.0 B |
| `stg_tuss_terminologia_oficial` | ✅ preenchida | 64,660 | real | — | — | — | 0.0 B |
| `stg_ans_linha_generica` | ⬜ vazia | 0 | real | data_ingestao | — | — | 0.0 B |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `stg_beneficiario_informacao_consolidada` | ⬜ vazia | 0 | real | competencia | — | — | 0.0 B |
| | | | | | *SIB beneficiário não materializado via dbt* | | |
| `stg_beneficiario_regiao_geografica` | ⬜ vazia | 0 | real | competencia | — | — | 0.0 B |
| | | | | | *SIB beneficiário não materializado via dbt* | | |
| `stg_cnes_estabelecimento` | ⬜ vazia | 0 | real | competencia | — | — | 0.0 B |
| | | | | | *Fonte CNES não carregada em bruto_ans* | | |
| `stg_faixa_preco` | ⬜ vazia | 0 | real | competencia | — | — | 0.0 B |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `stg_fip` | ⬜ vazia | 0 | real | trimestre | — | — | 0.0 B |
| | | | | | *Fonte FIP não carregada em bruto_ans* | | |
| `stg_iap` | ⬜ vazia | 0 | real | competencia | — | — | 0.0 B |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `stg_monitoramento_garantia_atendimento` | ⬜ vazia | 0 | real | competencia | — | — | 0.0 B |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `stg_ntrp_area_comercializacao` | ⬜ vazia | 0 | real | competencia | — | — | 0.0 B |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `stg_ntrp_vcm_faixa_etaria` | ⬜ vazia | 0 | real | competencia | — | — | 0.0 B |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `stg_operadora_acreditada` | ⬜ vazia | 0 | real | data_validade | — | — | 0.0 B |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `stg_operadora_cancelada` | ⬜ vazia | 0 | real | data_cancelamento | — | — | 0.0 B |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `stg_operadora_prestador_nao_hospitalar` | ⬜ vazia | 0 | real | competencia | — | — | 0.0 B |
| | | | | | *produto_prestador: registro_ans=NULL em todos os registros brutos* | | |
| `stg_painel_precificacao` | ⬜ vazia | 0 | real | competencia | — | — | 0.0 B |
| | | | | | *painel_precificacao: registro_ans=NULL em todos os registros brutos* | | |
| `stg_penalidade_operadora` | ⬜ vazia | 0 | real | competencia | — | — | 0.0 B |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `stg_peona_sus` | ⬜ vazia | 0 | real | competencia | — | — | 0.0 B |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `stg_percentual_reajuste_agrupamento` | ⬜ vazia | 0 | real | competencia | — | — | 0.0 B |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `stg_pfa` | ⬜ vazia | 0 | real | competencia | — | — | 0.0 B |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `stg_plano_servico_opcional` | ⬜ vazia | 0 | real | competencia | — | — | 0.0 B |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `stg_portabilidade` | ⬜ vazia | 0 | real | competencia | — | — | 0.0 B |
| | | | | | *Fonte portabilidade não carregada em bruto_ans* | | |
| `stg_prestador_acreditado` | ⬜ vazia | 0 | real | data_validade | — | — | 0.0 B |
| | | | | | *produto_prestador: registro_ans=NULL em todos os registros brutos* | | |
| `stg_produto_prestador_hospitalar` | ⬜ vazia | 0 | real | competencia | — | — | 0.0 B |
| | | | | | *produto_prestador: registro_ans=NULL em todos os registros brutos* | | |
| `stg_produto_tabela_auxiliar` | ⬜ vazia | 0 | real | competencia | — | — | 0.0 B |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `stg_programa_qualificacao_institucional` | ⬜ vazia | 0 | real | competencia | — | — | 0.0 B |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `stg_promoprev` | ⬜ vazia | 0 | real | competencia | — | — | 0.0 B |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `stg_rede_assistencial` | ⬜ vazia | 0 | real | competencia | — | — | 0.0 B |
| | | | | | *Fonte rede assistencial não carregada em bruto_ans* | | |
| `stg_ressarcimento_beneficiario_abi` | ⬜ vazia | 0 | real | competencia | — | — | 0.0 B |
| | | | | | *Fonte ressarcimento não carregada em bruto_ans* | | |
| `stg_ressarcimento_cobranca_arrecadacao` | ⬜ vazia | 0 | real | competencia | — | — | 0.0 B |
| | | | | | *Fonte ressarcimento não carregada em bruto_ans* | | |
| `stg_ressarcimento_hc` | ⬜ vazia | 0 | real | competencia | — | — | 0.0 B |
| | | | | | *Fonte ressarcimento não carregada em bruto_ans* | | |
| `stg_ressarcimento_indice_pagamento` | ⬜ vazia | 0 | real | competencia | — | — | 0.0 B |
| | | | | | *Fonte ressarcimento não carregada em bruto_ans* | | |
| `stg_ressarcimento_sus_operadora_plano` | ⬜ vazia | 0 | real | competencia | — | — | 0.0 B |
| | | | | | *Fonte ressarcimento não carregada em bruto_ans* | | |
| `stg_rn623_lista` | ⬜ vazia | 0 | real | trimestre | — | — | 0.0 B |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `stg_rpc` | ⬜ vazia | 0 | real | competencia | — | — | 0.0 B |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `stg_sip_mapa_assistencial` | ⬜ vazia | 0 | real | competencia | — | — | 0.0 B |
| | | | | | *Fonte SIB/SIP não carregada ou registro_ans=NULL no bruto* | | |
| `stg_solicitacao_alteracao_rede_hospitalar` | ⬜ vazia | 0 | real | competencia | — | — | 0.0 B |
| | | | | | *Fonte rede assistencial não carregada em bruto_ans* | | |
| `stg_taxa_cobertura_plano` | ⬜ vazia | 0 | real | competencia | — | — | 0.0 B |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `stg_tiss_ambulatorial` | ⬜ vazia | 0 | real | competencia | — | — | 0.0 B |
| | | | | | *Fonte TISS não carregada em bruto_ans* | | |
| `stg_tiss_dados_plano` | ⬜ vazia | 0 | real | competencia | — | — | 0.0 B |
| | | | | | *Fonte TISS não carregada em bruto_ans* | | |
| `stg_tiss_hospitalar` | ⬜ vazia | 0 | real | competencia | — | — | 0.0 B |
| | | | | | *Fonte TISS não carregada em bruto_ans* | | |
| `stg_tiss_procedimento` | ⬜ vazia | 0 | real | trimestre | — | — | 0.0 B |
| | | | | | *Fonte TISS não carregada em bruto_ans* | | |
| `stg_valor_comercial_medio_municipio` | ⬜ vazia | 0 | real | competencia | — | — | 0.0 B |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `stg_vda` | ⬜ vazia | 0 | real | competencia | — | — | 0.0 B |
| | | | | | *Fonte VDA não carregada em bruto_ans* | | |

## Schema: `stg_cliente` — staging cliente

| Tabela | Status | Registros | Tipo Count | Col. Temporal | Período (min→max) | Períodos | Tamanho |
|--------|--------|-----------|-----------|---------------|-------------------|----------|---------|
| `stg_cliente_contrato` | ⬜ vazia | 0 | real | competencia | — | — | 0.0 B |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |
| `stg_cliente_subfatura` | ⬜ vazia | 0 | real | competencia | — | — | 0.0 B |
| | | | | | *Fonte bruta ausente ou dbt model dependente de dado não carregado* | | |

---

## Legenda

| Símbolo | Significado |
|---------|-------------|
| ✅ | Tabela preenchida com dados reais |
| ⬜ | Tabela vazia — sem dados disponíveis |
| ❌ | Erro ao consultar |
| `count_tipo=real` | COUNT(*) executado |
| `count_tipo=estimado` | n_live_tup usado (tabela > 1M linhas) |
