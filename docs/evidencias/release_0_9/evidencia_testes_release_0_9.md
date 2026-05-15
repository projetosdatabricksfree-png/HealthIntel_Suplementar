# Evidência — Testes Release 0.9 Core ANS Comercial

**Data**: 2026-05-16
**Branch**: `sprint-43-fechamento-92-tabelas` (pré-merge para main)
**Commit**: `f9cd8c9`

---

## 1. Hard gate `consumo_ans` (sem-db + com-db)

```
$ .venv/bin/python scripts/auditoria/validar_consumo_ans_comercial.py --sem-db
SUCESSO hard gate consumo_ans comercial

$ .venv/bin/python scripts/auditoria/validar_consumo_ans_comercial.py \
    --evidencia docs/evidencias/release_0_9/evidencia_consumo_ans_release_0_9.md
SUCESSO hard gate consumo_ans comercial
```

- 26 tabelas no catálogo (12 disponivel + 5 parcial + 8 vazia_bloqueada + 1 fora_do_escopo).
- 12 tabelas disponíveis com `count(*) > 0` reais.
- Detalhe: [`evidencia_consumo_ans_release_0_9.md`](evidencia_consumo_ans_release_0_9.md).

## 2. Auditoria empírica de grants `healthintel_cliente_reader`

```
$ .venv/bin/python scripts/auditoria/auditar_grants_cliente_reader.py
Modo: set role healthintel_cliente_reader via admin DSN
Tabelas acessíveis: 12
Schemas internos testados: 11 (vazamentos: 0)
Tabelas disponíveis testadas: 12 (faltando: 0)
SUCESSO auditoria empirica grants cliente_reader
```

- Cliente reader bloqueia 100% dos 11 schemas internos testados.
- Cliente reader libera 100% das 12 tabelas `disponivel`.
- Detalhe: [`evidencia_grants_cliente_reader_release_0_9.md`](evidencia_grants_cliente_reader_release_0_9.md).

## 3. Auditoria endpoints API

```
$ .venv/bin/python scripts/auditoria/auditar_endpoints_api_release_0_9.py
Evidencia gerada: docs/evidencias/release_0_9/evidencia_api_release_0_9.md
SUCESSO auditoria API release 0.9
```

- 19 routers analisados, 93 endpoints totais.
- 42 endpoints publicar, 44 publicar_parcial, 7 ocultar.
- Routers totalmente ocultos via `include_in_schema=False`: `cnes`, `rede`, `regulatorio`, `regulatorio_v2`, `bronze`, `tiss`.
- Endpoints individuais ocultos (em routers mistos): 12 em `prata`, 1 em `financeiro`, 1 em `mercado`, 5 em `premium`.
- Detalhe: [`evidencia_api_release_0_9.md`](evidencia_api_release_0_9.md).

## 4. Smoke API

```
$ HEALTHINTEL_API_KEY=hi_local_dev_2026_api_key make smoke-api-release-0-9
[1] Endpoints públicos / internos:    /saude=200, /prontidao sem token=401
[2] Autenticação:                     sem chave=401, chave inválida=401
[3] Endpoints publicáveis (7):        todos retornam 200|403 (depende do plano)
[4] Paginação:                        page+per_page funcionais, per_page=99999 limitado
[5] Endpoints ocultos do Swagger:     ainda respondem com 200|403|404 (não-quebra)
[6] Endpoint inexistente:             404
[7] OpenAPI:                          docs desabilitado em produção (esperado)

===== Resumo =====
PASS: 18
FAIL: 0
```

- Detalhe: [`smoke_api_release_0_9.log`](smoke_api_release_0_9.log).

## 5. dbt tests `tag:consumo`

```
$ cd healthintel_dbt && ../.venv/bin/dbt test \
    --select tag:consumo --exclude consumo_tiss_utilizacao_operadora_mes

Finished running 54 data tests in 0:00:09.54
Done. PASS=54 WARN=0 ERROR=0 SKIP=0 NO-OP=0 TOTAL=54
```

- 54 testes dbt no domínio `consumo` (excluindo TISS fora do escopo).
- 100% pass.

## 6. dbt parse + compile

```
$ make release-0-9-check
[release-0-9-check] dbt parse...
Performance info: /tmp/healthintel_dbt_target/perf_info.json
[release-0-9-check] hard gate --sem-db...
SUCESSO hard gate consumo_ans comercial
[release-0-9-check] OK
```

- 279 modelos, 1 snapshot, 507 data tests, 11 seeds, 60 sources, 14 exposures, 871 macros.

## 7. Migration 060 (idempotência)

```
$ docker compose exec -T postgres psql < infra/postgres/init/060_release_0_9_grants_consumo_ans.sql
NOTICE: [release 0.9] healthintel_cliente_reader: 12 tabelas SELECT em 1 schema(s).
DO

$ docker compose exec -T postgres psql < infra/postgres/init/060_release_0_9_grants_consumo_ans.sql
NOTICE: [release 0.9] healthintel_cliente_reader: 12 tabelas SELECT em 1 schema(s).
DO
```

- 2 execuções consecutivas → resultado idêntico.

## 8. Sintaxe Python (py_compile)

```
$ .venv/bin/python -m py_compile \
    api/app/main.py api/app/routers/prata.py api/app/routers/financeiro.py \
    api/app/routers/mercado.py api/app/routers/premium.py \
    scripts/auditoria/auditar_endpoints_api_release_0_9.py \
    scripts/auditoria/auditar_grants_cliente_reader.py
✅ Sintaxe OK
```

## 9. Resumo agregado

| Suite | Resultado |
|---|---|
| Hard gate consumo_ans (sem-db) | ✅ SUCESSO |
| Hard gate consumo_ans (banco real) | ✅ SUCESSO |
| Auditor grants empírico | ✅ SUCESSO (0 vazamentos) |
| Auditor endpoints API | ✅ SUCESSO |
| Smoke API (18 testes) | ✅ 18 PASS / 0 FAIL |
| dbt test tag:consumo | ✅ 54 PASS |
| dbt parse | ✅ 279 modelos OK |
| Migration 060 idempotente | ✅ 2x execução = mesmo resultado |
| Sintaxe Python (py_compile) | ✅ OK |

**Total**: 9/9 categorias de teste passando. Release 0.9 está validada localmente. Falta apenas evidência VPS de produção (bloco 5).
