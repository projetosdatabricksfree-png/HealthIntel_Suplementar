# Catálogo de Datasets

| Dataset | Schema PostgreSQL | Modelo dbt principal | DAG/Fonte | Freshness SLO | Referência ANS |
| --- | --- | --- | --- | --- | --- |
| `cadop` | `bruto_ans` | `stg_cadop` / `dim_operadora_atual` | `dag_ingest_cadop` | `24h` | Cadastro de operadoras |
| `sib_operadora` | `bruto_ans` | `stg_sib_operadora` / `fat_beneficiario_operadora` | `dag_ingest_sib_operadora` | `72h` | SIB mensal |
| `sib_municipio` | `bruto_ans` | `stg_sib_municipio` / `fat_beneficiario_localidade` | `dag_ingest_sib_municipio` | `72h` | SIB municipal |
| `igr` | `bruto_ans` | `stg_igr` / `fat_monitoramento_regulatorio_trimestral` | `dag_ingest_igr` | `72h` | IGR |
| `nip` | `bruto_ans` | `stg_nip` / `fat_reclamacao_operadora` | `dag_ingest_nip` | `72h` | NIP e TIR/TR |
| `rn623_lista` | `bruto_ans` | `stg_rn623_lista` / `api_rn623_lista_trimestral` | `dag_ingest_rn623_lista` | `72h` | RN 623/2024 |
| `idss` | `bruto_ans` | `stg_idss` / `fat_idss_operadora` | `dag_ingest_idss` | `30d` | IDSS |
| `regime_especial` | `bruto_ans` | `stg_regime_especial` / `fat_regime_especial_historico` | `dag_ingest_regime_especial` | `72h` | Regime especial |
| `prudencial` | `bruto_ans` | `stg_prudencial` / `int_regulatorio_v2_operadora_trimestre` | `dag_ingest_prudencial` | `72h` | Prudencial |
| `portabilidade` | `bruto_ans` | `stg_portabilidade` / `fat_portabilidade_operadora_mensal` | `dag_ingest_portabilidade` | `72h` | Portabilidade |
| `taxa_resolutividade` | `bruto_ans` | `stg_taxa_resolutividade` / `fat_monitoramento_regulatorio_trimestral` | `dag_ingest_taxa_resolutividade` | `72h` | Taxa de resolutividade |
| `diops` | `bruto_ans` | `stg_diops` / `fat_financeiro_operadora_trimestral` | `dag_ingest_diops` | `72h` | DIOPS |
| `fip` | `bruto_ans` | `stg_fip` / `fat_financeiro_operadora_trimestral` | `dag_ingest_fip` | `72h` | FIP |
| `vda` | `bruto_ans` | `stg_vda` / `fat_vda_operadora_mensal` | `dag_ingest_vda` | `30d` | VDA |
| `glosa` | `bruto_ans` | `stg_glosa` / `fat_glosa_operadora_mensal` | `dag_ingest_glosa` | `30d` | Glosa |
| `rede_assistencial` | `bruto_ans` | `stg_rede_assistencial` / `fat_cobertura_rede_municipio` | `dag_ingest_rede_assistencial` | `30d` | Painel de Rede e Vazios Assistenciais |
| `vazio_assistencial` | derivado | `fat_vazio_assistencial_municipio` / `api_vazio_assistencial` | derivação dbt | `30d` | Painel de Rede e Vazios Assistenciais |
| `oportunidade_v2` | derivado | `fat_oportunidade_v2_municipio_mensal` / `api_oportunidade_v2_municipio_mensal` | derivação dbt | `30d` | composto interno |

