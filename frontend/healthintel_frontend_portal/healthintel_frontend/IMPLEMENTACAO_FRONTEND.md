# Implementação do frontend — HealthIntel Suplementar

Este pacote contém uma primeira versão funcional do frontend comercial/portal de desenvolvedor.

## Decisão de arquitetura

O backend atual já possui FastAPI com `X-API-Key`, rate limit, rotas protegidas e billing/admin. Por isso o frontend foi criado como **portal de desenvolvedor API-first**, não como dashboard analítico.

## Estrutura criada

```text
frontend/
  src/
    App.tsx
    styles.css
    data/catalog.ts
    lib/api.ts
  package.json
  vite.config.ts
  Dockerfile
  nginx.conf
  README.md
```

## Como encaixa na ideia do produto

- Landing page: vende a curadoria operacional dos dados públicos da ANS.
- Planos: Piloto, Essencial, Plus, Enterprise, Enterprise Técnico.
- Documentação: catálogo de endpoints, plano mínimo e exemplos de integração.
- Login: acesso por API key.
- Console: health check, playground, snippets, status e upgrade.

## Limitação assumida

O backend ainda não parece expor autenticação SaaS completa por usuário e senha. O portal usa `X-API-Key`, que é o mecanismo real do backend hoje.

Quando evoluir o backend, criar endpoints de portal:

```http
POST /v1/auth/register
POST /v1/auth/login
GET  /v1/portal/me
GET  /v1/portal/usage
POST /v1/portal/api-keys
DELETE /v1/portal/api-keys/{id}
```

## Instalação rápida

```bash
cd HealthIntel_Suplementar
cp -r frontend ./frontend
cd frontend
cp .env.example .env
npm install
npm run dev
```


## Observação de CORS

O backend atual define origens CORS por variável `API_CORS_ALLOWED_ORIGINS`. Para desenvolvimento com Vite em `http://localhost:5173`, há duas opções:

1. manter `VITE_API_BASE_URL=` vazio e deixar o proxy do Vite redirecionar para `http://localhost:8080`;
2. ou adicionar `http://localhost:5173` em `API_CORS_ALLOWED_ORIGINS`.
