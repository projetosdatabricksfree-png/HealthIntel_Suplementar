# Catálogo de Tabelas — Padrão Obrigatório

**Versão:** v3.8.0-gov
**Data:** 2026-04-27

---

## Objetivo

Definir o padrão obrigatório para documentar toda tabela da plataforma HealthIntel Suplementar. Toda tabela nova deve ter uma entrada neste catálogo, preenchida conforme o template oficial.

---

## Template de Documentação de Tabela

Cada tabela deve ser documentada com os seguintes campos obrigatórios:

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| **nome_fisico** | Nome físico no PostgreSQL | `api_premium_operadora_360_validado` |
| **schema** | Schema PostgreSQL | `api_ans` |
| **camada** | Camada oficial | `api_ans` |
| **tipo_artefato** | Tabela, view, materialized view, seed, snapshot | `table` |
| **descricao** | Descrição funcional em português | "Operadoras com score 360 validado (documental + MDM + publicação)" |
| **origem** | Fonte primária dos dados | `ANS — CADOP, DIOPS, SIB, TISS` |
| **finalidade** | Propósito de negócio | "Visão 360 de operadoras para consumo premium via API" |
| **granularidade** | Grão da tabela | `Uma linha por operadora por competência` |
| **chave_natural** | Coluna(s) que identificam unicamente no negócio | `registro_ans, competencia` |
| **chave_surrogate** | Surrogate key, se existir | `operadora_master_id` |
| **upstream** | Tabelas fonte (lineage) | `mdm_ans.mdm_operadora_master, quality_ans.quality_operadora_360` |
| **downstream** | Tabelas que consomem esta | `api/app/routers/premium.py → /v1/premium/operadoras` |
| **status_publicacao** | `interno`, `publico`, `premium`, `restrito` | `premium` |
| **sensibilidade_lgpd** | `publico`, `interno`, `restrito`, `pessoal`, `sensivel` | `publico` |
| **owner_tecnico** | Time/pessoa responsável | `Engenharia de Dados` |
| **owner_negocio** | Área de negócio | `Produto HealthIntel` |
| **sla_atualizacao** | Frequência de atualização | `Mensal (até D+5 da competência)` |
| **regra_atualizacao** | `full_refresh`, `incremental`, `snapshot` | `incremental` |
| **regra_retencao** | Política de retenção | `60 competências (5 anos)` |

---

## Template Oficial

Usar o arquivo `templates/template_tabela.md` como base para novas tabelas.

---

## Camadas Oficiais e Schemas

| Camada | Schema | Propósito |
|--------|--------|-----------|
| bruto_ans | `bruto_ans` | Preservação fiel de arquivos originais ANS |
| stg_ans | `stg_ans` | Padronização e tipagem sem perda de origem |
| int_ans | `int_ans` | Transformações intermediárias |
| nucleo_ans | `nucleo_ans` | Fatos e dimensões canônicas |
| quality_ans | `quality_ans` | Validação, scores e exceções |
| mdm_ans | `mdm_ans` | Master Data público |
| api_ans | `api_ans` | Projeções para API (ouro/prata) |
| consumo_ans | `consumo_ans` | Views analíticas públicas para SQL direto |
| bruto_cliente | `bruto_cliente` | Dados brutos do tenant — privado |
| stg_cliente | `stg_cliente` | Padronização de dados do tenant — privado |
| mdm_privado | `mdm_privado` | MDM privado por tenant |
| consumo_premium_ans | `consumo_premium_ans` | Views premium para SQL direto autorizado |
| plataforma | `plataforma` | Logs, billing, chaves, planos |

### Camadas NÃO ativas

- **enrichment**: não é camada ativa. Reativação exige ADR.
- Qualquer nova camada exige ADR, hard gate e atualização deste catálogo.

---

## Status de Publicação

| Status | Descrição | Quem acessa |
|--------|-----------|-------------|
| **interno** | Uso exclusivo da plataforma | Engenharia |
| **publico** | Disponível em API pública (plano ouro/prata) | Todos os planos |
| **premium** | Disponível apenas para plano premium | Plano premium |
| **restrito** | Dados de tenant, nunca público | Tenant autenticado |

---

## Regras

1. Toda tabela nova deve ser documentada antes do merge em main.
2. Documentação deve estar em `docs/governanca/` ou no `dbt_project.yml` com `description`.
3. Schema físico deve corresponder exatamente ao documentado.
4. Mudança de schema ou camada exige atualização deste catálogo.
5. Tabela sem documentação é blocking para release.

---

## Exemplo Preenchido

### `api_ans.api_premium_operadora_360_validado`

| Campo | Valor |
|-------|-------|
| nome_fisico | `api_premium_operadora_360_validado` |
| schema | `api_ans` |
| camada | `api_ans` |
| tipo_artefato | `table` |
| descricao | Operadoras com score 360 validado — documental + MDM + publicação |
| origem | ANS — CADOP, DIOPS, SIB, TISS; quality_ans; mdm_ans |
| finalidade | Visão 360 de operadoras para consumo premium via API |
| granularidade | Uma linha por operadora por competência |
| chave_natural | `registro_ans, competencia` |
| chave_surrogate | `operadora_master_id` |
| upstream | `mdm_ans.mdm_operadora_master`, `quality_ans.quality_operadora_360` |
| downstream | `api/app/routers/premium.py → /v1/premium/operadoras` |
| status_publicacao | `premium` |
| sensibilidade_lgpd | `publico` |
| owner_tecnico | Engenharia de Dados |
| owner_negocio | Produto HealthIntel |
| sla_atualizacao | Mensal (até D+5) |
| regra_atualizacao | `incremental` |
| regra_retencao | 60 competências |