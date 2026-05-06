# Fase 9 - Frontend Comercial e Portal do Cliente

## Objetivo

Transformar o HealthIntel Core ANS em uma experiencia comercial demonstravel: site publico, portal do cliente, documentacao de API, live tester, gestao local de API key, uso, billing, datasets e seguranca.

Esta fase prepara demo comercial e piloto controlado. Ela nao substitui autenticacao, billing, emissao de chaves e governanca de usuarios reais no backend.

## Escopo do Frontend

O frontend esta em:

```text
frontend/healthintel_frontend_fase9
```

Superficies implementadas:

- Site publico do HealthIntel Core ANS.
- Portal autenticado localmente por e-mail + API key.
- Catalogo de endpoints classificado por `core`, `premium`, `admin`, `interno` e `bloqueado_mvp`.
- Live tester limitado aos endpoints `core`.
- Telas de API keys, uso, billing, datasets, equipe, perfil e seguranca em modo portal-ready.

## Rotas Publicas

```text
/
/produto
/precos
/documentacao
/seguranca
/contato
/login
```

A documentacao publica mostra apenas endpoints `core` do HealthIntel Core ANS. Endpoints TISS, CNES completo, Bronze, Prata, Premium e Admin nao sao vendidos no fluxo publico do MVP.

## Rotas do Portal

```text
/app
/app/endpoints
/app/explorer
/app/api-keys
/app/uso
/app/datasets
/app/billing
/app/equipe
/app/perfil
/app/seguranca
/app/admin/billing
/app/admin/layouts
```

As rotas `/app/*` exigem login local no frontend. O login atual salva e-mail e API key no `localStorage`, aceitavel para homologacao e demo controlada.

## Variaveis de Ambiente

Arquivo:

```text
frontend/healthintel_frontend_fase9/.env.example
```

Variaveis:

```env
VITE_API_BASE_URL=http://localhost:8080
VITE_ENABLE_DEMO_FALLBACK=true
VITE_APP_NAME=HealthIntel Core ANS
```

Regras:

- `VITE_API_BASE_URL` aponta para o Nginx da API local.
- `VITE_ENABLE_DEMO_FALLBACK=true` so gera fallback demo em modo Vite de desenvolvimento/homologacao.
- Em build de producao, falha de rede retorna erro real mesmo que a variavel esteja `true`.
- Nenhuma chave real deve ser versionada.

## Como Rodar Local

```bash
cd frontend/healthintel_frontend_fase9
cp .env.example .env
npm install
npm run dev
```

URL:

```text
http://localhost:5173
```

API esperada:

```text
http://localhost:8080
```

Health checks:

```bash
curl http://localhost:8080/saude
curl http://localhost:8080/prontidao
```

## Como Rodar via Docker

O `infra/docker-compose.yml` possui o servico:

```yaml
frontend:
  build:
    context: ../frontend/healthintel_frontend_fase9
  container_name: healthintel_frontend
  ports:
    - "${FRONTEND_EXTERNAL_PORT:-5173}:80"
  depends_on:
    - nginx
  restart: unless-stopped
```

Comandos:

```bash
docker compose -f infra/docker-compose.yml config
docker compose -f infra/docker-compose.yml build frontend
docker compose -f infra/docker-compose.yml up -d nginx frontend
```

## Endpoints Core

Endpoints que podem aparecer no produto inicial:

```text
GET /saude
GET /prontidao
GET /v1/meta/dataset
GET /v1/meta/versao
GET /v1/meta/pipeline
GET /v1/meta/endpoints
GET /v1/operadoras
GET /v1/operadoras/{registro_ans}
GET /v1/operadoras/{registro_ans}/score
GET /v1/operadoras/{registro_ans}/score-v3
GET /v1/operadoras/{registro_ans}/score-v3/historico
GET /v1/operadoras/{registro_ans}/regulatorio
GET /v1/operadoras/{registro_ans}/score-regulatorio
GET /v1/operadoras/{registro_ans}/regime-especial
GET /v1/operadoras/{registro_ans}/portabilidade
GET /v1/regulatorio/rn623
GET /v1/operadoras/{registro_ans}/financeiro
GET /v1/operadoras/{registro_ans}/score-v2
GET /v1/mercado/municipio
GET /v1/mercado/vazio-assistencial
GET /v1/rankings/operadora/score
GET /v1/rankings/operadora/crescimento
GET /v1/rankings/municipio/oportunidade
GET /v1/rankings/municipio/oportunidade-v2
GET /v1/rankings/composto
GET /v1/rede/municipio/{cd_municipio}
```

## Endpoints Bloqueados no MVP

Nao vender no MVP publico:

```text
/v1/cnes/*
/v1/tiss/*
/v1/premium/*
/v1/bronze/*
/v1/prata/*
/admin/*
/raw
/export-full
/download-all
```

Motivos:

- TISS e CNES completo ainda aumentam custo operacional e risco de escopo.
- Bronze e Prata sao camadas internas.
- Premium e Admin nao fazem parte do fluxo publico do Core ANS.
- Exportacao full contraria a protecao comercial do produto.

## Integracao API

O live tester usa:

```http
X-API-Key: <chave>
```

Implementacao:

```text
frontend/healthintel_frontend_fase9/src/services/apiClient.ts
frontend/healthintel_frontend_fase9/src/pages/portal/ExplorerPage.tsx
```

Controles:

- Usa `VITE_API_BASE_URL`.
- Envia `X-API-Key` quando a chave existe no portal.
- Nao executa chamadas automaticas em massa.
- Limita `por_pagina` entre 1 e 100.
- Executa apenas endpoints `core`.
- Com `VITE_ENABLE_DEMO_FALLBACK=false`, erro de rede aparece como erro real.

## Pendencias Backend

Antes de producao publica, implementar:

- Autenticacao real.
- Sessao `HttpOnly` e `Secure`.
- CRUD de usuarios.
- Gestao real de API keys.
- Rotacao e revogacao de chaves.
- 2FA.
- Allowlist de IP/dominio.
- Auditoria real do portal.
- Billing por cliente.
- Endpoints reais de uso agregado.
- Emissao de chaves por plano.

## Checklist de Go-live

- [x] `npm install` executa sem vulnerabilidades conhecidas.
- [x] `npm run build` passa.
- [x] `.env.example` existe e nao contem segredo.
- [x] `Dockerfile` do frontend usa build Vite e Nginx.
- [x] `nginx.conf` serve SPA com fallback para `index.html`.
- [x] Compose possui servico `frontend`.
- [x] Site publico nao vende TISS, CNES completo, Bronze, Prata, Premium ou Admin como MVP.
- [x] Live tester monta chamadas com `X-API-Key`.
- [x] Catalogo de endpoints foi comparado com routers atuais da API.
- [ ] Backend possui autenticacao real de usuario do portal.
- [ ] Backend possui CRUD real de API keys.
- [ ] Backend possui billing self-service real.
- [ ] Smoke com API e banco populado validado em ambiente de piloto.

## Status

Pronto para demo comercial e piloto controlado do HealthIntel Core ANS.

Nao esta pronto para producao publica completa enquanto autenticacao, usuarios, API keys e billing reais nao forem implementados no backend.
