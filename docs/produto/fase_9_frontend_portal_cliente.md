# Fase 9 - Frontend Comercial e Portal do Cliente

## Objetivo

Deixar o HealthIntel Core ANS demonstravel e homologavel localmente: site publico, portal do cliente, documentacao de API, Live Tester, API key, uso, billing, datasets, equipe, perfil, seguranca e chamadas reais contra a API local.

Esta fase prepara demo comercial, homologacao local e piloto controlado. Ela nao substitui autenticacao, billing, emissao de chaves, 2FA e governanca real de usuarios no backend.

## Localizacao

O app Vite real esta em:

```text
frontend/healthintel_frontend_fase9
```

Tambem existe wrapper em:

```text
frontend/package.json
frontend/.env.example
```

Assim, os comandos podem ser executados a partir de `frontend/`.

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

O site publico vende apenas o HealthIntel Core ANS: operadoras, beneficiarios, mercado por municipio, rankings, score, financeiro, regulatorio, metadados de atualizacao e CNES agregado.

Nao entram no fluxo comercial publico: TISS analitico, analises avancadas de rede e cobertura, endpoints internos, areas admin, dados tecnicos de engenharia, exportacao integral e pacotes sob contrato.

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

As rotas `/app/*` exigem login local no frontend. O login salva e-mail e API key em `localStorage`, aceitavel apenas para homologacao e piloto controlado.

## Variaveis

Frontend:

```env
VITE_API_BASE_URL=http://localhost:8080
VITE_ENABLE_DEMO_FALLBACK=false
VITE_APP_NAME=HealthIntel Core ANS
```

API local:

```env
API_CORS_ALLOWED_ORIGINS=http://localhost:8080,http://127.0.0.1:8080,http://localhost:5173,http://127.0.0.1:5173
```

Chaves locais de smoke:

```text
hi_local_dev_2026_api_key
hi_local_admin_2026_api_key
```

Nenhuma chave real deve ser versionada.

## Como Rodar Local

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

URLs:

```text
Frontend: http://localhost:5173
API:      http://localhost:8080
```

Build:

```bash
cd frontend
npm run build
```

## Docker

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

Validacao:

```bash
docker compose -f infra/docker-compose.yml config
docker compose -f infra/docker-compose.yml build frontend
docker compose -f infra/docker-compose.yml up -d nginx frontend
```

Se CORS falhar no navegador, recriar a API para aplicar `API_CORS_ALLOWED_ORIGINS`:

```bash
docker compose -f infra/docker-compose.yml up -d --force-recreate api nginx
```

## Endpoints Core Publicaveis

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
GET /v1/operadoras/{registro_ans}/regulatorio
GET /v1/operadoras/{registro_ans}/financeiro
GET /v1/operadoras/{registro_ans}/score-v2
GET /v1/operadoras/{registro_ans}/score-v3
GET /v1/operadoras/{registro_ans}/score-v3/historico
GET /v1/operadoras/{registro_ans}/score-regulatorio
GET /v1/operadoras/{registro_ans}/regime-especial
GET /v1/operadoras/{registro_ans}/portabilidade
GET /v1/mercado/municipio
GET /v1/mercado/vazio-assistencial
GET /v1/rankings/operadora/score
GET /v1/rankings/operadora/crescimento
GET /v1/rankings/municipio/oportunidade
GET /v1/rankings/municipio/oportunidade-v2
GET /v1/rankings/composto
GET /v1/rede/municipio/{cd_municipio}
GET /v1/cnes/municipio/{cd_municipio}
GET /v1/cnes/uf/{sg_uf}
GET /v1/regulatorio/rn623
```

## Recursos Sob Contrato ou Internos

Nao vender no fluxo publico padrao:

```text
/v1/tiss/*
/v1/premium/*
/admin/*
/v1/bronze/*
/v1/prata/*
```

No portal, estes itens podem aparecer com rotulo de admin, interno ou sob demanda, sem induzir que fazem parte do Core publico.

## Comportamento Implementado

- Todos os botoes principais possuem acao real: navegacao, API, modal, toast, localStorage, copia ou exportacao local.
- Contato valida campos, salva lead local e registra auditoria.
- Login valida e-mail/API key e registra auditoria local.
- Logout limpa sessao e API key.
- API Keys salva, limpa, testa `/v1/meta/endpoints`, copia chave mascarada e mostra exemplo cURL.
- Endpoints navegam para `/app/explorer?endpoint=<id>`.
- Explorer usa API real, envia `X-API-Key`, mostra URL, metodo, headers mascarados, status, tempo, JSON, erro real e cURL.
- Uso possui filtros e exportacao local demonstrativa ate existir endpoint agregado real.
- Billing, equipe, perfil e seguranca persistem localmente e registram auditoria.
- Admin Billing e Admin Layouts chamam endpoints reais e exibem erro real.

## Pendencias para Producao Publica

- Autenticacao real.
- Sessao `HttpOnly` e `Secure`.
- CRUD de usuarios.
- Papeis e permissoes reais.
- 2FA real.
- Gestao, emissao, rotacao e revogacao de API keys.
- Allowlist de IP/dominio no backend.
- Auditoria real do portal.
- Billing por cliente.
- Endpoint real de uso agregado.
- Deploy com HTTPS, dominio e secrets fora do repositorio.

## Status

Pronto para homologacao local e demo comercial controlada quando:

- `npm run build` passar.
- API responder em `localhost:8080`.
- CORS liberar `localhost:5173`.
- Smoke manual de `docs/produto/fase_9_homologacao_frontend_api.md` for concluido.

Nao declarar pronto para producao publica enquanto as pendencias de autenticacao, billing, usuarios e API keys reais nao forem implementadas no backend.
