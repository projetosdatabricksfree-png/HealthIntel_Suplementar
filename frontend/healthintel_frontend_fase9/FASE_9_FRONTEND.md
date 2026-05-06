# Fase 9 — Frontend Comercial + Portal do Cliente

## Objetivo

Implementar o frontend completo do HealthIntel Core ANS com duas superfícies:

1. **Site público comercial**, inspirado na lógica de produtos API-first: produto, documentação, preços, segurança e contato.
2. **Portal autenticado do cliente**, com dashboard, endpoints, live tester, API keys, uso, datasets, billing, equipe, perfil e segurança.

## Decisão de Produto

O frontend não deve vender “ANS completa”.  
O frontend deve vender **HealthIntel Core ANS**:

- operadoras;
- beneficiários;
- mercado por município;
- rankings;
- score;
- financeiro;
- regulatório;
- metadados;
- CNES agregado.

Fora do fluxo publico padrao:

- TISS;
- analises avancadas de rede e cobertura;
- areas administrativas;
- pacotes sob contrato;
- exportacao integral.

## Paleta Visual

A identidade usa azul claro, branco e ciano, com aparência de saúde suplementar, tecnologia médica e dados confiáveis.

Tokens principais:

```css
--color-primary: #0878c9;
--color-primary-dark: #075ea2;
--color-primary-soft: #dff3ff;
--color-secondary: #00a7c8;
--color-bg: #f5fbff;
--color-surface: #ffffff;
```

## Integração com API

A API atual usa:

```http
X-API-Key: sua_chave
```

O frontend possui `requestApi` centralizado em:

```text
src/services/apiClient.ts
```

Configuração:

```bash
VITE_API_BASE_URL=http://localhost:8080
VITE_ENABLE_DEMO_FALLBACK=false
VITE_APP_NAME=HealthIntel Core ANS
```

## Rotas do Site Público

```text
/
 /produto
 /precos
 /documentacao
 /seguranca
 /contato
 /login
```

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

## Endpoints Mapeados

O catálogo está em:

```text
src/data/endpoints.ts
```

Ele inclui endpoints reais do backend atual:

- `/saude`
- `/prontidao`
- `/v1/meta/*`
- `/v1/operadoras/*`
- `/v1/mercado/*`
- `/v1/rankings/*`
- `/v1/regulatorio/*`
- `/v1/rede/*`
- `/v1/cnes/*`
- `/v1/tiss/*`
- `/v1/premium/*`
- `/admin/billing/*`
- `/admin/layouts/*`

Cada endpoint é classificado como:

```text
core
premium
admin
interno
sob_demanda
```

## Segurança Implementada no Frontend

- Nginx com headers básicos de segurança.
- Portal com rotas protegidas no frontend.
- API key salva localmente apenas para desenvolvimento/homologação.
- Tela de allowlist de domínio/IP preparada.
- Tela de auditoria preparada.
- Sem exportacao integral no fluxo comercial.
- Datasets bloqueados sinalizados visualmente.

## Pendências Backend Recomendadas

Para produção, implementar no backend:

- autenticação real do portal;
- sessão HttpOnly/Secure;
- CRUD de usuários do cliente;
- CRUD de API keys;
- rotação/revogação de API key;
- whitelist de IP/domínio;
- dashboard real de billing por cliente;
- endpoint de uso agregado por cliente;
- endpoint de auditoria;
- endpoint de plano atual.

## Como Rodar

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

## Integração no Repositório

O frontend já está versionado em:

```text
HealthIntel_Suplementar/frontend/healthintel_frontend_fase9
```

O `infra/docker-compose.yml` possui o serviço:

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

Em produção, o ideal é servir o frontend via Nginx/Cloudflare e deixar a API em subdomínio separado:

```text
app.healthintel.com.br
api.healthintel.com.br
```
