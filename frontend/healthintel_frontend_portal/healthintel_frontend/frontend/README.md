# HealthIntel Frontend

Frontend comercial e portal de desenvolvedor para o **HealthIntel Suplementar**.

## O que este frontend entrega

- Landing page B2B para vender a plataforma como **DaaS/API de dados ANS**.
- Página de planos baseada em camadas: Ouro, Prata e Bronze.
- Login funcional via `X-API-Key`, compatível com o backend atual.
- Portal do desenvolvedor com:
  - status da API (`/saude` e `/prontidao`);
  - chave de API mascarada;
  - catálogo de endpoints;
  - playground para testar endpoints com `X-API-Key`;
  - snippets `curl` e Python;
  - visão comercial de consumo, plano e upgrade.
- Página de documentação pública para facilitar integração.

## Como instalar dentro do monorepo

Copie a pasta `frontend/` para a raiz do repositório:

```bash
cd ~/Desktop/PROJETOS/healthIntel_suplementar
cp -r /caminho/para/frontend ./frontend
cd frontend
cp .env.example .env
npm install
npm run dev
```

Acesse:

```text
http://localhost:5173
```

Backend esperado:

```text
http://localhost:8080
```

## Configuração

Edite `.env`:

```env
# Em desenvolvimento, deixe vazio para usar o proxy do Vite para http://localhost:8080.
VITE_API_BASE_URL=
```

Se você preferir chamar a API diretamente por `http://localhost:8080`, ajuste também o backend:

```env
API_CORS_ALLOWED_ORIGINS=http://localhost:8080,http://127.0.0.1:8080,http://localhost:5173,http://127.0.0.1:5173
API_ALLOWED_HOSTS=localhost,127.0.0.1,testserver,api,healthintel_api
```

## Modelo de autenticação usado

O backend atual já usa `X-API-Key`. Por isso o login do MVP não usa e-mail/senha real; ele funciona como portal de desenvolvedor:

1. usuário informa e-mail/empresa para contexto local;
2. cola a API key emitida pelo backend/admin;
3. o portal salva a chave no `localStorage`;
4. todas as chamadas protegidas enviam o header:

```http
X-API-Key: SUA_CHAVE
```

Quando o backend tiver autenticação SaaS completa, o ideal é adicionar:

- `POST /v1/auth/register`
- `POST /v1/auth/login`
- `GET /v1/portal/me`
- `GET /v1/portal/usage`
- `POST /v1/portal/api-keys`
- `DELETE /v1/portal/api-keys/{id}`

## Build

```bash
npm run build
npm run preview
```

## Docker

```bash
docker build -t healthintel-frontend .
docker run --rm -p 3000:80 healthintel-frontend
```

## Integração recomendada com o Makefile

Na raiz do monorepo, adicione opcionalmente:

```makefile
frontend-dev:
	cd frontend && npm install && npm run dev

frontend-build:
	cd frontend && npm run build
```
