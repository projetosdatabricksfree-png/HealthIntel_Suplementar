# HealthIntel Core ANS — Frontend Fase 9

Frontend comercial e portal do cliente para o produto **HealthIntel Core ANS**.

## Objetivo

Criar a camada visual para vender e operar o DaaS/API:

- site público comercial;
- página de planos;
- documentação de endpoints;
- login/portal do cliente;
- dashboard de uso;
- catálogo de endpoints;
- live tester da API;
- gestão de API keys;
- perfil, segurança, billing e equipe;
- páginas administrativas preparadas para billing/layout.

## Stack

- React 19
- TypeScript
- Vite
- CSS puro com design system próprio
- React Router
- Lucide Icons
- Recharts

## Executar localmente

```bash
cd frontend/healthintel_frontend_fase9
cp .env.example .env
npm install
npm run dev
```

Acesse:

```text
http://localhost:5173
```

## Integração com a API

Configure:

```bash
VITE_API_BASE_URL=http://localhost:8080
```

A API atual do projeto usa o header:

```http
X-API-Key: sua_chave
```

No portal, a chave é armazenada apenas no `localStorage` do navegador para demo controlada e homologação. Em produção, a recomendação é trocar o login local por autenticação real com sessão segura HttpOnly, CRUD de usuários, emissão/rotação/revogação de chaves e auditoria.

## Rotas principais

### Público

- `/`
- `/produto`
- `/precos`
- `/documentacao`
- `/seguranca`
- `/contato`
- `/login`

### Portal

- `/app`
- `/app/endpoints`
- `/app/explorer`
- `/app/api-keys`
- `/app/uso`
- `/app/datasets`
- `/app/billing`
- `/app/equipe`
- `/app/perfil`
- `/app/seguranca`

### Admin

- `/app/admin/billing`
- `/app/admin/layouts`

## Observações

Este frontend está pronto para acoplar no repositório como pasta `frontend/`.

A API do projeto já possui autenticação por API key, rate limit, billing admin e endpoints Core. Porém, o backend ainda não possui endpoints completos de autenticação de usuário do portal, gestão de times e emissão de chaves pelo próprio cliente. Por isso, essas telas foram implementadas como portal-ready, com estrutura visual e serviços preparados para posterior integração.
