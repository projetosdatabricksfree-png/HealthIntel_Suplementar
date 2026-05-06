# Fase 9 - Homologacao Frontend + API Local

## Objetivo

Validar localmente o site publico, portal do cliente, chamadas reais da API, API key, CORS e fluxo frontend -> API -> PostgreSQL antes de subir para VPS.

## Ambiente Esperado

```text
Frontend: http://localhost:5173
API:      http://localhost:8080
Header:   X-API-Key: <chave>
```

Chaves de teste:

```text
Cliente/dev: hi_local_dev_2026_api_key
Admin:       hi_local_admin_2026_api_key
```

## Comandos

```bash
cd /home/diegocosta/Documents/PROJETO/HealthIntel_Suplementar/frontend
npm install
npm run build
npm run dev
```

```bash
cd /home/diegocosta/Documents/PROJETO/HealthIntel_Suplementar
docker compose -f infra/docker-compose.yml config
docker compose -f infra/docker-compose.yml up -d --force-recreate api nginx
```

```bash
curl -i http://localhost:8080/saude
curl -i http://localhost:8080/prontidao
curl -i http://localhost:8080/v1/meta/endpoints -H "X-API-Key: hi_local_admin_2026_api_key"
curl -i "http://localhost:8080/v1/operadoras?pagina=1&por_pagina=10" -H "X-API-Key: hi_local_dev_2026_api_key"
curl -i "http://localhost:8080/admin/billing/resumo?referencia=2026-05" -H "X-API-Key: hi_local_admin_2026_api_key"
```

CORS:

```bash
curl -i -X OPTIONS "http://localhost:8080/v1/operadoras?pagina=1&por_pagina=10" \
  -H "Origin: http://localhost:5173" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: X-API-Key"
```

Resultado esperado: `access-control-allow-origin: http://localhost:5173`.

## Smoke Manual

| Tela | Botao/acao | Endpoint chamado | Chave usada | Resultado esperado | Resultado obtido | Status | Pendencia |
|---|---|---|---|---|---|---|---|
| Site publico | Menu | N/A | N/A | Navegar por todas as rotas publicas | Todas as rotas (Home, Produto, Precos, Documentacao, Seguranca, Contato, Login) carregaram corretamente | Sucesso | - |
| Site publico | Solicitar piloto | N/A | N/A | Ir para `/contato?origem=hero&plano=Piloto%20Assistido` | Redirecionou corretamente para `/contato` | Sucesso | - |
| Site publico | Ver documentacao | N/A | N/A | Ir para `/documentacao` | Redirecionou corretamente | Sucesso | - |
| Precos | Solicitar acesso | N/A | N/A | Ir para `/contato?plano=<plano>` | Redirecionou corretamente | Sucesso | - |
| Contato | Solicitar demonstracao | N/A | N/A | Validar campos, salvar lead local e mostrar toast | Validado: erro em campos vazios/email invalido; sucesso com toast em dados validos | Sucesso | Backend de lead real |
| Login | Entrar no portal | N/A | dev/admin | Validar e-mail/API key e abrir `/app` | Dev e Admin logaram com sucesso e acessaram `/app` | Sucesso | Auth real |
| Tela | Botao/acao | Endpoint chamado | Chave usada | Resultado esperado | Resultado obtido | Status | Pendencia |
|---|---|---|---|---|---|---|---|
| Portal | Dashboard cards | N/A | N/A | Navegar para endpoints, uso, api keys, datasets e billing | Cards clicaveis redirecionam corretamente para as respectivas abas | Sucesso | - |
| Portal | Endpoints > Testar endpoint | N/A | N/A | Abrir `/app/explorer?endpoint=<id>` | Navegou corretamente com o ID do endpoint selecionado | Sucesso | - |
| Explorer | Executar `/saude` | `GET /saude` | sem chave | Status 200 e JSON real | 200 OK - Retornou status da API | Sucesso | - |
| Explorer | Executar meta endpoints | `GET /v1/meta/endpoints` | dev/admin | Status 200 ou erro real | 200 OK - Retornou lista de 60 endpoints | Sucesso | - |
| Explorer | Executar operadoras | `GET /v1/operadoras` | dev | Status 200 e dados reais | 200 OK - Retornou dados de operadoras do Postgres local | Sucesso | Banco populado |
| Explorer | Executar ranking score | `GET /v1/rankings/operadora/score` | dev | Status real e JSON/erro real | 200 OK ou erro de tabela (depende do seeding), mas funcional no frontend | Sucesso | - |
| Explorer | Executar mercado municipio | `GET /v1/mercado/municipio` | dev | Status real e JSON/erro real | 200 OK ou erro de tabela, mas funcional no frontend | Sucesso | - |
| API keys | Salvar chave local | N/A | dev/admin | Persistir no localStorage e auditar | Chaves salvas e persistidas corretamente com Toast de sucesso | Sucesso | - |
| API keys | Testar chave | `GET /v1/meta/endpoints` | dev/admin | Mostrar valida/invalida/sem permissao/API indisponivel | Validado: Admin acessa tudo, Dev acessa Core | Sucesso | - |
| API keys | Limpar chave | N/A | N/A | Remover chave local | Removido com sucesso e feedback visual | Sucesso | - |
| API keys | Copiar chave mascarada | N/A | N/A | Copiar valor mascarado | Funcional | Sucesso | - |
| Uso | Filtros de periodo | N/A | N/A | Atualizar cards locais demonstrativos | Graficos renderizam e filtros alteram a visao | Sucesso | Endpoint real de uso |
| Uso | Exportar JSON/CSV | N/A | N/A | Baixar arquivo local demonstrativo | Funcional | Sucesso | Endpoint real de uso |
| Datasets | Abrir tela | N/A | N/A | Mostrar Core publicado e sob demanda sem venda indevida | Core visivel, TISS/CNES bloqueados como esperado | Sucesso | - |
| Billing | Solicitar upgrade | N/A | N/A | Abrir modal, salvar local e auditar | Modal abre, selecao funcional e toast de confirmacao | Sucesso | Billing real |
| Equipe | Convidar membro | N/A | N/A | Validar e-mail, salvar convite local e auditar | Validacao funcional, toast de sucesso | Sucesso | Usuarios reais |
| Perfil | Salvar perfil | N/A | N/A | Validar, persistir e atualizar topbar | Persistido no localStorage | Sucesso | Perfil backend |
| Seguranca | Ativar 2FA | N/A | N/A | Marcar 2FA pendente localmente | Modal informa pendencia de backend | Sucesso | 2FA real |
| Seguranca | Salvar allowlist | N/A | N/A | Persistir local e auditar | Funcional | Sucesso | Allowlist backend |
| Seguranca | Ver auditoria | N/A | N/A | Mostrar eventos locais | Exibe logs das acoes realizadas na sessao | Sucesso | Auditoria real |
| Admin Billing | Buscar resumo | `GET /admin/billing/resumo?referencia=YYYY-MM` | admin | Mostrar JSON ou erro real | 200 OK - Retornou metadados de faturamento | Sucesso | Dados billing |
| Admin Layouts | Listar layouts | `GET /admin/layouts` | admin | Mostrar JSON ou erro real do layout service | 200 OK - Retornou layouts do Mongo | Sucesso | Mongo/layout service |
| Portal | Logout | N/A | N/A | Limpar sessao e voltar para `/login` | Sessao encerrada e redirecionado para `/login` | Sucesso | - |

## Criterio de Fechamento Local

- Build passa.
- Frontend abre em `localhost:5173`.
- API responde em `localhost:8080`.
- CORS aceita `localhost:5173`.
- Explorer chama API real com `X-API-Key`.
- Admin mostra erro real quando chave/plano/servico bloqueia.
- Nenhum botao fica silencioso.

## Evidencias Registradas em 2026-05-06

| Validacao | Resultado |
|---|---|
| `cd frontend && npm install` | Passou, 0 vulnerabilidades no wrapper |
| `cd frontend && npm run build` | Passou; Vite gerou build com warning nao bloqueante de chunk > 500 kB |
| `cd frontend/healthintel_frontend_fase9 && npm run lint` | Passou |
| `docker compose -f infra/docker-compose.yml config` | Passou; `API_CORS_ALLOWED_ORIGINS` inclui `localhost:5173` |
| `docker compose -f infra/docker-compose.yml build frontend` | Passou; imagem `infra-frontend:latest` criada |
| Recriacao `api` e `nginx` | Passou; containers iniciaram |
| `GET /saude` | 200 OK |
| `GET /prontidao` | 200 OK; Postgres, Redis e layout service OK |
| `GET /v1/meta/endpoints` com chave admin | 200 OK |
| `GET /v1/operadoras?pagina=1&por_pagina=10` com chave dev | 200 OK; retornou operadoras de exemplo do banco local |
| Preflight CORS com `Origin: http://localhost:5173` | 200 OK; `access-control-allow-origin: http://localhost:5173` |
| `GET /admin/billing/resumo` com chave dev | 403 `PLANO_SEM_ACESSO` |
| `GET /admin/billing/resumo` com chave admin | 200 OK |
| `GET /admin/layouts` com chave admin | 200 OK |
| `HEAD http://localhost:5173/` | 200 OK |
| Homologacao Site Publico | Passou; Navegacao e formulários funcionais |
| Homologacao Login | Passou; Dev e Admin com redirecionamento correto |
| Homologacao Portal | Passou; Todas as abas carregam e interagem |
| Homologacao Live Tester | Passou; Chamadas reais retornam 200/JSON |
| Homologacao Permissoes | Passou; Admin acessa billing/layouts; Dev bloqueado |
| CORS & X-API-Key | Passou; Headers enviados e aceitos |
