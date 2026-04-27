# Plano de Correção Pós-Auditoria — Fase 5

**Commit-base:** `64ca4e4ef8a28ffb85adcc00d5408224e6dde167`  
**Branch:** `main`  
**Data:** 2026-04-27  
**Auditor:** Claude Opus 4.7 — auditoria técnica autônoma  
**Status final:** ✅ PRONTO PARA HOMOLOGAÇÃO

---

## Estado Inicial (pré-auditoria)

- Working tree: limpo (`nothing to commit`)
- Arquivos modificados antes das correções: nenhum

---

## Inventário de Achados

| # | Achado | Status |
|---|--------|--------|
| A1 | `docs/auditoria/` inexistente | CORRIGIDO |
| A2 | `make test` invoca `pytest` de sistema (sem pytest-asyncio) → 14 falhas | CORRIGIDO |
| A3 | `pyproject.toml` sem `asyncio_mode = "auto"` | CORRIGIDO |
| A4 | Padrões proibidos em código-fonte (Serpro/BrasilAPI/enrichment) | NÃO CONFIRMADO (falsos positivos) |
| A5 | CNPJ/CPF como tipo numérico em modelos | NÃO CONFIRMADO (somente em `target/` compilado) |
| A6 | Chamadas HTTP externas em modelos dbt | NÃO CONFIRMADO (somente em API→layoutservice, smoke scripts, ELT) |
| A7 | `sprint_28_validacao_receita_serpro_cache.md` ativo sem marcação | NÃO CONFIRMADO (header OBSOLETO presente) |
| A8 | `dbt_project.yml` sem config de Fase 5 | NÃO CONFIRMADO (todos os schemas configurados) |
| A9 | Modelos MDM público ausentes | NÃO CONFIRMADO (10 arquivos presentes) |
| A10 | Modelos MDM privado ausentes | NÃO CONFIRMADO (9 arquivos + SQL RLS presentes) |
| A11 | Modelos consumo_premium ausentes | NÃO CONFIRMADO (12 modelos presentes) |
| A12 | Modelos api/premium ausentes | NÃO CONFIRMADO (9 modelos + YAML presentes) |
| A13 | Router premium não registrado em main.py | NÃO CONFIRMADO (registrado em linha 61) |
| A14 | FastAPI premium consultando schemas não-api_ans | NÃO CONFIRMADO (somente `api_ans.api_premium_*`) |
| A15 | Rotas privadas sem exigência de tenant | NÃO CONFIRMADO (helper `_obter_tenant_id` retorna 403) |
| A16 | docs/governanca/ inexistente | NÃO CONFIRMADO (13 docs + 12 templates presentes) |
| A17 | infra/postgres/init/027 e 028 ausentes | NÃO CONFIRMADO (ambos presentes) |

---

## Correções Aplicadas

### C1 — `asyncio_mode = "auto"` em pyproject.toml

**Arquivo:** `pyproject.toml`  
**Razão:** pytest-asyncio 0.26.0 exige declaração explícita de modo. Sem isso, 14 testes async falhavam com "async def functions are not natively supported" ao usar sistema de pytest.  
**Resultado:** 104/104 testes passam com `make test`.

```diff
 [tool.pytest.ini_options]
 pythonpath = [".", "shared/python"]
 testpaths = ["api/tests", "ingestao/tests", "testes"]
+asyncio_mode = "auto"
```

### C2 — `make test` usa `.venv/bin/pytest`

**Arquivo:** `Makefile`  
**Razão:** O target `test:` chamava `pytest` do PATH do sistema, que não tem pytest-asyncio instalado. O venv tem a versão correta.  
**Resultado:** `make test` passa 104/104.

```diff
 PYTHON ?= python
+PYTEST_BIN := .venv/bin/pytest
...
 test:
-    pytest
+    $(PYTEST_BIN)
```

### C3 — Criação de `docs/auditoria/`

**Arquivo:** `docs/auditoria/plano_correcao_pos_auditoria_fase5.md` (este documento)  
**Razão:** Diretório inexistente; exigido pelo processo de auditoria.

---

## Achados Falsos Positivos

| Achado | Classificação | Justificativa |
|--------|---------------|---------------|
| Grep de `Serpro/BrasilAPI` em `.md` | Referência histórica/anti-escopo | Docs sprint explicam **por que** não usar; não são instruções operacionais |
| `cnpj.*integer` em `target/` | Artefato compilado | `target/compiled/` é output do dbt, não código-fonte. Source SQL usa `cast(... as text)` |
| `httpx` em `api/app/routers/admin_layout.py` | Anti-escopo aceito | API→Layout Service via HTTP interno (porta 8001) — necessário e documentado |
| `httpx` em `ingestao/app/elt/` | Anti-escopo aceito | Download de arquivos ANS públicos — propósito legítimo do ELT |

---

## Hard Gates Executados

| Gate | Comando | Resultado | Data |
|------|---------|-----------|------|
| G1 | dbt debug | ✅ PASS — connection ok | 2026-04-27 |
| G2 | dbt compile (182 modelos) | ✅ PASS — exit 0 | 2026-04-27 |
| G3 | ruff check api/ ingestao/ scripts/ shared/ testes/ | ✅ PASS — All checks passed | 2026-04-27 |
| G4 | make test (104 testes) | ✅ PASS — 104 passed | 2026-04-27 |
| G5 | grep padrões proibidos em source | ✅ PASS — zero hits em código-fonte | 2026-04-27 |
| G6 | grep HTTP em modelos dbt | ✅ PASS — zero hits em models/ | 2026-04-27 |
| G7 | grep CNPJ/CPF como int em source | ✅ PASS — zero hits em source | 2026-04-27 |
| G8 | Premium lê somente api_ans.api_premium_* | ✅ PASS — verificado em services/premium.py | 2026-04-27 |
| G9 | Tenant obrigatório em rotas privadas | ✅ PASS — helper _obter_tenant_id retorna 403 | 2026-04-27 |
| G10 | RLS em bruto_cliente c/ FORCE | ✅ PASS — 028_fase5_mdm_privado_rls.sql | 2026-04-27 |
| G11 | healthintel_cliente_reader sem acesso a consumo_premium_ans | ✅ PASS — 027_fase5_premium_roles.sql | 2026-04-27 |

---

## Arquivos Criados

- `docs/auditoria/plano_correcao_pos_auditoria_fase5.md` (este arquivo)

## Arquivos Alterados

- `pyproject.toml` — adiciona `asyncio_mode = "auto"`
- `Makefile` — adiciona `PYTEST_BIN` e usa em `test:`

## Arquivos Marcados como Obsoletos

- `docs/sprints/fase5/sprint_28_validacao_receita_serpro_cache.md` — já tinha header OBSOLETO antes da auditoria

---

## Pendências Reais

Nenhuma pendência crítica. Itens de backlog não bloqueantes:

| Pendência | Tipo | Severidade |
|-----------|------|------------|
| `make lint` usa `ruff` do PATH (não do venv) | Cosmético | BAIXA — ruff do sistema pode diferir de versão |
| `make sql-lint` usa sqlfluff via dbt bin (pode falhar sem DB conectado) | Operacional | BAIXA |
| Tag `v3.8.0-gov` ainda não criada | Release | MÉDIA — aguarda autorização do usuário |
| Testes de integração requerem banco de dados ativo | Infraestrutura | BAIXA — por design |

---

## Veredito

| Critério | Status |
|----------|--------|
| Pronto para produção | ⚠️ Não — sem cliente ativo em produção, sem infraestrutura de prod provisionada |
| Pronto para homologação | ✅ Sim — todos os gates passam, código compilado e testado |
| Pronto para demo comercial controlada | ✅ Sim — smoke scripts disponíveis, endpoints premium funcionais |

**Próximo ciclo recomendado:** criar tag `v3.8.0-gov` (Sprint 33 encerrada), iniciar Fase 6 (Sprint 14 do tracking comercial — infraestrutura de produção).

---

## Evidências Pós-Auditoria

| Gate | Resultado | Evidência |
|------|-----------|-----------|
| dbt test | PASS com warning esperado | PASS=383 WARN=1 ERROR=0 TOTAL=384 |
| smoke premium | PASS | `{'status': 'ok', 'endpoints_publicos': 6, 'endpoints_privados': 2}` |
| pytest | PASS | `104 passed in 1.24s` |
| lint/checks | PASS | `All checks passed!` |

> **Nota:** O warning `assert_cnpj_digito_invalido_em_modelos` é **esperado e não bloqueante**. A Sprint 28 definiu dígito verificador inválido como `severity: 'warn'` — registros com CNPJ-DV inválido são quarentenados mas não impedem o build. TOTAL=384 testes, WARN=1 previsto, ERROR=0.

---

## git status final

```
modified: Makefile
modified: pyproject.toml
new file: docs/auditoria/plano_correcao_pos_auditoria_fase5.md
```
