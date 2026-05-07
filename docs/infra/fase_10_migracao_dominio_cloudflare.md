# Fase 10 - Migracao futura para dominio e Cloudflare

## Objetivo

Migrar a homologacao por IP para URLs com dominio e HTTPS depois que `healthintel.com.br` estiver propagado e configurado no Cloudflare.

URLs futuras:

- Frontend: `https://app.healthintel.com.br`
- API: `https://api.healthintel.com.br`

## DNS previsto

No Cloudflare:

| Nome | Tipo | Destino | Proxy |
|---|---|---|---|
| `app.healthintel.com.br` | `A` | `5.189.160.27` | Ativo apos validar HTTPS |
| `api.healthintel.com.br` | `A` | `5.189.160.27` | Ativo apos validar HTTPS |

Durante a primeira virada, pode ser mais seguro iniciar com proxy desativado, validar origem e depois ativar Cloudflare.

## Mudancas de ambiente

Trocar no `.env.hml`:

```env
FRONTEND_PUBLIC_URL=https://app.healthintel.com.br
API_PUBLIC_URL=https://api.healthintel.com.br
API_ALLOWED_HOSTS=localhost,127.0.0.1,5.189.160.27,api,healthintel_api,app.healthintel.com.br,api.healthintel.com.br
API_CORS_ALLOWED_ORIGINS=https://app.healthintel.com.br,https://api.healthintel.com.br
VITE_API_BASE_URL=https://api.healthintel.com.br
```

Gerar novamente o build do frontend apos trocar `VITE_API_BASE_URL`.

## Proxy HTTPS

Opcoes recomendadas:

- Caddy com HTTPS automatico.
- Nginx com Certbot/Let's Encrypt.
- Cloudflare Tunnel, se a decisao for nao expor portas diretamente.

Em qualquer opcao, a API deve passar a responder via `443` e a porta `8080` deve deixar de ser publica.

## Fechamento da porta 8080

Depois de validar `https://api.healthintel.com.br`:

```bash
sudo ufw delete allow 8080/tcp
sudo ufw status verbose
```

Tambem ajustar o compose para prender a API temporaria em loopback ou remover publicacao direta:

```env
API_EXTERNAL_PORT=127.0.0.1:8080
```

## CORS final

O CORS final nao deve manter IP publico como origem permanente, exceto se houver uma razao operacional documentada.

Origem esperada:

```env
API_CORS_ALLOWED_ORIGINS=https://app.healthintel.com.br
```

## Ordem segura de migracao

1. Homologar por IP.
2. Configurar DNS `app` e `api`.
3. Subir proxy HTTPS.
4. Rebuildar frontend com `VITE_API_BASE_URL=https://api.healthintel.com.br`.
5. Recriar frontend/API/nginx.
6. Validar frontend, API, API key e CORS.
7. Fechar porta `8080`.
8. Atualizar documentacao de URLs.

## Checks pos-migracao

```bash
curl -i https://api.healthintel.com.br/saude
curl -i https://api.healthintel.com.br/prontidao
curl -i https://api.healthintel.com.br/v1/meta/endpoints \
  -H "X-API-Key: hi_local_admin_2026_api_key"
curl -i -X OPTIONS https://api.healthintel.com.br/v1/meta/endpoints \
  -H "Origin: https://app.healthintel.com.br" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: X-API-Key"
```

## Riscos

- DNS pode levar tempo para propagar.
- Cloudflare com proxy ativo pode mascarar erro de origem; validar com proxy desativado antes ajuda.
- Se o frontend for buildado ainda apontando para IP, o navegador continuara chamando `http://5.189.160.27:8080`.
- Manter `8080` aberto apos HTTPS aumenta superficie de ataque.
