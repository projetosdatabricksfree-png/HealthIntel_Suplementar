# Sprint 28 — Validação Determinística de CNPJ (Offline)

**Status:** Implementada — pendente evidências de hard gates.  
**Fase:** Fase 5 — Qualidade, Governança e MDM sem dependência externa.  
**Pré-requisito:** Sprint 27 com hardgates verdes.  
**Baseline congelado:** `v3.0.0`. **Não alterado por esta sprint.**  
**Schemas utilizados:** `quality_ans` (existentes). Nenhum schema novo é criado.  
**Objetivo:** validação estrutural, matemática e referencial interna de CNPJ, 100% offline, determinística e sem dependência externa.  
**Fim esperado:** macro centralizada de classificação de CNPJ, modelos `dq_*` refatorados, testes de formato/sequência (error), dígito verificador (warn), consistência referencial CADOP×operadora (error), auditoria de razão social divergente (não-bloqueante), ADR formal e documentação atualizada.

## Regra-mãe (não negociável)

- [x] CI roda sem internet, sem token, sem segredo e sem e-CNPJ.
- [x] Nenhuma chamada HTTP em macros, modelos ou testes dbt (proibido `requests`, `httpx`, `urlopen`, `http_get`).
- [x] Nenhum provider externo (SerproCnpjProvider), job de enriquecimento, schema `enrichment`, cache externo ou variável de ambiente de API.
- [x] CNPJ permanece como `varchar`/`text` de 14 dígitos, nunca `bigint` ou `int`.
- [x] Warnings de dígito verificador inválido são aceitos — fontes públicas externas podem conter CNPJs de demonstração/fictícios. O job de CI desta sprint **não** deve executar `dbt test` ou `dbt build` com `--warn-error` para testes tagueados como `documento_warning`.

## Contrato Arquitetural da Sprint

| Item | Valor |
|------|-------|
| Camada utilizada | `quality_ans` (existente, Sprint 27). Nenhuma camada nova é criada. |
| Schemas físicos | `quality_ans` (modelos `dq_*` + auditoria). |
| Tags dbt | `quality`, `documento`, `cnpj`, `cadop`, `operadora`, `cnes`, `audit`, `documento_warning`. |
| Materialização | `table` para modelos `dq_*` e `audit_*`; testes singulares. |
| Upstream | `stg_cadop`, `stg_cnes_estabelecimento`, `dim_operadora_atual`. |
| Downstream | Sprint 29 (MDM), Sprint 31 (produtos premium). |
| Owner técnico | Engenharia de dados HealthIntel. |
| Owner de negócio | Produto HealthIntel. |
| Regra de publicação | Interna. `quality_ans` não é exposto diretamente via FastAPI ou `consumo_ans`. |
| Regra de teste | `dbt test` com zero `error`; `warn` aceito para dígito verificador. |
| Regra de rollback | Remover arquivos novos desta sprint; modelos `dq_*` podem reverter ao estado anterior sem perda de baseline. |

## Entregas

### 1. Macro Centralizada de Classificação de CNPJ

**Arquivo:** `healthintel_dbt/macros/validar_cnpj_completo.sql`  
**Responsabilidade:** retornar o status de qualidade documental de um CNPJ com base em validações locais.

Status retornados:

| Status | Condição |
|--------|----------|
| `NULO` | CNPJ normalizado é nulo |
| `SEQUENCIA_INVALIDA` | CNPJ composto por sequência repetida (ex: `00000000000000`) |
| `INVALIDO_FORMATO` | CNPJ normalizado com tamanho diferente de 14 dígitos |
| `INVALIDO_DIGITO` | CNPJ com dígito verificador inválido |
| `VALIDO` | CNPJ passa em todas as validações |

A macro reutiliza `normalizar_cnpj` e `validar_cnpj_digito` existentes.

### 2. Modelos `dq_*` Refatorados

**Arquivos:** `dq_cadop_documento.sql`, `dq_cnes_documento.sql`, `dq_operadora_documento.sql`  
**Mudança:** a classificação `documento_quality_status` agora é delegada a `validar_cnpj_completo`, eliminando lógica duplicada. As colunas técnicas `cnpj_tamanho_valido`, `cnpj_digito_valido` e `cnpj_is_sequencia_invalida` são preservadas como colunas analíticas. `motivo_invalidade_documento` é derivado via CTE `classificado` para evitar erro de alias SQL.

### 3. Testes dbt

| Arquivo | Severity | Escopo |
|---------|----------|--------|
| `assert_cnpj_formato_sequencia_valido_em_modelos.sql` | `error` | CNPJ com tamanho ≠ 14 ou sequência repetida (ignora nulo) |
| `assert_cnpj_digito_invalido_em_modelos.sql` | `warn` | CNPJ com dígito verificador inválido (ignora nulo); consolidado sobre `dq_cadop_documento`, `dq_operadora_documento` e `dq_cnes_documento` |
| `assert_operadora_cnpj_divergente_cadop.sql` | `error` | CNPJ divergente entre `dim_operadora_atual` e CADOP/ANS |

> Os testes antigos `assert_cnpj_digito_valido_cadop.sql` e `assert_cnpj_digito_valido_cnes.sql` foram removidos após a criação do teste consolidado `assert_cnpj_digito_invalido_em_modelos.sql`, evitando duplicidade de warnings e mantendo uma única fonte de validação para dígito verificador de CNPJ.

### 4. Modelo de Auditoria (Não-Bloqueante)

**Arquivo:** `healthintel_dbt/models/quality/audit_operadora_razao_social_divergente_cadop.sql`  
**Materialização:** `table` em `quality_ans`.  
**Responsabilidade:** expor divergências de razão social entre a dimensão de operadora e a fonte CADOP/ANS quando o CNPJ é idêntico. **Não há teste dbt vinculado** — este modelo é apenas para inspeção humana. Evita falsos positivos por acentuação, abreviação (LTDA/SA/S.A.) ou variação textual.

### 5. ADR — Decisão Arquitetural

**Arquivo:** `docs/arquitetura/decisao_validacao_cnpj_offline.md`  
Documenta formalmente a decisão de manter validação 100% offline, as alternativas rejeitadas e o backlog futuro.

### 6. Documentação Atualizada

| Arquivo | Mudança |
|---------|---------|
| `docs/sprints/fase5/sprint_28_validacao_receita_serpro_cache.md` | Marcado como **OBSOLETO** |
| `docs/sprints/fase5/README.md` | Sprint 28 renomeada; `enrichment` removido das camadas |
| `docs/sprints/fase5/governanca_minima_fase5.md` | Schema `enrichment` removido; bloco `dbt_project.yml` simplificado |

---

## Anti-escopo Explícito (o que NÃO é feito nesta sprint)

| Item | Justificativa |
|------|---------------|
| Serpro (API oficial) | Custo recorrente, dependência de rede, quebra determinismo do CI. |
| Receita Federal online | Mesmo problema do Serpro; e-CNPJ inviabiliza CI. |
| BrasilAPI | API gratuita como hard gate introduz dependência externa e instabilidade. |
| Scraping | Risco legal e fragilidade técnica. |
| Schema `enrichment` | Fora do escopo; sem cache externo. |
| Pipeline de enriquecimento (`make enrich-cnpj`) | Sem chamada externa; sem job dedicado. |
| Provider Python (`SerproCnpjProvider`, `MockCnpjProvider`) | Desnecessário. |
| Variáveis de ambiente de API externa | `SERPRO_*`, `BRASIL_API_*`, `HEALTHINTEL_CNPJ_PROVIDER` não existem. |
| `--warn-error` para dígito verificador | Warnings são aceitos; CI não deve usar `--warn-error` para `documento_warning`. |

---

## Backlog Futuro

Uma sprint opcional futura pode realizar **ingestão offline dos dados abertos de CNPJ da Receita Federal** (arquivos CSV públicos disponibilizados periodicamente pela RFB), sem dependência de API online, sem token, sem segredo e sem custo recorrente. Esta sprint não bloqueia o MVP e não faz parte da Sprint 28.

---

## Hard Gates

Cada item exige evidência objetiva antes de considerar a sprint concluída.

- [x] `grep -rE "requests|httpx|urlopen|http_get" healthintel_dbt/models/ healthintel_dbt/macros/ healthintel_dbt/tests/` retorna vazio.
- [x] `grep -rEi "SerproCnpjProvider|SERPRO_|BRASIL_API|brasilapi|documento_receita_cache|schema.*enrichment" healthintel_dbt/ infra/ scripts/ Makefile` retorna vazio.
- [x] `grep -rEi "cnpj[^,\n]*\b(bigint|integer|int)\b" healthintel_dbt/models/ healthintel_dbt/macros/ healthintel_dbt/tests/ --exclude-dir=target --exclude-dir=dbt_packages` retorna vazio.
- [x] `dbt compile` zero erros.
- [x] `dbt build` zero erros.
- [x] `dbt test` zero falhas `error`; warnings aceitos.

### Atenção para CI com `set -e`

`grep` sem matches retorna exit code 1. Em scripts com `set -e`, usar:

```bash
if grep -rE "requests|httpx|urlopen|http_get" healthintel_dbt/models/ healthintel_dbt/macros/ healthintel_dbt/tests/; then
  echo "ERRO: chamada HTTP encontrada no dbt"
  exit 1
fi
```

---

## Resultado Esperado

A Sprint 28 entrega validação determinística de CNPJ sem qualquer dependência externa. O `dbt build` e `dbt test` permanecem 100% offline. A macro `validar_cnpj_completo` torna-se a fonte única de verdade para classificação de CNPJ no projeto. Divergências estruturais são hard gates; divergências de dígito verificador são warnings; divergências de razão social são materializadas para auditoria humana. Nenhum custo Serpro, nenhuma API externa, nenhum schema `enrichment`.

---

## Evidências de Execução

| Gate | Comando | Resultado | Data |
|------|---------|-----------|------|
| V1 | `grep -rE "requests\|httpx\|urlopen\|http_get" healthintel_dbt/models/ healthintel_dbt/macros/ healthintel_dbt/tests/` | PASS | 2026-04-27 |
| V2 | `grep -rEi "SerproCnpjProvider\|SERPRO_\|BRASIL_API\|brasilapi\|documento_receita_cache\|schema.*enrichment" healthintel_dbt/ infra/ scripts/ Makefile` | PASS | 2026-04-27 |
| V3 | `grep -rEi "cnpj[^,\n]*\b(bigint\|integer\|int)\b" healthintel_dbt/models/ healthintel_dbt/macros/ healthintel_dbt/tests/ --exclude-dir=target --exclude-dir=dbt_packages` | PASS | 2026-04-27 |
| V4 | `dbt compile` | PASS (0 erros) | 2026-04-27 |
| V5 | `dbt build` | PASS=389, WARN=1, ERROR=0 | 2026-04-27 |
| V6 | `dbt test` | PASS=389, WARN=1 (`assert_cnpj_digito_invalido_em_modelos`), ERROR=0 | 2026-04-27 |
