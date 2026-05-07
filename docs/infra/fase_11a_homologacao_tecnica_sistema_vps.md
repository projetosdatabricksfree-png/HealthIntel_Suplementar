# Fase 11A - Homologacao tecnica por dominio HTTP na VPS

## Objetivo

Validar a transicao da homologacao por IP para homologacao por dominio HTTP, mantendo a API publica temporariamente em `:8080` e o frontend em `http://app.healthintel.com.br`.

## Problema encontrado

- `curl -i http://api.healthintel.com.br:8080/saude` retornava `HTTP/1.1 400 Bad Request`.
- O corpo da resposta era `Invalid host header`.

## Causa

O `TrustedHostMiddleware` da API estava correto no codigo, mas o container em execucao ainda recebia um `.env.hml` antigo:

- `API_ALLOWED_HOSTS` continha apenas `localhost`, `127.0.0.1`, `5.189.160.27`, `api` e `healthintel_api`.
- `API_CORS_ALLOWED_ORIGINS` continha apenas origens por IP e localhost.

Com isso, qualquer requisicao com `Host: api.healthintel.com.br` era rejeitada antes do roteamento.

## Correcao aplicada na VPS

No arquivo **nao versionado** `/opt/healthintel/.env.hml`:

```env
FRONTEND_PUBLIC_URL=http://app.healthintel.com.br
API_PUBLIC_URL=http://api.healthintel.com.br:8080
API_ALLOWED_HOSTS=localhost,127.0.0.1,5.189.160.27,app.healthintel.com.br,api.healthintel.com.br,api,healthintel_api
API_CORS_ALLOWED_ORIGINS=http://app.healthintel.com.br,http://api.healthintel.com.br:8080,http://5.189.160.27,http://5.189.160.27:8080,http://localhost:5173,http://127.0.0.1:5173
```

Depois disso:

```bash
docker compose --env-file .env.hml \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.hml.yml \
  up -d --build api nginx
```

## Frontend

O build do frontend passou a ser preparado para ler `API_PUBLIC_URL` no script [deploy_hml_ip.sh](/home/diegocosta/Documents/PROJETO/HealthIntel_Suplementar/scripts/vps/deploy_hml_ip.sh).

Na VPS, o arquivo usado para build e:

```env
VITE_API_BASE_URL=http://api.healthintel.com.br:8080
VITE_ENABLE_DEMO_FALLBACK=false
VITE_APP_NAME=HealthIntel Core ANS
```

## Testes executados

### Health e prontidao

```bash
curl -i http://127.0.0.1:8080/saude
curl -i http://127.0.0.1:8080/saude -H "Host: api.healthintel.com.br"
curl -i http://api.healthintel.com.br:8080/saude
curl -i http://api.healthintel.com.br:8080/prontidao
```

Resultado esperado e obtido:

- `/saude`: `200`
- `/prontidao`: `200`
- sem `Invalid host header`

### CORS por dominio

```bash
curl -i -X OPTIONS "http://api.healthintel.com.br:8080/v1/operadoras?pagina=1&por_pagina=10" \
  -H "Origin: http://app.healthintel.com.br" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: X-API-Key"
```

Resultado esperado e obtido:

- status `200`/`204`
- `access-control-allow-origin: http://app.healthintel.com.br`
- `access-control-allow-headers` incluindo `X-API-Key`

### Endpoints protegidos

Validacao com chaves HML nao versionadas:

- `/v1/meta/endpoints` com chave admin: `200`
- `/v1/operadoras` com chave dev: `200`
- `/admin/billing/resumo` com chave dev: `403`
- `/admin/billing/resumo` com chave admin: `200` ou erro real nao relacionado a autenticacao

## Pendencias

- Esta fase continua em HTTP de homologacao. Nao e producao.
- A porta `8080` segue publica ate a migracao para HTTPS/proxy dedicado.
- O proximo passo e fechar a etapa de HTTPS/Caddy ou Nginx TLS, mover a API para `https://api.healthintel.com.br` e remover exposicao publica de `:8080`.

## Proxima etapa

A migracao para HTTPS com Caddy fica formalizada em [fase_11b_https_caddy_dominio_vps.md](/home/diegocosta/Documents/PROJETO/HealthIntel_Suplementar/docs/infra/fase_11b_https_caddy_dominio_vps.md). Nessa transicao:

- `FRONTEND_EXTERNAL_PORT` passa para `127.0.0.1:3000`
- `API_EXTERNAL_PORT` passa para `127.0.0.1:8080`
- `Caddy` assume a exposicao publica em `80/443`
- `API_CORS_ALLOWED_ORIGINS` passa a aceitar `https://app.healthintel.com.br`
- `VITE_API_BASE_URL` passa a ser `https://api.healthintel.com.br`
- `8080/tcp` e removida do firewall depois da validacao TLS
