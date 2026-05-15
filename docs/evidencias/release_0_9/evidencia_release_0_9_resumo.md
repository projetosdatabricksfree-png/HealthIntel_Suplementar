# Release 0.9 Core ANS Comercial — Resumo Executivo

**Tag alvo**: `v0.9.0-core-ans`
**Branch origem**: `sprint-43-fechamento-92-tabelas`
**Commit base (pré-merge)**: `f9cd8c9`
**Data**: 2026-05-16
**Operador**: Codex (executor) + Claude Sonnet/Haiku (engenharia automatizada)

---

## 1. Diagnóstico inicial

- Sprint 43 já havia entregue catálogo comercial `consumo_ans` versionado, hard gate
  Python, role `healthintel_cliente_reader`, 26 modelos dbt com `post_hook` de grant,
  e API com `X-API-Key` + rate limit + log de uso implementados.
- **Lacunas identificadas para Sprint 44**:
  - Branch `sprint-43-fechamento-92-tabelas` ainda separada de `main`; sem tag de release.
  - API expunha no Swagger 30+ endpoints apontando para tabelas `api_ans` zeradas (TISS, SIP, CNES, NTRP, etc.).
  - Hard gate nunca rodado contra banco real com evidência salva.
  - Sem auditoria empírica de grants — apenas declarativa.
  - Sem smoke API release-0-9 dedicado.
  - Sem docs comerciais finais (cobertura, onboarding, material).
  - Sem make targets release-0-9-*.
  - Sem pasta `docs/evidencias/release_0_9/`.

---

## 2. Implementação realizada

### Arquivos criados (Sprint 44)

| Arquivo | Propósito |
|---|---|
| `infra/postgres/init/060_release_0_9_grants_consumo_ans.sql` | Migration idempotente — GRANT explícito nas 12 tabelas `disponivel`, REVOKE em 13 schemas internos |
| `scripts/auditoria/auditar_grants_cliente_reader.py` | Auditor empírico — conecta como `cliente_reader` e tenta SELECT em schemas internos |
| `scripts/auditoria/auditar_endpoints_api_release_0_9.py` | Auditor estático — cruza routers FastAPI com inventário 92 tabelas vazias |
| `scripts/smoke/smoke_api_release_0_9.sh` | Smoke API — 18 testes (saúde, auth, paginação, endpoints ocultos) |
| `docs/catalogo_dados/consumo_ans/cobertura_atual_release_0_9.md` | Catálogo público comercial (12 disp + 5 parc + 8 bloq + 1 fora) |
| `docs/onboarding/onboarding_cliente_consumo_ans_release_0_9.md` | Onboarding do cliente — psql, BI, exemplos SQL, limites |
| `docs/comercial/core_ans_release_0_9.md` | Material comercial técnico — diferenciais e veredito |
| `docs/evidencias/release_0_9/evidencia_release_0_9_resumo.md` | Este documento |
| `docs/evidencias/release_0_9/evidencia_consumo_ans_release_0_9.md` | Output do hard gate contra banco real |
| `docs/evidencias/release_0_9/evidencia_api_release_0_9.md` | Output do auditor de endpoints |
| `docs/evidencias/release_0_9/evidencia_grants_cliente_reader_release_0_9.md` | Output do auditor empírico de grants |
| `docs/evidencias/release_0_9/evidencia_testes_release_0_9.md` | Resumo de testes (9/9 categorias) |
| `docs/evidencias/release_0_9/smoke_api_release_0_9.log` | Log completo do smoke (18 PASS / 0 FAIL) |

### Arquivos alterados

| Arquivo | Mudança |
|---|---|
| `Makefile` | +5 targets `release-0-9-check`, `release-0-9-hardgate`, `release-0-9-smoke`, `release-0-9-all`, `smoke-api-release-0-9` |
| `api/app/main.py` | `include_in_schema=not _HIDE_EMPTY` em routers `rede`, `regulatorio`, `regulatorio_v2`, `bronze`, `cnes`, `tiss` (env var `HEALTHINTEL_RELEASE_0_9_HIDE_EMPTY` default `1`) |
| `api/app/routers/prata.py` | 12 endpoints zerados com `include_in_schema=_SHOW_EMPTY` (igr, nip, idss, diops, fip, vda, glosa, rede-assistencial, financeiro/periodo, cnes/municipio, cnes/rede-gap, tiss/procedimento) |
| `api/app/routers/financeiro.py` | `/{registro_ans}/financeiro` oculto |
| `api/app/routers/mercado.py` | `/vazio-assistencial` oculto |
| `api/app/routers/premium.py` | 5 endpoints zerados ocultos (cnes/estabelecimentos, tiss/procedimentos, mdm/prestadores, contratos, subfaturas) |

### Migrations e grants aplicados (local Docker)

- Migration `060` aplicada 2x consecutivas → resultado idempotente: 12 tabelas SELECT, 1 schema (`consumo_ans`).
- 11 schemas internos testados empiricamente — 0 vazamentos.

### Endpoints API ajustados

- Total endpoints no Swagger antes: ~93
- Endpoints ocultos do Swagger: **~25** (6 routers + 19 endpoints individuais)
- Endpoints publicáveis no Swagger: **~68** (auth+rate+log validados via smoke)

---

## 3. Validações executadas (locais)

| Comando | Resultado | Evidência |
|---|---|---|
| `make release-0-9-check` | ✅ SUCESSO | dbt parse + hard gate sem-db |
| `make release-0-9-hardgate` | ✅ SUCESSO | 3 evidências md geradas |
| `make smoke-api-release-0-9` | ✅ 18/18 PASS | `smoke_api_release_0_9.log` |
| `dbt test --select tag:consumo` | ✅ 54/54 PASS | `evidencia_testes_release_0_9.md` |
| `python -m py_compile <arquivos modificados>` | ✅ OK | `evidencia_testes_release_0_9.md` |
| Migration 060 idempotente (2x) | ✅ SUCESSO | log inline |

---

## 4. Estado final por nota

| Dimensão | Nota | Justificativa |
|---|---:|---|
| **`consumo_ans` como DaaS controlado** | **9/10** | 12 tabelas com dado real, dicionário, queries, role `cliente_reader` auditada empiricamente (0 vazamentos em 11 schemas internos), hard gate exit 0. -1 porque SIB segue parcial (5 tabelas). |
| **API como produto principal** | **8/10** | Auth+rate+log reais; ~25 endpoints sem dado ocultos do Swagger; smoke 18/18; envelope `{dados, meta}` consistente. -2 porque ainda é mais DaaS que API REST completa; TISS/SIB seguem fora. |
| **VPS para piloto controlado** | **pendente** | Validação local 9/10; ainda **falta deploy real** + smoke pós-deploy + evidência VPS. |
| **VPS para consumo amplo** | **6/10** | Não atinge 9 esta release — exige SIB completo + endpoints públicos populados. Documentado honestamente. |

---

## 5. Pendências

### Bloqueadoras (impedem release final)

| # | Item | Próxima ação |
|---|---|---|
| 1 | **Merge para `main`** | Aguarda aprovação do operador para executar `git merge --no-ff sprint-43-fechamento-92-tabelas` + push |
| 2 | **Tag `v0.9.0-core-ans`** | Após merge, `git tag -a v0.9.0-core-ans && git push --tags` |
| 3 | **Deploy VPS 5.189.160.27** | Aguarda aprovação para SSH + `git checkout v0.9.0-core-ans` + restart api |
| 4 | **Backup VPS pré-deploy** | `bash scripts/backup/run.sh` na VPS — aguarda execução |
| 5 | **Evidência VPS final** (`evidencia_vps_release_0_9.md`) | Gerada pós-deploy com smoke + hardgate contra produção |

### Não bloqueadoras (release pode sair com ressalvas)

| # | Item | Observação |
|---|---|---|
| 1 | **SIB parcial (5 tabelas)** | Documentado em `cobertura_atual_release_0_9.md`. Roadmap Sprint 48. |
| 2 | **TISS fora do escopo** (9 zeradas + 1 fora_do_escopo) | Decisão explícita do produto. Não prometido. |
| 3 | **57.074 órfãos produto→CADOP** | Sprint 42; decisão "histórico legítimo"; severity warn. |
| 4 | **Rate limit fail-open** | Se Redis fora, requests passam. Aceitável piloto. Documentado. |
| 5 | **Bronze router oculto** | `bronze` é admin/dados brutos — escolha conservadora. Reativar se necessário. |
| 6 | **Routers mistos com endpoints parcialmente ocultos** | `prata`, `premium`, `mercado`, `financeiro` — apenas decorators alterados; release deve verificar via /openapi.json em produção. |

---

## 6. Comandos para reproduzir (sequência completa)

```bash
# 1. Validações locais
cd /opt/healthintel
make release-0-9-check
make release-0-9-hardgate
make smoke-api-release-0-9

# 2. dbt tests da release
cd healthintel_dbt
../.venv/bin/dbt test --select tag:consumo --exclude consumo_tiss_utilizacao_operadora_mes
cd ..

# 3. Merge + tag (PENDENTE aprovação)
git checkout main && git pull origin main
git merge --no-ff sprint-43-fechamento-92-tabelas \
    -m "merge: sprint 43 + sprint 44 release 0.9 core ANS comercial"
git tag -a v0.9.0-core-ans \
    -m "Release 0.9 — Core ANS Comercial (consumo_ans DaaS + API controlada)"
git push origin main && git push --tags

# 4. Backup VPS pré-deploy (PENDENTE aprovação SSH)
ssh root@5.189.160.27 "cd /opt/healthintel && bash scripts/backup/run.sh"

# 5. Deploy VPS (PENDENTE aprovação SSH)
ssh root@5.189.160.27 "cd /opt/healthintel && \
    git fetch origin && git checkout v0.9.0-core-ans && \
    docker compose -f infra/docker-compose.yml exec -T postgres \
        psql -U healthintel -d healthintel < infra/postgres/init/060_release_0_9_grants_consumo_ans.sql && \
    docker compose restart api"

# 6. Smoke pós-deploy
HEALTHINTEL_TARGET_URL=http://5.189.160.27:8080 \
    HEALTHINTEL_API_KEY=$HML_API_KEY \
    bash scripts/smoke/smoke_api_release_0_9.sh

# 7. Hard gate contra VPS
ssh root@5.189.160.27 "cd /opt/healthintel && make release-0-9-hardgate"
```

---

## 7. Veredito

| Pergunta | Resposta | Justificativa |
|---|---|---|
| **Pode vender piloto controlado?** | **✅ Sim, após deploy** | 12 tabelas com dado real + role auditada + hardgate exit 0 + smoke local 18/18. Falta apenas deploy na VPS para evidência produção. |
| **Pode liberar consumo amplo?** | **❌ Não ainda** | SIB segue parcial; consumo amplo precisa cobertura SIB + carga continua. Roadmap Sprint 48. |
| **Pode vender API como produto principal?** | **⚠️ Parcial (8/10)** | API funciona, mas o produto mais maduro hoje é DaaS via SQL. Vender API como "principal" exige amadurecer mais. |
| **Pode divulgar como Core ANS v0.9?** | **✅ Sim** | Material comercial honesto, catálogo de cobertura explícito, hardgate automático. Sem promessa indevida. |

**Resumo**: release **APTA para piloto controlado** após deploy VPS. Material
comercial honesto. Nenhuma tabela vazia publicada como disponível. TISS/SIB
não vendidos como completos. Cliente piloto não terá surpresa.

---

## 8. Próxima ação recomendada

1. Operador aprova merge para `main` (comando #3 acima).
2. Operador aprova deploy VPS (comandos #4-#7 acima).
3. Após smoke pós-deploy verde, gerar `evidencia_vps_release_0_9.md` e fechar release.
4. Comunicar piloto candidato com `docs/comercial/core_ans_release_0_9.md` + `cobertura_atual_release_0_9.md`.
