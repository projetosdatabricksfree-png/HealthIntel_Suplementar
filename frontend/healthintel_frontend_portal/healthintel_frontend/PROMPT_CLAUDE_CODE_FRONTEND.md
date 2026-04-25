# Prompt para aplicar no Claude Code / Codex

Você está no monorepo `HealthIntel_Suplementar`.

Objetivo: integrar a pasta `frontend/` como portal comercial e developer console do produto HealthIntel Suplementar.

Regras:
- Não alterar a lógica da API existente.
- Usar o mecanismo atual de autenticação por `X-API-Key`.
- Manter o frontend como aplicação Vite + React + TypeScript.
- Não transformar o produto em BI/dashboard analítico.
- O posicionamento deve ser DaaS/API B2B: landing page, planos, documentação, playground e console de API.

Tarefas:
1. Copiar a pasta `frontend/` para a raiz do monorepo.
2. Adicionar no `Makefile`:
   - `frontend-dev`: entra em `frontend`, instala dependências se necessário e sobe `npm run dev`.
   - `frontend-build`: entra em `frontend` e executa `npm run build`.
3. Validar:
   - `cd frontend && npm install`
   - `npm run build`
   - backend ligado em `http://localhost:8080`
   - frontend ligado em `http://localhost:5173`
4. Garantir que chamadas `/saude`, `/prontidao` e `/v1/*` funcionem via proxy do Vite.
5. Se configurar chamada direta por domínio absoluto, ajustar no backend:
   - `API_CORS_ALLOWED_ORIGINS` incluindo `http://localhost:5173`.
6. Não criar autenticação por e-mail/senha agora. O MVP usa API key.
7. Criar issue/backlog separado para autenticação SaaS real:
   - `POST /v1/auth/register`
   - `POST /v1/auth/login`
   - `GET /v1/portal/me`
   - `GET /v1/portal/usage`
   - `POST /v1/portal/api-keys`
   - `DELETE /v1/portal/api-keys/{id}`
