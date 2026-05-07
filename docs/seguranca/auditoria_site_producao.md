# Auditoria de Segurança — Site e API em Produção

**Data:** 2026-05-07
**Executor:** Auditoria interna HealthIntel
**Escopo:** Frontend portal + API FastAPI + Nginx

---

## Achados e Correções Aplicadas

### C1 — `verificar_plano` permissiva com `endpoint_permitido` vazio
| Campo | Valor |
|-------|-------|
| **Severidade** | CRÍTICO |
| **Arquivo** | `api/app/dependencia.py:175` |
| **Achado** | `if not endpoints_permitidos: return` — qualquer chave sem endpoints autorizados acessava tudo |
| **Correção** | Retorno substituído por `HTTPException 403 PLANO_SEM_ENDPOINTS`; admin (`is_admin=True`) continua passando |
| **Teste criado** | `api/tests/unit/test_security_hardening.py::test_verificar_plano_vazio_levanta_403` |
| **Evidência** | `pytest api/tests/unit/test_security_hardening.py -v` |

### C2 — Swagger/OpenAPI públicos em produção
| Campo | Valor |
|-------|-------|
| **Severidade** | CRÍTICO |
| **Arquivo** | `api/app/main.py:65` |
| **Achado** | `/docs`, `/redoc`, `/openapi.json` habilitados sem proteção |
| **Correção** | `docs_url=None`, `redoc_url=None`, `openapi_url=None` quando `api_env == "production"` |
| **2ª camada** | Nginx bloqueia essas rotas com `return 404` (`infra/nginx/nginx.conf`) |
| **Teste criado** | `test_security_hardening.py::test_docs_bloqueados_em_producao` |

### C3 — `/saude` expõe hostnames de infraestrutura
| Campo | Valor |
|-------|-------|
| **Severidade** | CRÍTICO |
| **Arquivo** | `api/app/main.py:103-114` |
| **Achado** | Resposta incluía `postgres_host`, `redis_host`, `mongo_host` sem autenticação |
| **Correção** | `/saude` retorna apenas `{"status": "ok"}` |
| **Teste criado** | `test_security_hardening.py::test_saude_nao_expoe_infra`, `test_saude_nao_expoe_versao_ambiente` |

### C4 — `/prontidao` público sem proteção
| Campo | Valor |
|-------|-------|
| **Severidade** | CRÍTICO |
| **Arquivo** | `api/app/main.py:117-121` |
| **Achado** | Endpoint com detalhes de dependências acessível por qualquer cliente |
| **Correção** | Requer header `X-Internal-Token` com valor de `API_INTERNAL_TOKEN`; Nginx bloqueia por IP externo |
| **Teste criado** | `test_security_hardening.py::test_prontidao_sem_token_retorna_401`, `test_prontidao_token_invalido_retorna_401`, `test_hardening.py::test_prontidao_sem_token_deve_retornar_401` |

### C5 — Rotas `/admin/*` sem RBAC real
| Campo | Valor |
|-------|-------|
| **Severidade** | CRÍTICO |
| **Arquivos** | `api/app/routers/admin_billing.py`, `api/app/routers/admin_layout.py` |
| **Achado** | Qualquer chave de cliente comercial com acesso a `/admin/*` na lista de endpoints podia usar rotas admin |
| **Correção** | Substituído `verificar_plano` por `verificar_admin` nos dois routers; `is_admin=True` somente para `plano_nome == "admin_interno"` |
| **Teste criado** | `test_security_hardening.py::test_verificar_admin_sem_flag_levanta_403`, `test_admin_billing_rejeita_chave_comum` |

### A1 — `/prata` sem `verificar_plano`
| Campo | Valor |
|-------|-------|
| **Severidade** | ALTO |
| **Arquivo** | `api/app/routers/prata.py` |
| **Achado** | Router prata só aplicava `verificar_camada`, não `verificar_plano` |
| **Correção** | Adicionado `Depends(verificar_plano)` ao `APIRouter` |
| **Teste criado** | `test_security_hardening.py::test_verificar_plano_rota_nao_autorizada_levanta_403` |

### A2 — Startup não bloqueava secrets default em produção
| Campo | Valor |
|-------|-------|
| **Severidade** | ALTO |
| **Arquivo** | `api/app/core/config.py` |
| **Achado** | `validar_configuracao()` verificava só 2 secrets e apenas em não-local (não em production explícito) |
| **Correção** | Em `api_env == "production"`, valida 5 secrets; lança `RuntimeError` bloqueando o servidor |
| **Secrets validados** | `API_JWT_ADMIN_SECRET`, `LAYOUT_SERVICE_TOKEN`, `POSTGRES_PASSWORD`, `MONGO_INITDB_ROOT_PASSWORD`, `API_INTERNAL_TOKEN` |
| **Teste criado** | `test_security_hardening.py::test_validar_configuracao_bloqueia_startup_em_producao_com_secrets_default` |

### A3 — Nginx sem HSTS e sem bloqueio de docs
| Campo | Valor |
|-------|-------|
| **Severidade** | ALTO |
| **Arquivo** | `infra/nginx/nginx.conf` |
| **Achado** | Header HSTS ausente; `/docs`, `/redoc`, `/openapi.json` não bloqueados no proxy |
| **Correção** | Adicionados `Strict-Transport-Security`, bloqueio de docs e restrição IP para `/prontidao` |

### A4 — CORS sem warning em não-local
| Campo | Valor |
|-------|-------|
| **Severidade** | ALTO |
| **Arquivo** | `api/app/core/config.py` |
| **Achado** | Nenhum aviso se CORS incluía localhost em ambiente HML/staging |
| **Correção** | Warning de log quando origins com `localhost`/`127.0.0.1` detectadas fora de `local/dev/test/ci` |

### M1-M2 — SEO ausente
| Campo | Valor |
|-------|-------|
| **Severidade** | MODERADO |
| **Arquivos** | `frontend/.../public/robots.txt`, `public/sitemap.xml`, `index.html` |
| **Correção** | Criados `robots.txt` e `sitemap.xml`; adicionadas meta OG e Twitter Cards ao `index.html` |

### M3 — CTAs de plano com nome completo no query param
| Campo | Valor |
|-------|-------|
| **Severidade** | MODERADO |
| **Arquivos** | `src/data/plans.ts`, `src/components/PlanCard.tsx`, `src/pages/public/ContactPage.tsx` |
| **Achado** | `?plano=Piloto Assistido` em vez de `?plano=piloto` |
| **Correção** | Adicionado campo `slug` ao tipo `ApiPlan`; CTAs usam `plan.slug`; formulário mapeado para slugs |

### M4 — Ausência de testes Playwright
| Campo | Valor |
|-------|-------|
| **Severidade** | MODERADO |
| **Correção** | 5 suítes criadas: links_e_botoes, planos_ctas, menu_mobile, formulario_contato, ausencia_links_quebrados |

---

## Comandos de Verificação

```bash
# Testes de segurança da API
make api-security-tests

# Testes de segurança específicos (novos)
make security-audit-local

# Smoke completo
make smoke

# Frontend E2E (requer servidor dev rodando)
make frontend-e2e

# CI local completo
make ci-local

# Verificação manual
curl http://localhost:8080/saude
# → {"status":"ok"}

curl http://localhost:8080/prontidao
# → 401

curl http://localhost:8080/docs
# → 404 (em produção)

curl http://localhost:8080/admin/billing/resumo?referencia=2026-05 \
  -H "X-API-Key: hi_local_dev_2026_api_key"
# → 403 ACESSO_RESTRITO_ADMIN
```

---

## Critérios de Aceite — Status

| Critério | Status |
|----------|--------|
| Nenhum endpoint público expõe hostnames internos ou stack trace | ✅ |
| Nenhuma rota `/admin/*` aceita chave de cliente comum | ✅ |
| Nenhuma rota `/prata` ignora plano contratado | ✅ |
| API não sobe em produção com secrets default | ✅ |
| Docs Swagger não ficam públicos em produção | ✅ |
| Todos os botões do portal têm destino correto | ✅ |
| robots.txt e sitemap.xml acessíveis | ✅ |
| OpenGraph presente no index.html | ✅ |
| Testes de segurança criados e passando | ✅ |
| Testes Playwright criados | ✅ |
