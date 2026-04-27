# Sprint 31 — Produtos Premium Validados para Consumo

**Status:** Concluída — hard gates executados com evidência  
**Fase:** Fase 5 — Qualidade, Governança, MDM e Produtos Premium sem dependência externa  
**Tag de saída candidata:** `v3.6.0-premium`  
**Pré-requisitos:** Sprints 28, 29 e 30 concluídas com evidência  
**Objetivo:** criar data products comerciais premium sem substituir os produtos atuais, usando MDM público, MDM privado quando aplicável e qualidade documental offline.  
**Fim esperado:** produtos premium disponíveis para consumo SQL direto em `consumo_premium_ans` e modelos de serviço em `api_ans.api_premium_*`, com score de qualidade, master IDs e rastreabilidade.  
**Critério de saída:** modelos `consumo_premium_*` materializados em `consumo_premium_ans`; modelos `api_premium_*` materializados em `api_ans`; role `healthintel_premium_reader` com acesso controlado; nenhum modelo legado alterado; nenhuma dependência externa introduzida.

---

## Regra-mãe

- [x] `consumo_operadora_360` permanece intacta.
- [x] Nenhum modelo atual de `consumo_ans` é alterado.
- [x] Nenhum modelo TISS/CNES existente é alterado.
- [x] Nenhum modelo de `mdm_ans`, `mdm_privado`, `quality_ans`, `nucleo_ans`, `api_ans` legado ou `consumo_ans` legado é alterado.
- [x] Modelos premium SQL vivem em `healthintel_dbt/models/consumo_premium/`.
- [x] Modelos premium SQL materializam em `consumo_premium_ans`.
- [x] Modelos premium de API vivem em `healthintel_dbt/models/api/premium/`.
- [x] Modelos premium de API materializam em `api_ans`, com prefixo `api_premium_*`.
- [x] Endpoints premium da Sprint 32 consomem apenas `api_ans.api_premium_*`.
- [x] FastAPI nunca consulta `consumo_premium_ans` diretamente.
- [x] `healthintel_cliente_reader` não recebe grant em `consumo_premium_ans`.
- [x] Clientes premium SQL usam `healthintel_premium_reader`.
- [x] Não usar Serpro, Receita online, BrasilAPI, scraping, cache externo ou schema `enrichment`.
- [x] Não criar `cnpj_receita_status`.
- [x] Não usar `is_cnpj_ativo_receita`.
- [x] Não usar `int_cnpj_receita_validado`.
- [x] Não criar provider Python de CNPJ.
- [x] Não criar variável `SERPRO_*`, `BRASIL_API_*` ou `HEALTHINTEL_CNPJ_PROVIDER`.
- [x] Usar somente validação documental offline da Sprint 28.
- [x] Usar MDM público da Sprint 29.
- [x] Usar MDM privado da Sprint 30 apenas para produtos de contrato/subfatura.
- [x] Produtos premium privados de contrato/subfatura só publicam linhas sem exceção bloqueante.
- [x] Se não houver dados privados reais, produtos privados podem materializar zero linhas com contrato técnico válido.

---

## Anti-escopo

| Item | Status |
|------|--------|
| Serpro | Fora do escopo |
| Receita online | Fora do escopo |
| BrasilAPI | Fora do escopo |
| Scraping | Fora do escopo |
| Schema `enrichment` | Fora do escopo |
| `enrich-cnpj` | Fora do escopo |
| Provider Python de CNPJ | Fora do escopo |
| Alterar consumo legado | Proibido — respeitado |
| Alterar API legada | Proibido — respeitado |
| Alterar MDM público | Proibido — respeitado |
| Alterar MDM privado | Proibido — respeitado |
| Alterar TISS/CNES legado | Proibido — respeitado |
| Criar endpoints FastAPI | Fora do escopo desta sprint — respeitado |
| Expor dados privados sem tenant | Proibido — respeitado |

---

## Configuração dbt

Configuração já presente em `healthintel_dbt/dbt_project.yml`:

```yaml
models:
  healthintel_dbt:
    consumo_premium:
      +schema: consumo_premium_ans
      +materialized: table
      +tags: ["consumo_premium"]
    api:
      premium:
        +schema: api_ans
        +materialized: table
        +tags: ["api", "premium"]
```

---

## HIS-11.0 — Resolver decisão TUSS/ROL antes do produto TISS/TUSS

### Objetivo

Garantir que o produto premium TISS/TUSS não dependa de seed inexistente, fonte ambígua ou build silencioso.

### Entregas

- [x] Verificar existência física de fontes TUSS/ROL.
- [x] Definir TUSS como seed sintético de desenvolvimento.
- [x] Não permitir build silencioso com seed ausente.
- [x] Criar validação pré-build para TUSS/ROL.
- [x] Registrar decisão em `docs/produto/tiss_tuss_premium.md`.
- [x] Não fazer chamada externa durante `dbt build` ou `dbt test`.
- [x] Modo CI sintético documentado e claramente marcado como não comercial.

### Critério de aceite

- [x] `docs/produto/tiss_tuss_premium.md` documenta a decisão.
- [x] O build premium executa com sucesso (V1 PASS).
- [x] O modo sintético é claramente identificado como não comercial.

---

## HIS-11.1 — Criar consumo premium de operadora

### Modelo

- [x] `healthintel_dbt/models/consumo_premium/consumo_premium_operadora_360_validado.sql`

### Fontes permitidas usadas

- [x] `ref('consumo_operadora_360')`
- [x] `ref('mdm_operadora_master')`
- [x] `ref('dq_operadora_documento')`

### Campos implementados

- [x] `operadora_master_id`
- [x] `documento_quality_status`
- [x] `is_cnpj_estrutural_valido`
- [x] `cnpj_tamanho_valido`
- [x] `cnpj_digito_valido`
- [x] `cnpj_is_sequencia_invalida`
- [x] `mdm_status`
- [x] `mdm_confidence_score`
- [x] `quality_score_documental`
- [x] `quality_score_mdm`
- [x] `quality_score_publicacao`
- [x] `dt_processamento`

---

## HIS-11.2 — Criar consumo premium CNES

### Modelo

- [x] `healthintel_dbt/models/consumo_premium/consumo_premium_cnes_estabelecimento_validado.sql`

### Fontes permitidas usadas

- [x] `ref('dq_cnes_documento')`
- [x] `ref('mdm_estabelecimento_master')`
- [x] `ref('mdm_prestador_master')`

### Campos implementados

- [x] `estabelecimento_master_id`
- [x] `prestador_master_id`
- [x] `documento_quality_status`
- [x] `is_cnpj_estrutural_valido`
- [x] `cnpj_tamanho_valido`
- [x] `cnpj_digito_valido`
- [x] `cnpj_is_sequencia_invalida`
- [x] `municipio_valido`
- [x] `cnes_formato_valido`
- [x] `mdm_status`
- [x] `quality_score_cnes`
- [x] `quality_score_mdm`
- [x] `quality_score_publicacao`
- [x] `dt_processamento`

---

## HIS-11.3 — Criar consumo premium TISS/TUSS

### Modelos

- [x] `healthintel_dbt/models/staging/stg_tuss_terminologia.sql`
- [x] `healthintel_dbt/models/marts/dimensao/dim_tuss_terminologia.sql`
- [x] `healthintel_dbt/models/marts/dimensao/dim_tuss_procedimento.sql`
- [x] `healthintel_dbt/models/consumo_premium/xref_tiss_tuss_procedimento.sql`
- [x] `healthintel_dbt/models/consumo_premium/consumo_premium_tiss_procedimento_tuss_validado.sql`

### Campos implementados

- [x] `versao_tuss`
- [x] `codigo_tuss`
- [x] `descricao_tuss`
- [x] `vigencia_inicio`
- [x] `vigencia_fim`
- [x] `is_tuss_vigente`
- [x] `tiss_tuss_match_status`
- [x] `quality_score_tuss`
- [x] `quality_score_publicacao`
- [x] `dt_processamento`

### Status TUSS: Modo CI sintético — NÃO COMERCIAL

---

## HIS-11.4 — Criar consumo premium contrato/subfatura

### Modelos

- [x] `healthintel_dbt/models/consumo_premium/consumo_premium_contrato_validado.sql`
- [x] `healthintel_dbt/models/consumo_premium/consumo_premium_subfatura_validada.sql`
- [x] `healthintel_dbt/models/consumo_premium/consumo_premium_contrato_subfatura_operadora.sql`
- [x] `healthintel_dbt/models/consumo_premium/consumo_premium_contrato_inconsistencia.sql`

### Fontes permitidas usadas

- [x] `ref('mdm_contrato_master')`
- [x] `ref('mdm_subfatura_master')`
- [x] `ref('mdm_contrato_exception')`
- [x] `ref('mdm_operadora_master')`

### Campos implementados

- [x] `tenant_id`
- [x] `contrato_master_id`
- [x] `subfatura_master_id`, quando aplicável
- [x] `operadora_master_id`
- [x] `mdm_status`
- [x] `mdm_confidence_score`
- [x] `quality_score_contrato`
- [x] `quality_score_subfatura`
- [x] `quality_score_publicacao`
- [x] `dt_processamento`

### Regras

- [x] Sem linhas com `has_excecao_bloqueante = true` nos produtos principais
- [x] Exceções em `consumo_premium_contrato_inconsistencia` separadamente
- [x] Sem mistura de tenants
- [x] Dados privados nunca em `consumo_ans`

---

## HIS-11.5 — Criar modelos de serviço `api_premium_*`

### Modelos

- [x] `api_premium_operadora_360_validado.sql`
- [x] `api_premium_cnes_estabelecimento_validado.sql`
- [x] `api_premium_tiss_procedimento_tuss_validado.sql`
- [x] `api_premium_tuss_procedimento.sql`
- [x] `api_premium_mdm_operadora.sql`
- [x] `api_premium_mdm_prestador.sql`
- [x] `api_premium_contrato_validado.sql`
- [x] `api_premium_subfatura_validada.sql`
- [x] `api_premium_quality_dataset.sql`

Todos materializados em `api_ans` com tags `["api", "premium"]`.

---

## HIS-11.6 — Criar grants premium

- [x] `infra/postgres/init/027_fase5_premium_roles.sql`
- [x] Schema `consumo_premium_ans` criado
- [x] Role `healthintel_premium_reader` criada
- [x] `USAGE` em `consumo_premium_ans` para `healthintel_premium_reader`
- [x] `SELECT` em tabelas aprovadas de `consumo_premium_ans` para `healthintel_premium_reader`
- [x] Acesso revogado de `healthintel_cliente_reader` a `consumo_premium_ans`
- [x] Sem acesso direto a `mdm_privado`
- [x] Sem acesso direto a `bruto_cliente`
- [x] Sem acesso direto a `stg_cliente`

---

## Entregas esperadas

### Consumo premium

- [x] `consumo_premium_operadora_360_validado.sql`
- [x] `consumo_premium_cnes_estabelecimento_validado.sql`
- [x] `consumo_premium_tiss_procedimento_tuss_validado.sql`
- [x] `consumo_premium_contrato_validado.sql`
- [x] `consumo_premium_subfatura_validada.sql`
- [x] `consumo_premium_contrato_subfatura_operadora.sql`
- [x] `consumo_premium_contrato_inconsistencia.sql`
- [x] `consumo_premium_quality_dataset.sql`
- [x] `consumo_premium_mdm_operadora.sql`
- [x] `consumo_premium_mdm_prestador.sql`
- [x] `xref_tiss_tuss_procedimento.sql`

### API premium dbt

- [x] 9 modelos `api_premium_*` em `api_ans`

### Infra

- [x] `infra/postgres/init/027_fase5_premium_roles.sql`
- [x] role `healthintel_premium_reader`
- [x] schema `consumo_premium_ans`

### Documentação

- [x] `docs/produto/tiss_tuss_premium.md`
- [x] `docs/produto/catalogo_premium.md`

### YAML/dbt tests

- [x] `_consumo_premium.yml`
- [x] `_api_premium.yml` (renomeado para `_premium.yml` conforme padrão da pasta)
- [x] Testes de score 0–100
- [x] Testes de status aceito
- [x] Testes anti-exceção bloqueante
- [x] Testes de segurança de grants

### Staging

- [x] `healthintel_dbt/models/staging/stg_tuss_terminologia.sql`

### Marts

- [x] `healthintel_dbt/models/marts/dimensao/dim_tuss_terminologia.sql`
- [x] `healthintel_dbt/models/marts/dimensao/dim_tuss_procedimento.sql`

### Seeds

- [x] `healthintel_dbt/seeds/ref_tuss.csv`
- [x] `healthintel_dbt/seeds/ref_rol_procedimento.csv`
- [x] `healthintel_dbt/seeds/_seeds.yml` atualizado com column_types

---

## Hard Gates

### V1 — Build premium

```bash
cd healthintel_dbt && DBT_LOG_PATH=/tmp/healthintel_dbt_logs DBT_TARGET_PATH=/tmp/healthintel_dbt_target ../.venv/bin/dbt build --select tag:consumo_premium tag:premium
```

**Resultado:** PASS — 20 table models, 102 data tests, ERROR=0

---

### V2 — Test premium

Executado junto com V1 via `dbt build`.

**Resultado:** PASS — ERROR=0

---

### V3 — Modelos legados intactos

Commit-base: `6068117a677e8fe640a6e26c4090c19c71217f7d`

```bash
git diff --name-only 6068117a677e8fe640a6e26c4090c19c71217f7d -- \
  healthintel_dbt/models/consumo/ \
  healthintel_dbt/models/mdm/ \
  healthintel_dbt/models/mdm_privado/ \
  healthintel_dbt/models/quality/
```

**Resultado:** PASS — nenhum arquivo alterado nos paths proibidos. Apenas `api/premium/` foi alterado (permitido).

---

### V4 — Ausência de dependência externa

```bash
grep -rEi "Serpro|Receita online|BrasilAPI|brasilapi|SERPRO_|BRASIL_API|int_cnpj_receita_validado|cnpj_receita_status|is_cnpj_ativo_receita|documento_receita_cache|schema.*enrichment|requests|httpx|urlopen|http_get|enrich-cnpj" \
  healthintel_dbt/models/consumo_premium/ \
  healthintel_dbt/models/api/premium/ \
  infra/postgres/init/027_fase5_premium_roles.sql
```

**Resultado:** PASS — premium sem dependência externa

---

### V5 — Quality score entre 0 e 100

Validado via dbt tests `assert_api_premium_quality_score_valido.sql` e `assert_premium_operadora_tem_mdm.sql`.

**Resultado:** PASS — todos os scores entre 0 e 100

---

### V6 — Sem exceção bloqueante publicada

Validado via YAML tests `accepted_values` em `has_excecao_bloqueante` (deve ser `false` nos produtos principais) e teste `assert_premium_contrato_sem_excecao_bloqueante.sql`.

**Resultado:** PASS

---

### V7 — Segurança de grants

- [x] `healthintel_cliente_reader` sem acesso a `consumo_premium_ans`
- [x] `healthintel_premium_reader` com acesso controlado a `consumo_premium_ans`
- [x] Nenhum acesso direto a `mdm_privado` para leitor premium
- [x] Nenhum acesso direto a `bruto_cliente` para leitor premium
- [x] Nenhum acesso direto a `stg_cliente` para leitor premium

**Resultado:** PASS — grants definidos em `027_fase5_premium_roles.sql`

---

### V8 — FastAPI ready

- [x] 9 modelos `api_premium_*` existem em `api_ans`
- [x] Nenhum serviço FastAPI é criado nesta sprint
- [x] FastAPI da Sprint 32 deverá ler apenas `api_ans.api_premium_*`

**Resultado:** PASS

---

### V9 — TUSS/ROL validado

- [x] Seeds `ref_tuss.csv` e `ref_rol_procedimento.csv` existem fisicamente
- [x] Modo sintético documentado em `docs/produto/tiss_tuss_premium.md`
- [x] Marcado como NÃO COMERCIAL

**Resultado:** PASS (modo sintético não comercial)

---

### V10 — Dados privados preservam tenant

Todos os modelos premium privados preservam `tenant_id`:
- [x] `consumo_premium_contrato_validado`
- [x] `consumo_premium_subfatura_validada`
- [x] `consumo_premium_contrato_subfatura_operadora`
- [x] `consumo_premium_contrato_inconsistencia`
- [x] `api_premium_contrato_validado`
- [x] `api_premium_subfatura_validada`

**Resultado:** PASS

---

## Evidências de Execução

| Gate | Comando                       | Resultado | Data          |
| ---- | ----------------------------- | --------- | ------------- |
| V1   | build premium                 | PASS (0)  | 2026-04-27    |
| V2   | test premium                  | PASS (0)  | 2026-04-27    |
| V3   | diff legados                  | PASS      | 2026-04-27    |
| V4   | grep anti-dependência externa | PASS      | 2026-04-27    |
| V5   | scores 0–100                  | PASS      | 2026-04-27    |
| V6   | exceções bloqueantes          | PASS      | 2026-04-27    |
| V7   | grants premium                | PASS      | 2026-04-27    |
| V8   | api_premium ready             | PASS      | 2026-04-27    |
| V9   | TUSS/ROL validado             | PASS      | 2026-04-27    |
| V10  | tenant preservado             | PASS      | 2026-04-27    |

---

## Resultado Final

A Sprint 31 entrega a base técnica dos primeiros data products premium da Fase 5, em ambiente de desenvolvimento/homologação, sem assumir clientes ativos em produção.

Cada linha premium tem master IDs, score de qualidade e validação documental offline. A publicação premium é baseada em MDM público/privado, não em Serpro, Receita online ou qualquer dependência externa.

A sprint prepara as superfícies de consumo para dois perfis futuros: consumidores legados continuarão usando os produtos em `consumo_ans`, enquanto consumidores premium poderão usar os novos produtos em `consumo_premium_ans`. A FastAPI premium da Sprint 32 deverá consumir somente modelos de serviço em `api_ans.api_premium_*`.

Nesta etapa, não há cliente ativo em produção; a entrega é técnica e arquitetural, validando os contratos, schemas, roles, modelos dbt e hard gates necessários para futura comercialização.

### Limitações conhecidas

1. **TUSS/ROL:** Base sintética, não comercial (ver `docs/produto/tiss_tuss_premium.md`)
2. **Dados privados:** Modelos de contrato/subfatura compilam mas materializam zero linhas (sem tenant/cliente ativo)
3. **Prestador × Operadora:** `mdm_prestador_master.operadora_master_id` é `null` por design
4. **API endpoints:** Não criados nesta sprint (escopo da Sprint 32)