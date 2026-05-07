# Fase 11b - HTTPS com Caddy na VPS

## Objetivo

Subir a borda publica da homologacao tecnica com TLS em `app.healthintel.com.br` e `api.healthintel.com.br`, removendo a exposicao publica temporaria da porta `8080`.

## Estado anterior

- Frontend publico em `http://app.healthintel.com.br`
- API publica em `http://api.healthintel.com.br:8080`
- CORS liberado para `http://app.healthintel.com.br`
- Firewall com `22/tcp`, `80/tcp` e `8080/tcp` abertos

## Arquitetura HTTPS

- `Caddy` publica `80/443` no host
- `healthintel_frontend` fica acessivel somente em `127.0.0.1:3000`
- `healthintel_nginx` fica acessivel somente em `127.0.0.1:8080`
- `healthintel_layout_service`, `postgres`, `redis` e `mongo` continuam restritos a loopback

## Caddyfile

```caddyfile
app.healthintel.com.br {
    reverse_proxy 127.0.0.1:3000

    header {
        X-Frame-Options "DENY"
        X-Content-Type-Options "nosniff"
        Referrer-Policy "strict-origin-when-cross-origin"
        Permissions-Policy "geolocation=(), microphone=(), camera=()"
    }
}

api.healthintel.com.br {
    reverse_proxy 127.0.0.1:8080

    header {
        X-Frame-Options "DENY"
        X-Content-Type-Options "nosniff"
        Referrer-Policy "strict-origin-when-cross-origin"
        Permissions-Policy "geolocation=(), microphone=(), camera=()"
    }
}
```

## Variaveis alteradas

```env
FRONTEND_PUBLIC_URL=https://app.healthintel.com.br
API_PUBLIC_URL=https://api.healthintel.com.br
API_EXTERNAL_PORT=127.0.0.1:8080
FRONTEND_EXTERNAL_PORT=127.0.0.1:3000
LAYOUT_EXTERNAL_PORT=127.0.0.1:8081
API_ALLOWED_HOSTS=localhost,127.0.0.1,5.189.160.27,app.healthintel.com.br,api.healthintel.com.br,api,healthintel_api
API_CORS_ALLOWED_ORIGINS=https://app.healthintel.com.br,https://api.healthintel.com.br,http://app.healthintel.com.br,http://api.healthintel.com.br:8080,http://5.189.160.27,http://5.189.160.27:8080,http://localhost:5173,http://127.0.0.1:5173
VITE_API_BASE_URL=https://api.healthintel.com.br
```

## Portas antes e depois

- Antes:
  - publico `80/tcp`
  - publico `8080/tcp`
- Depois:
  - publico `80/tcp`
  - publico `443/tcp`
  - `8080/tcp` fechado publicamente
  - interno `127.0.0.1:8080` mantido

## Comandos de deploy

```bash
cd /opt/healthintel

docker compose \
  --env-file .env.hml \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.hml.yml \
  config

docker compose \
  --env-file .env.hml \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.hml.yml \
  up -d --build api nginx frontend
```

## Validacoes

```bash
curl -i https://app.healthintel.com.br
curl -i https://api.healthintel.com.br/saude
curl -i https://api.healthintel.com.br/prontidao
curl -i -X OPTIONS "https://api.healthintel.com.br/v1/operadoras?pagina=1&por_pagina=10" \
  -H "Origin: https://app.healthintel.com.br" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: X-API-Key"
```

## Bundle do frontend

O container `healthintel_frontend` precisa expor apenas `https://api.healthintel.com.br` nos assets buildados. O bundle nao pode manter `localhost:8080`, `127.0.0.1:8080`, `5.189.160.27:8080` ou `http://api.healthintel.com.br:8080`.

## Firewall

Depois da validacao TLS:

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw delete allow 8080/tcp
sudo ufw status verbose
```

## Rollback

1. Restaurar o backup de `/etc/caddy/Caddyfile` se necessario.
2. Reabrir `8080/tcp` se a borda TLS falhar: `sudo ufw allow 8080/tcp`.
3. Voltar `API_PUBLIC_URL` e `FRONTEND_PUBLIC_URL` para HTTP no `.env.hml`.
4. Rebuildar `api`, `nginx` e `frontend`.

## Pendencias

- O ambiente continua sendo homologacao tecnica, nao producao.
- A proxima etapa e homologar dados comerciais do Core, nao a plataforma.

## Veredito

Quando `app.healthintel.com.br` e `api.healthintel.com.br` responderem por HTTPS com CORS correto e `8080/tcp` estiver fechada publicamente, a borda tecnica da homologacao estara pronta para continuar a validacao de dados e endpoints Core.
