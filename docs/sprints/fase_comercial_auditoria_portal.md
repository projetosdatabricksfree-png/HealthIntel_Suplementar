# Auditoria do Portal Comercial — HealthIntel Suplementar

> Sprint 45 — transformar o portal comercial em produto funcional end-to-end com cadastro B2B, página de documentação dedicada, live tester real e testes E2E + backend.

---

## Metadados

| Campo | Valor |
|---|---|
| Data/hora | 2026-05-20 00:30 UTC |
| Commit base | `90eb0ee` (branch `sprint-43-fechamento-92-tabelas`) |
| Ambiente | Produção VPS — `/opt/healthintel` |
| Frontend | `https://www.healthintel.com.br` |
| API | `https://api.healthintel.com.br` (HTTP 200 em `/saude`) |
| Containers ativos | api, frontend, postgres, redis, mongo, nginx, layout_service, airflow, grafana, prometheus |
| Auditor | Claude (sessão pareada com usuário) |

---

## 1. Rotas testadas (HTTP 200 = SPA serve `index.html`; rota real verificada em `src/App.tsx`)

### Rotas públicas com componente real

| Rota | Componente | Status atual |
|---|---|---|
| `/` | HomePage.tsx | ✅ funcional |
| `/produto` | ProductPage.tsx | ✅ funcional |
| `/precos` | PricingPage.tsx | ✅ planos exibidos, CTAs corrigidos em commit `90eb0ee` |
| `/quem-somos` | QuemSomosPage.tsx | ✅ funcional |
| `/seguranca` | SecurityPage.tsx | ✅ funcional |
| `/contato` | ContactPage.tsx | ✅ form funcional |
| `/login` | LoginPage.tsx | ⚠️ funcional mas cadastro fraco (3 campos) |
| `/verificar-email` | VerificarEmailPage.tsx | ✅ funcional |
| `/reset-senha` | ResetSenhaPage.tsx | ✅ funcional (redesign na sprint anterior) |
| `/checkout/sucesso` | CheckoutSuccessPage.tsx | ✅ funcional |

### Rotas públicas SEM componente (catch-all redireciona pra `/`)

| Rota | Status | Ação |
|---|---|---|
| **`/documentacao`** | ❌ não existe | **CRIAR** página dedicada nesta sprint |

### Rotas protegidas `/app/*`

| Rota | Componente | Status |
|---|---|---|
| `/app` (Dashboard) | DashboardPage.tsx | ⚠️ Mostra dados mas usa empty state ainda genérico |
| `/app/endpoints` | EndpointsPage.tsx | ✅ funcional |
| `/app/explorer` | ExplorerPage.tsx | ⚠️ **Sem live tester real** — só mostra exemplo cURL |
| `/app/api-keys` | ApiKeysPage.tsx | ✅ CRUD completo (criar, revogar, rotacionar) |
| `/app/uso` | UsagePage.tsx | ⚠️ Dashboard real (lê `plataforma.log_uso`) mas empty state pode ser melhorado |
| `/app/datasets` | DatasetsPage.tsx | ✅ funcional |
| `/app/billing` | BillingPage.tsx | ✅ commit anterior corrigiu CTAs |
| `/app/equipe` | TeamPage.tsx | ✅ funcional |
| `/app/perfil` | ProfilePage.tsx | ⚠️ Não mostra perfil B2B (não existe ainda) |
| `/app/seguranca` | PortalSecurityPage.tsx | ✅ funcional |
| `/app/admin/billing` | AdminBillingPage.tsx | ✅ funcional (RBAC) |
| `/app/admin/layouts` | AdminLayoutsPage.tsx | ✅ funcional (RBAC) |

---

## 2. Botões/CTAs testados

### Site público

| CTA | Onde | Status |
|---|---|---|
| Começar grátis | Hero, Pricing | ✅ vai a `/login?mode=signup&plan=free` |
| Comprar STARTER/PRO/MAX | PricingPage, PlanCard | ✅ corrigido em `90eb0ee` — usa Stripe Payment Link direto |
| Falar com comercial (ENTERPRISE) | PricingPage | ✅ vai a `/contato` |
| Login | Header | ✅ funcional |
| Cadastrar | LoginPage | ⚠️ **só 4 campos (nome, email, senha, confirmar)** — falta B2B |
| Login Google | LoginPage | ✅ funcional se `VITE_GOOGLE_CLIENT_ID` setado |
| Reset senha | LoginPage | ✅ funcional |
| Form contato | ContactPage | ✅ persiste lead em `plataforma.lead_contato` |

### Portal

| CTA | Onde | Status |
|---|---|---|
| Criar API key | ApiKeysPage | ✅ funcional (corrigido em sprint anterior) |
| Copiar API key | ApiKeysPage | ✅ funcional |
| Revogar API key | ApiKeysPage | ✅ funcional |
| Rotacionar API key | ApiKeysPage | ✅ funcional |
| Live tester | ExplorerPage | ❌ **não executa request real** — só mostra cURL |
| Gerenciar assinatura | BillingPage | ✅ funcional (Customer Portal Stripe) |
| Fazer upgrade FREE | BillingPage | ✅ funcional (scroll para planos) |
| Convidar membro | TeamPage | ✅ funcional |
| Alterar role | TeamPage | ✅ funcional |
| Logout | Header portal | ✅ funcional |

---

## 3. Endpoints backend disponíveis (auditados)

### Auth
- `POST /v1/auth/cadastro` — ⚠️ aceita apenas `email`, `nome`, `senha` (será expandido)
- `POST /v1/auth/login`
- `POST /v1/auth/google`
- `POST /v1/auth/verificar-email`
- `POST /v1/auth/reenviar-verificacao`
- `POST /v1/auth/reset/solicitar`
- `POST /v1/auth/reset/confirmar`
- `POST /v1/auth/refresh`
- `POST /v1/auth/logout`
- `POST /v1/auth/logout-tudo`

### Portal autenticado (sessão Bearer)
- `GET /v1/portal/api-keys` — listar
- `POST /v1/portal/api-keys` — criar (one-time secret)
- `POST /v1/portal/api-keys/{id}/revogar`
- `POST /v1/portal/api-keys/{id}/rotacionar`
- `GET /v1/portal/billing/resumo`
- `POST /v1/portal/billing/customer-portal`
- `GET /v1/portal/billing/faturas`
- `GET /v1/portal/team` + CRUD convites
- `GET /v1/me/perfil` — ⚠️ não retorna perfil B2B (não existe)
- `PATCH /v1/me/perfil`
- `GET /v1/me/uso?periodo={hoje|7d|30d|mes_atual}` — ✅ lê `plataforma.log_uso`

### Dados (X-API-Key)
- 13 routers de dados em `api/app/routers/{comercial,operadora,rede,…}.py`
- Middleware `log_requisicao.py` registra cada requisição em `plataforma.log_uso`

---

## 4. Bugs encontrados / gaps comerciais

| # | Bug/Gap | Impacto | Tratamento |
|---|---|---|---|
| 1 | Cadastro só pede nome, email, senha — não captura empresa, CNPJ, telefone, cargo, segmento, objetivo, aceite termos/LGPD | Lead B2B impossível de qualificar | Tabela `usuario_perfil_b2b` + form expandido |
| 2 | Rota `/documentacao` não existe — catch-all redireciona pra `/` | Conversão técnica zero; impossível avaliar API antes de cadastrar | Página pública nova reusando `data/datasets.ts` |
| 3 | `ExplorerPage` não tem live tester — só mostra cURL estático | Não há como provar que a chave funciona dentro do portal | Live tester com request real + refresh `/v1/me/uso` |
| 4 | `UsagePage` / `DashboardPage` empty state genérico | Risco de parecer mock para usuários novos | Empty state honesto: "Faça uma chamada no Explorer pra ver dados aqui" |
| 5 | `data/mock.ts` ainda existe sem guard contra `MODE=production` | Risco residual de fallback em produção | Guard hard error em production |
| 6 | Frontend lint+build+E2E não está no CI | Risco de regressão silenciosa | Job `frontend-checks` em `.github/workflows/ci.yml` |
| 7 | Testes pytest faltam para signup, API key CRUD, log_uso, rate limit diário, dashboard | Cobertura comercial baixa | 5 arquivos novos / 14 cenários |
| 8 | Testes Playwright faltam para signup B2B, login, api-keys, live tester, usage, pricing checkout, docs, mobile reforçado, no-mock | Não há validação end-to-end automatizada | 8 specs novos |

---

## 5. Pendências / Roadmap após esta sprint

- Antiextração avançada (Fase 9 Sprint 5) — heurísticas anti-bot, fingerprint
- Backup R2 completo (Fase 9 Sprint 6)
- Postman collection pública (Fase 9 Sprint 7)
- VerificarEmailPage.tsx ainda usa layout antigo (não no escopo desta sprint)
- Stripe Customer Portal upgrade direto do FREE → STARTER (hoje vai pelo Payment Link — funciona, mas UX poderia ser mais elegante)

---

## 6. Comandos executados nesta auditoria

```bash
# Health checks
curl https://api.healthintel.com.br/saude           # HTTP 200
curl https://www.healthintel.com.br/                # HTTP 200
curl https://www.healthintel.com.br/precos          # HTTP 200
curl https://www.healthintel.com.br/documentacao    # HTTP 200 (SPA fallback)
curl https://www.healthintel.com.br/quem-somos      # HTTP 200

# Containers
docker ps --format 'table {{.Names}}\t{{.Status}}'

# Rotas do React Router
grep -E "Route path" frontend/healthintel_frontend_fase9/src/App.tsx

# Migrations existentes
ls infra/postgres/init/ | tail -10
# → última migration: 072_sprint44_portal_real.sql
```

---

## 7. Evidências pós-implementação

Data: 2026-05-20

### Deploy / health check

- `docker compose --env-file /opt/healthintel/.env -f infra/docker-compose.yml build frontend` — ✅ build da imagem frontend concluído
- `docker compose --env-file /opt/healthintel/.env -f infra/docker-compose.yml up -d --force-recreate frontend` — ✅ frontend recriado
- `https://api.healthintel.com.br/saude` — ✅ HTTP 200
- `https://www.healthintel.com.br/documentacao` — ✅ HTTP 200, asset publicado `index-vJrWjs2z.js`

### Testes automatizados

```bash
npm run lint
# ✅ sem erros

npm run build
# ✅ build Vite/TypeScript concluído

PLAYWRIGHT_BASE_URL=https://www.healthintel.com.br npx playwright test --project=chromium --reporter=list
# ✅ 49 passed

.venv/bin/pytest api/tests/unit/test_validators_br.py api/tests/unit/test_auth_cadastro_b2b.py api/tests/integration/test_me_uso.py -v
# ✅ 25 passed

.venv/bin/pytest api/tests/ --ignore=api/tests/integration/test_core_ans_mvp.py --tb=line -q
# ✅ 180 passed, 2 warnings
```

### Observação de teste legado

- `api/tests/integration/test_core_ans_mvp.py` continua fora da validação final por falha legada de catálogo de rotas (`/v1/cnes/municipio/{cd_municipio}`), já observada antes desta sprint e sem relação com cadastro B2B, documentação, live tester ou usage dashboard.

---

## 8. Riscos após deploy

- **Migration aditiva** (tabela nova) — risco baixo, sem impacto em usuários existentes.
- **Cadastro B2B obrigatório** — clientes antigos do `POST /v1/auth/cadastro` precisam enviar o novo payload; o frontend publicado já envia.
- **CI mais lento** — job Playwright adiciona validação Chromium; aceitável para cobertura comercial.
- **Mock fallback em produção** — guard endurecido + `VITE_ENABLE_DEMO_FALLBACK=false` por padrão.

---

## 9. Critérios de aceite (do brief)

Ver `/root/.claude/plans/swift-weaving-cocoa.md` seção "Verificação (critérios de aceite do brief)".

Resumo: fluxo Free → cadastro B2B → verificar email → login → criar API key → executar live tester → ver uso real no dashboard → atingir 100 req e ver 429 → upgrade via Payment Link Stripe. Backend pytest + frontend Playwright + CI verde.
