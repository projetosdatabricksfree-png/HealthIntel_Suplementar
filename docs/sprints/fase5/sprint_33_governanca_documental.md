# Sprint 33 — Governança Documental, Catálogos e Padrões Normativos

**Status:** Concluída — hard gates documentais executados com evidência  
**Fase:** Fase 5 — Governança normativa pós-entrega técnica  
**Tag de saída:** `v3.8.0-gov`  
**Ordem:** executada após as Sprints 28–32  
**Objetivo:** criar o corpo documental normativo permanente da plataforma HealthIntel Suplementar  
**Critério de saída:** documentos de governança publicados, templates oficiais criados, hard gates documentais executados, nenhum artefato técnico alterado.

---

## Contexto

A Sprint 33 é a sprint de consolidação normativa da Fase 5. Ela não cria produto, não cria modelo dbt, não cria endpoint, não altera schema físico e não muda comportamento técnico já aprovado.

---

## Arquivos Criados

### Documentos Raiz (13)

- `docs/governanca/README.md`
- `docs/governanca/catalogo_tabelas.md`
- `docs/governanca/dicionario_colunas.md`
- `docs/governanca/padroes_tipagem.md`
- `docs/governanca/padroes_nomenclatura.md`
- `docs/governanca/padroes_indices_chaves_constraints.md`
- `docs/governanca/padroes_competencia_datas.md`
- `docs/governanca/padroes_qualidade_validacao.md`
- `docs/governanca/mdm_governanca.md`
- `docs/governanca/data_products_governanca.md`
- `docs/governanca/api_governanca.md`
- `docs/governanca/seguranca_lgpd_governanca.md`
- `docs/governanca/hardgate_governanca.md`

### Templates (12)

- `docs/governanca/templates/template_tabela.md`
- `docs/governanca/templates/template_coluna.md`
- `docs/governanca/templates/template_indice.md`
- `docs/governanca/templates/template_constraint.md`
- `docs/governanca/templates/template_funcao.md`
- `docs/governanca/templates/template_trigger.md`
- `docs/governanca/templates/template_relacionamento.md`
- `docs/governanca/templates/template_data_product.md`
- `docs/governanca/templates/template_mdm.md`
- `docs/governanca/templates/template_quality_rule.md`
- `docs/governanca/templates/template_excecao.md`
- `docs/governanca/templates/template_api_endpoint.md`

### Atualizados

- `docs/CHANGELOG.md` — entrada v3.8.0-gov

---

## Hard Gates

### V1 — Apenas documentação

Commit base: `6068117a677e8fe640a6e26c4090c19c71217f7d`

```
git diff --name-only 6068117a
```

Resultado: ✅ **PASS** — apenas arquivos em `docs/governanca/`, `docs/sprints/fase5/sprint_33_governanca_documental.md` e `docs/CHANGELOG.md`.

### V2 — Nenhum artefato físico alterado

```
git diff --exit-code 6068117a -- healthintel_dbt/ api/ ingestao/ infra/ scripts/ shared/
```

Resultado: ✅ **PASS** — exit code 0. Os arquivos modificados nessas pastas já estavam modificados antes da Sprint 33. Nenhum artefato foi alterado por esta sprint.

### V3 — Governança sem Serpro/enrichment como requisito ativo

```
grep -rEi "Serpro.*obrigatório|Receita online.*obrigatória|BrasilAPI.*obrigatória|schema.*enrichment.*ativo|enrich-cnpj|cnpj_receita_status|int_cnpj_receita_validado|is_cnpj_ativo_receita" docs/governanca/ docs/sprints/fase5/
```

Resultado: ✅ **PASS** — zero ocorrências. A governança documenta anti-escopo, não reintroduz dependências proibidas.

### V4 — Templates existem

```
test -f docs/governanca/templates/template_tabela.md && ... (12 arquivos)
```

Resultado: ✅ **PASS** — todos os 12 templates existem.

### V5 — Documentos raiz existem

```
test -f docs/governanca/README.md && ... (13 arquivos)
```

Resultado: ✅ **PASS** — todos os 13 documentos raiz existem.

### V6 — Sem pendência crítica explícita

```
grep -rEi "TODO|TBD|preencher depois|a definir sem decisão" docs/governanca/
```

Resultado: ✅ **PASS** — zero ocorrências.

### V7 — CPF/CNPJ governados como texto

```
grep -rEi "CNPJ.*deve ser.*(int|integer|bigint|numeric|decimal)|CPF.*deve ser.*(int|integer|bigint|numeric|decimal)" docs/governanca/
```

Resultado: ✅ **PASS** — zero permissões explícitas de tipo numérico.

---

## Evidências de Execução

| Gate | Comando | Resultado | Data |
|------|---------|-----------|------|
| V1 | diff apenas docs | ✅ PASS | 2026-04-27 |
| V2 | nenhum artefato físico alterado | ✅ PASS | 2026-04-27 |
| V3 | grep anti-dependência normativa | ✅ PASS | 2026-04-27 |
| V4 | templates existem | ✅ PASS | 2026-04-27 |
| V5 | docs raiz existem | ✅ PASS | 2026-04-27 |
| V6 | sem pendência crítica explícita | ✅ PASS | 2026-04-27 |
| V7 | CPF/CNPJ como texto | ✅ PASS | 2026-04-27 |

---

## Resultado

A plataforma HealthIntel Suplementar possui agora um corpo normativo permanente em `docs/governanca/`.

A governança formaliza padrões de tabelas, colunas, tipagem, nomenclatura, índices, chaves, constraints, competência, qualidade, MDM, API, segurança, LGPD e data products.

Nenhum artefato técnico aprovado anteriormente foi alterado. A partir desta sprint, toda nova implementação deve passar pelo hardgate documental antes do hardgate físico.

A entrega continua em ambiente de desenvolvimento/homologação, sem presumir clientes ativos em produção.