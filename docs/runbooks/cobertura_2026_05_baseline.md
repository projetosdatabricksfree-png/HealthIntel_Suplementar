# Cobertura ANS — baseline 2026-05-27

Snapshot oficial das tabelas `api_ans.*` em produção antes do backfill da Frente 2 do plano `precisamos-analisar-a-quantidade-warm-newt`.

Banco: `healthintel` · Schema: `api_ans` · Container: `healthintel_postgres` · Data da coleta: **2026-05-27**.

## Datasets prometidos no site (`Coverage.tsx`) vs. realidade

| Promessa no site | Tabela(s) api_ans principais | Range competência | Linhas | Situação |
|---|---|---|---|---|
| **CADOP** — Cadastro de Operadoras | `api_bronze_cadop` · `api_prata_cadop` · `api_operadora` | 202401–202612 | 238.008 · 1.107 · 1.110 | ⚠️ Falta 2023 e anterior |
| **SIB** — Beneficiários | `api_bronze_sib_operadora` · `api_bronze_sib_municipio` · `api_prata_sib_*` | 202501–202603 | 804 · 59.893 | ❌ Sem 2023, 2024 (partições `_2024` vazias) |
| **CNES** — Rede | `api_cnes_municipio` · `api_cnes_rede_gap` · `api_prata_cnes_*` | 202305–202605 | 740 · 740 | ⚠️ Range OK, sub-ingerido (só 740 linhas) |
| **DIOPS** — Fin. operadoras | `api_bronze_diops` · `api_prata_diops` | 1T2023–4T2025 | 10.232.273 · 11.582 | ✅ OK |
| **FIP** — Fin. complementar | `api_bronze_fip` · `api_prata_fip` | 2024T1–2026T2 | 36 · 20 | ❌ Quase vazio |
| **IDSS** — Índice | `api_bronze_idss` · `api_prata_idss` | 2012–2025 | 13.072 | ✅ OK (13 anos) |
| **NIP** — Notificações | `api_bronze_nip` · `api_prata_nip` | 201101–**202012** | 53.637 | ❌ Parado há 5+ anos |
| **Reajustes** | `api_reajuste_agrupamento` | — | **0** | ❌ Vazio |
| **ROL / TUSS** | `api_tuss_procedimento_vigente` · `api_premium_tuss_procedimento` | (vigência) | 64.654 · 3.500 | ✅ OK |
| **Garantias Financeiras** | `api_prudencial_operadora_trimestral` · `api_garantia_atendimento` | 1T2024–4T2025 · — | 11.216 · **0** | ⚠️ Parcial |
| **VDA** (componente de Garantias) | `api_bronze_vda` · `api_prata_vda` | — | **0** | ❌ Vazio |
| **Mercado / Rankings / Score** | `api_market_share_mensal` · `api_ranking_composto_mensal` · `api_score_v3_operadora_mensal` | 202501–202603 · 1T2003–4T2025 | 59.198 · 136.341 · 136.341 | ✅ OK |
| **Metadados** | router `meta` (sem tabela única) | — | — | ✅ OK |

## Confirmação do bronze (origem)

Datasets em `bruto_ans` (origem da ingestão Airflow) para os casos críticos:

| Tabela bruto_ans | Linhas | Status |
|---|---:|---|
| `percentual_reajuste_agrupamento` | 0 | ❌ DAG nunca rodou com sucesso |
| `vda_operadora_mensal` | 0 | ❌ DAG nunca rodou com sucesso |
| `monitoramento_garantia_atendimento` | 0 | ❌ DAG nunca rodou com sucesso |
| `nip_operadora_trimestral` (pai) | 53.637 · max=202012 | ❌ Parou em 2020 |
| `sib_beneficiario_operadora_2024` | 0 | ❌ Sem ingestão 2024 |
| `sib_beneficiario_operadora_2025` | 1 | ❌ Quase vazio |
| `sib_beneficiario_municipio_2024` | 0 | ❌ Sem ingestão 2024 |
| `sib_beneficiario_municipio_2025` | 1 | ❌ Quase vazio |
| `sib_beneficiario_operadora` (pai) | 804 · 202501–202603 | ⚠️ Só janela curta |
| `sib_beneficiario_municipio` (pai) | 59.893 · 202501–202603 | ⚠️ Só janela curta |

## Classificação para o Coverage do site

**Em produção (badge verde):**
- DIOPS (3 anos), IDSS (13 anos), ROL/TUSS, Score/Rankings/Market Share (parcial), CADOP (de 2024), Prudencial (Garantias parcial), Metadados.

**Backfill em andamento (badge âmbar):**
- SIB histórico (2023–2024)
- NIP pós-2020 (2021–2026)
- Reajustes (todo histórico)
- VDA (todo histórico)
- Garantias completas (monitoramento_garantia_atendimento)
- FIP histórico completo
- CADOP 2023 e anterior
- CNES granularidade (estabelecimentos)

## Comandos para reproduzir

```bash
# Listar tabelas
docker exec -i healthintel_postgres psql -U healthintel -d healthintel -c "
  SELECT table_name FROM information_schema.tables 
  WHERE table_schema='api_ans' ORDER BY table_name;
"

# Coverage por dataset
docker exec -i healthintel_postgres psql -U healthintel -d healthintel -c "
SELECT 'cadop' AS dataset, MIN(competencia)::text, MAX(competencia)::text, COUNT(*) FROM api_ans.api_bronze_cadop
UNION ALL SELECT 'sib_operadora', MIN(competencia)::text, MAX(competencia)::text, COUNT(*) FROM api_ans.api_bronze_sib_operadora
UNION ALL SELECT 'sib_municipio', MIN(competencia)::text, MAX(competencia)::text, COUNT(*) FROM api_ans.api_bronze_sib_municipio
UNION ALL SELECT 'diops', MIN(trimestre)::text, MAX(trimestre)::text, COUNT(*) FROM api_ans.api_bronze_diops
UNION ALL SELECT 'fip', MIN(trimestre)::text, MAX(trimestre)::text, COUNT(*) FROM api_ans.api_bronze_fip
UNION ALL SELECT 'idss', MIN(ano_base)::text, MAX(ano_base)::text, COUNT(*) FROM api_ans.api_bronze_idss
UNION ALL SELECT 'igr', MIN(trimestre)::text, MAX(trimestre)::text, COUNT(*) FROM api_ans.api_bronze_igr
UNION ALL SELECT 'glosa', MIN(competencia)::text, MAX(competencia)::text, COUNT(*) FROM api_ans.api_bronze_glosa
UNION ALL SELECT 'nip', MIN(trimestre)::text, MAX(trimestre)::text, COUNT(*) FROM api_ans.api_bronze_nip
UNION ALL SELECT 'cnes_mun', MIN(competencia)::text, MAX(competencia)::text, COUNT(*) FROM api_ans.api_cnes_municipio
UNION ALL SELECT 'vda', MIN(competencia)::text, MAX(competencia)::text, COUNT(*) FROM api_ans.api_bronze_vda
UNION ALL SELECT 'reajuste', MIN(competencia)::text, MAX(competencia)::text, COUNT(*) FROM api_ans.api_reajuste_agrupamento
UNION ALL SELECT 'prudencial', MIN(trimestre)::text, MAX(trimestre)::text, COUNT(*) FROM api_ans.api_prudencial_operadora_trimestral
UNION ALL SELECT 'market_share', MIN(competencia)::text, MAX(competencia)::text, COUNT(*) FROM api_ans.api_market_share_mensal
UNION ALL SELECT 'score_v3', MIN(competencia_id)::text, MAX(competencia_id)::text, COUNT(*) FROM api_ans.api_score_v3_operadora_mensal
ORDER BY 1;
"
```

## Referências
- Plano: `/root/.claude/plans/precisamos-analisar-a-quantidade-warm-newt.md`
- Memória: `project_layout_schema_drift` (drift de layout em ~25 datasets ANS)
- DAGs envolvidas: `dag_ingest_precificacao_ntrp`, `dag_ingest_vda`, `dag_ingest_regulatorios_complementares`, `dag_ingest_nip`, `dag_ingest_sib`, `dag_ingest_cadop`, `dag_ingest_fip`, `dag_ingest_cnes`.
