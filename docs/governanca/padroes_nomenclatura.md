# Padrões de Nomenclatura

**Versão:** v3.8.0-gov
**Data:** 2026-04-27

---

## Objetivo

Definir convenções obrigatórias de nomenclatura para tabelas, views, colunas, índices, constraints e artefatos dbt na plataforma HealthIntel Suplementar.

---

## Convenções de Nomenclatura por Camada

| Camada | Prefixo | Exemplo | Schema |
|--------|---------|---------|--------|
| Staging | `stg_<dominio>_<entidade>` | `stg_cadop_operadora` | `stg_ans` |
| Intermediate | `int_<dominio>_<processo>` | `int_financeiro_despesa_assistencial` | `int_ans` |
| Fatos | `fat_<dominio>_<grao>` | `fat_financeiro_operadora_mes` | `nucleo_ans` |
| Dimensões | `dim_<entidade>` | `dim_operadora` | `nucleo_ans` |
| Marts | `mart_<dominio>_<visao>` | `mart_operadora_360` | `nucleo_ans` |
| API (ouro/prata) | `api_<dominio>_<grao>` | `api_operadora_360` | `api_ans` |
| API Premium | `api_premium_<dominio>_<entidade>_<status>` | `api_premium_operadora_360_validado` | `api_ans` |
| Consumo | `consumo_<dominio>_<grao>` | `consumo_beneficiarios_operadora_mes` | `consumo_ans` |
| Consumo Premium | `consumo_premium_<dominio>_<entidade>_<status>` | `consumo_premium_operadora_360_validado` | `consumo_premium_ans` |
| MDM público | `mdm_<entidade>_master` | `mdm_operadora_master` | `mdm_ans` |
| MDM privado | `mdm_<entidade>_master` | `mdm_contrato_master` | `mdm_privado` |
| Crosswalk | `xref_<entidade>_<origem>` | `xref_tiss_tuss_procedimento` | `int_ans` / `mdm_ans` |
| Exceção | `*_exception` | `quality_operadora_exception` | `quality_ans` |

### Bruto
- `bruto_ans`: schema único, tabelas com nome do arquivo ANS (ex: `cadop_202501`).

### Plataforma
- Schema `plataforma`, nomes descritivos: `log_uso`, `chave_api`, `plano`, `billing_ciclo`.

---

## Convenções de Índices

| Tipo | Padrão | Exemplo |
|------|--------|---------|
| Primary Key | `pk_<tabela>` | `pk_api_premium_operadora_360_validado` |
| Foreign Key | `fk_<origem>_<destino>` | `fk_mdm_contrato_master_operadora_master` |
| Unique | `uk_<tabela>_<colunas>` | `uk_operadora_master_registro_ans_competencia` |
| Check | `ck_<tabela>_<regra>` | `ck_quality_dataset_score_0_100` |
| Índice | `ix_<tabela>_<colunas>` | `ix_api_operadora_360_competencia` |
| Índice único | `ux_<tabela>_<colunas>` | `ux_xref_tuss_procedimento_codigo_versao` |

---

## Convenções de Testes dbt

| Tipo | Padrão | Exemplo |
|------|--------|---------|
| Singular | `assert_<dominio>_<regra>.sql` | `assert_premium_operadora_tem_mdm.sql` |
| Genérico | `tests/generic/` | `unique`, `not_null`, `accepted_values` |

---

## Convenções de Colunas

| Padrão | Exemplo |
|--------|---------|
| `snake_case` | `razao_social`, `qt_beneficiarios` |
| Prefixo `qt_` para quantidades | `qt_beneficiarios` |
| Prefixo `vl_` para valores monetários | `vl_total` |
| Prefixo `taxa_` para taxas/percentuais | `taxa_aprovacao` |
| Prefixo `pc_` para percentuais normalizados 0-100 | `pc_sinistralidade` |
| Prefixo `dt_` para datas puras | `dt_referencia` |
| Prefixo `is_` para booleanos | `is_ativo`, `is_cnpj_estrutural_valido` |
| Prefixo `_` para campos técnicos | `_carregado_em`, `_hash_arquivo`, `_lote_ingestao` |
| Sufixo `_id` para identificadores | `tenant_id`, `operadora_master_id` |
| Sufixo `_status` para status | `mdm_status`, `documento_quality_status` |
| Sufixo `_score` para scores | `mdm_confidence_score`, `quality_score_documental` |

---

## Regras Obrigatórias

1. **Apenas `snake_case`.** Nada de CamelCase, kebab-case ou espaços.
2. **Evitar abreviação ambígua.** `qt_` é aceito para quantidade; `qtd_` também. `vl_` para valor. Não abreviar `razao_social` para `rz_soc`.
3. **Preservar termos regulatórios conhecidos.** `cadop`, `sib`, `tiss`, `tuss`, `dops` são aceitos como domínio.
4. **Não reutilizar nome físico com semântica diferente.** Se uma tabela mudou de propósito, ela deve ter nome novo.
5. **Prefixo de camada é obrigatório** para staging, intermediate, marts, API, consumo, MDM.
6. **Sufixo de status** (`_validado`, `_consolidado`, `_exception`) deve refletir o estado real do dado.

---

## Macros dbt

| Padrão | Exemplo |
|--------|---------|
| `snake_case` descritivo | `normalizar_cnpj`, `calcular_hhi`, `classificar_rating_regulatorio` |

---

## Seeds e Snapshots

| Tipo | Localização | Exemplo |
|------|-------------|---------|
| Seed | `seeds/` | `ref_tuss.csv`, `ref_rol_procedimento.csv` |
| Snapshot | `snapshots/` | `snap_cadop_operadora` |